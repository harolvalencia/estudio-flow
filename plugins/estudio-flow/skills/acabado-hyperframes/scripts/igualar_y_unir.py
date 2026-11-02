"""
Iguala el color, la nitidez y el volumen de los clips generados en Flow y los une en un
solo video.

Uso:
    python igualar_y_unir.py CARPETA [--salida final.mp4] [--modo auto|par|estadistico]

Toma los clips numerados de CARPETA (01.mp4, 02.mp4, ...) en orden. El primero es la
referencia de color. Cada clip siguiente se iguala a los anteriores ya corregidos:

  - "par": el clip empieza donde terminó el anterior (Extender, o Frames con el último
    fotograma). Se comparan esos dos fotogramas píxel a píxel y la corrección es exacta.
  - "estadistico": el clip es un plano nuevo (por ejemplo, Ingredients en Omni). Se
    igualan brillo, contraste y color en Lab contra el primer clip y los dos anteriores
    ya corregidos. Es aproximado: revisar el corte.

Deja en CARPETA/corregidos los clips corregidos (completos) y sus LUT .cube (sirven
también en CapCut, DaVinci o Premiere), y en CARPETA/final el video unido. Los
originales no se tocan. Solo necesita numpy y ffmpeg/ffprobe en el PATH.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ANCHO_MUESTRA, ALTO_MUESTRA = 640, 360
LUT_TAM = 33
UMBRAL_CONTINUIDAD = 0.95   # correlación mínima para considerar que un clip continúa al anterior
LUFS_OBJETIVO = -16.0
PICO_MAXIMO = -1.0          # dBTP
FUNDIDO_AUDIO = 0.01        # s, evita chasquidos en los cortes
CONVERSION_YUV_RGB = "scale=in_color_matrix=bt601:in_range=tv"
CONVERSION_RGB_YUV = "scale=out_color_matrix=bt601:out_range=tv"
ETIQUETAS_COLOR = ["-colorspace", "smpte170m", "-color_primaries", "bt709",
                   "-color_trc", "iec61966-2-1", "-color_range", "tv"]


def ejecutar(args, **kw):
    return subprocess.run(args, capture_output=True, check=True, **kw)


def sondear(ruta):
    out = ejecutar(["ffprobe", "-v", "error", "-count_packets", "-show_entries",
                    "stream=codec_type,width,height,r_frame_rate,nb_read_packets",
                    "-of", "json", str(ruta)], text=True).stdout
    flujos = json.loads(out)["streams"]
    v = next(s for s in flujos if s["codec_type"] == "video")
    num, den = map(int, v["r_frame_rate"].split("/"))
    return {"fps": num / den, "fotogramas": int(v["nb_read_packets"]),
            "ancho": int(v["width"]), "alto": int(v["height"]),
            "audio": any(s["codec_type"] == "audio" for s in flujos)}


def fotograma(ruta, indice, enfoque=0.0):
    """Un fotograma en RGB [0,1], convertido igual que lo hará lut3d al aplicar la LUT."""
    vf = (f"select=eq(n\\,{indice}),{filtro_enfoque(enfoque)}{CONVERSION_YUV_RGB}:w={ANCHO_MUESTRA}"
          f":h={ALTO_MUESTRA}:flags=area,format=rgb48le")
    crudo = ejecutar(["ffmpeg", "-v", "error", "-i", str(ruta), "-vf", vf, "-frames:v", "1",
                      "-f", "rawvideo", "-"]).stdout
    return (np.frombuffer(crudo, "<u2").reshape(ALTO_MUESTRA, ANCHO_MUESTRA, 3)
            .astype(np.float64) / 65535.0)


def muestras(ruta, cada=12):
    """Píxeles de un fotograma de cada `cada`, para las estadísticas de color."""
    vf = (f"select=not(mod(n\\,{cada})),{CONVERSION_YUV_RGB}:w=320:h=180:flags=area,"
          "format=rgb48le")
    crudo = ejecutar(["ffmpeg", "-v", "error", "-i", str(ruta), "-vf", vf, "-fps_mode", "passthrough",
                      "-f", "rawvideo", "-"]).stdout
    return np.frombuffer(crudo, "<u2").reshape(-1, 3).astype(np.float64) / 65535.0


def luma(img):
    return img @ np.array([0.299, 0.587, 0.114])


def correlacion(a, b):
    ya, yb = luma(a), luma(b)
    za = (ya - ya.mean()) / (ya.std() + 1e-9)
    zb = (yb - yb.mean()) / (yb.std() + 1e-9)
    return float((za * zb).mean())


def nitidez(img):
    """Varianza del laplaciano de la luma: baja cuando la imagen se ve suave o lavada."""
    y = luma(img)
    lap = y[1:-1, :-2] + y[1:-1, 2:] + y[:-2, 1:-1] + y[2:, 1:-1] - 4 * y[1:-1, 1:-1]
    return float(lap.var() * 1e4)


def filtro_enfoque(cantidad):
    return f"unsharp=5:5:{cantidad:.3f}:5:5:0," if cantidad > 0 else ""


def calibrar_enfoque(ruta, corregir, objetivo, maximo=2.0):
    """Cantidad de unsharp para que el primer fotograma de `ruta` iguale la nitidez `objetivo`."""
    def medir(c):
        img = fotograma(ruta, 0, c)
        return nitidez(corregir(img.reshape(-1, 3)).reshape(img.shape))
    if medir(0) >= objetivo:
        return 0.0
    if medir(maximo) < objetivo:
        return maximo
    bajo, alto = 0.0, maximo
    for _ in range(7):
        medio = (bajo + alto) / 2
        bajo, alto = (medio, alto) if medir(medio) < objetivo else (bajo, medio)
    return round((bajo + alto) / 2, 3)


def promedio_por_zonas(img, lado=8):
    """Promedia bloques de lado x lado: deja el color y quita textura y bordes."""
    h, w = img.shape[0] // lado * lado, img.shape[1] // lado * lado
    return img[:h, :w].reshape(h // lado, lado, w // lado, lado, 3).mean((1, 3))


# --- Lab (sRGB D65), para el modo estadístico y para medir diferencias -------------------
_M = np.array([[0.4124564, 0.3575761, 0.1804375],
               [0.2126729, 0.7151522, 0.0721750],
               [0.0193339, 0.1191920, 0.9503041]])
_BLANCO = np.array([0.95047, 1.0, 1.08883])
_D = 6 / 29


def rgb_a_lab(rgb):
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    t = (lin @ _M.T) / _BLANCO
    f = np.where(t > _D ** 3, np.cbrt(t), t / (3 * _D ** 2) + 4 / 29)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], -1)


def lab_a_rgb(lab):
    fy = (lab[..., 0] + 16) / 116
    f = np.stack([fy + lab[..., 1] / 500, fy, fy - lab[..., 2] / 200], -1)
    t = np.where(f > _D, f ** 3, 3 * _D ** 2 * (f - 4 / 29)) * _BLANCO
    lin = np.clip(t @ np.linalg.inv(_M).T, 0, None)
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)


def delta_e(a, b):
    """Diferencia de color media entre dos imágenes (alto, ancho, 3), sin contar textura."""
    a, b = promedio_por_zonas(a), promedio_por_zonas(b)
    return float(np.linalg.norm(rgb_a_lab(a) - rgb_a_lab(b), axis=-1).mean())


# --- Correcciones ---------------------------------------------------------------------
def rasgos(x):
    r, g, b = x[:, 0], x[:, 1], x[:, 2]
    return np.stack([np.ones_like(r), r, g, b, r * r, g * g, b * b, r * g, r * b, g * b,
                     r ** 3, g ** 3, b ** 3, r * g * b, r * r * g, r * r * b, g * g * r,
                     g * g * b, b * b * r, b * b * g], 1)


def ajustar_par(origen, destino):
    """Polinomio de grado 3 que lleva los colores de `origen` a los de `destino`.

    Ajusta la diferencia con el original (ridge), así los colores que no salen en la
    muestra quedan casi sin tocar. Pondera para que los colores poco frecuentes cuenten
    tanto como el cielo o el piso, ignora bordes (desalineación de medio píxel) y
    altas luces quemadas, y descarta lo que se movió entre los dos fotogramas.
    """
    gy, gx = np.gradient(luma(destino))
    borde = np.hypot(gx, gy)
    util = (borde < np.percentile(borde, 70)) & (origen.max(-1) < 0.995) & (destino.max(-1) < 0.995)
    x, y = origen[util], destino[util]   # imágenes (alto, ancho, 3) -> píxeles útiles (n, 3)
    caja = np.clip((x * 16).astype(int), 0, 15)
    clave = caja[:, 0] * 256 + caja[:, 1] * 16 + caja[:, 2]
    peso = 1 / np.sqrt(np.bincount(clave, minlength=4096)[clave])
    X = rasgos(x)
    elegidos = np.ones(len(x), bool)
    for _ in range(2):
        w = np.sqrt(peso[elegidos])[:, None]
        A, B = X[elegidos] * w, (y - x)[elegidos] * w
        coef = np.linalg.solve(A.T @ A + 1e-4 * len(A) * np.eye(A.shape[1]), A.T @ B)
        error = np.abs(x + X @ coef - y).sum(1)
        elegidos = error < np.percentile(error, 95)
    return lambda c: np.clip(c + rasgos(c) @ coef, 0, 1)


def ajustar_estadistico(origen, referencia, fuerza=0.8):
    """Media y desviación de cada canal Lab de `origen` llevadas a las de `referencia`."""
    lo, lr = rgb_a_lab(origen), rgb_a_lab(referencia)
    mo, so, mr, sr = lo.mean(0), lo.std(0), lr.mean(0), lr.std(0)

    def corregir(c):
        lab = rgb_a_lab(c)
        return np.clip(lab_a_rgb(lab + fuerza * ((lab - mo) / so * sr + mr - lab)), 0, 1)
    return corregir


def identidad(c):
    return c


def escribir_cube(funcion, ruta, titulo):
    eje = np.linspace(0, 1, LUT_TAM)
    b, g, r = np.meshgrid(eje, eje, eje, indexing="ij")   # en .cube el rojo varía más rápido
    rejilla = np.stack([r.ravel(), g.ravel(), b.ravel()], 1)
    salida = funcion(rejilla)
    with open(ruta, "w", newline="\n") as f:
        f.write(f'TITLE "{titulo}"\nLUT_3D_SIZE {LUT_TAM}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
        f.writelines(f"{p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n" for p in salida)


def sonoridad(ruta):
    err = subprocess.run(["ffmpeg", "-v", "info", "-i", str(ruta), "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    resumen = err[err.rfind("Summary:"):]
    integrada = float(re.search(r"I:\s+(-?[\d.]+) LUFS", resumen).group(1))
    pico = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", resumen).group(1))
    return integrada, pico


def filtro_video(lut, enfoque):
    if lut is None:
        return f"{filtro_enfoque(enfoque)}{CONVERSION_RGB_YUV},format=yuv420p"
    return (f"{filtro_enfoque(enfoque)}{CONVERSION_YUV_RGB},format=rgb48le,"
            f"lut3d=file={lut}:interp=tetrahedral,{CONVERSION_RGB_YUV},format=yuv420p")


def exportar_fotograma(ruta, indice, lut, enfoque, destino, cwd):
    """PNG a resolución completa de un fotograma ya corregido (para el 'start frame' de Flow)."""
    vf = f"select=eq(n\\,{indice}),{filtro_enfoque(enfoque)}{CONVERSION_YUV_RGB},format=rgb48le"
    if lut:
        vf += f",lut3d=file={lut}:interp=tetrahedral"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ruta), "-vf", vf + ",format=rgb24",
                    "-frames:v", "1", str(destino)], check=True, cwd=cwd)


def codificar(entradas, filtro, mapas, destino, cwd):
    args = ["ffmpeg", "-v", "error", "-y"]
    for e in entradas:
        args += ["-i", str(e)]
    args += ["-filter_complex", filtro]
    for m in mapas:
        args += ["-map", m]
    args += ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
             *ETIQUETAS_COLOR, "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
             str(destino)]
    subprocess.run(args, check=True, cwd=cwd)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("carpeta", type=Path)
    p.add_argument("--salida", default="unido.mp4", help="nombre del video unido (en CARPETA/final)")
    p.add_argument("--modo", choices=["auto", "par", "estadistico"], default="auto")
    p.add_argument("--sin-enfoque", action="store_true", help="no igualar la nitidez, solo color y volumen")
    p.add_argument("--solo-inicio", action="store_true",
                   help="solo exportar el fotograma inicial del siguiente clip, sin codificar videos")
    a = p.parse_args()

    clips = sorted((c for c in a.carpeta.glob("*.mp4") if re.fullmatch(r"\d+", c.stem)),
                   key=lambda c: int(c.stem))
    if len(clips) < 2:
        sys.exit("Hacen falta al menos dos clips numerados (01.mp4, 02.mp4...).")
    dir_corr, dir_luts, dir_final = a.carpeta / "corregidos", a.carpeta / "corregidos" / "luts", a.carpeta / "final"
    for d in (dir_corr, dir_luts, dir_final):
        d.mkdir(parents=True, exist_ok=True)

    info = [sondear(c) for c in clips]
    ref = info[0]
    for c, i in zip(clips, info):
        if abs(i["ancho"] / i["alto"] - ref["ancho"] / ref["alto"]) > 0.01:
            sys.exit(f"{c.name} no tiene la misma proporción que {clips[0].name}; genéralo con el mismo formato.")
        if (i["ancho"], i["alto"], i["fps"]) != (ref["ancho"], ref["alto"], ref["fps"]):
            print(f"{c.name}: {i['ancho']}x{i['alto']} a {i['fps']:g} fps; se lleva a "
                  f"{ref['ancho']}x{ref['alto']} a {ref['fps']:g} fps al unir.")

    print(f"Referencia de color: {clips[0].name}")
    correcciones, luts, enfoques, salto = [identidad], [None], [0.0], [0]
    cache_muestras = {}

    def muestras_de(j):
        if j not in cache_muestras:
            cache_muestras[j] = muestras(clips[j])
        return cache_muestras[j]

    for i in range(1, len(clips)):
        crudo = fotograma(clips[i - 1], info[i - 1]["fotogramas"] - 1, enfoques[i - 1])
        anterior = correcciones[i - 1](crudo.reshape(-1, 3)).reshape(crudo.shape)
        primero = fotograma(clips[i], 0)
        corr = correlacion(anterior, primero)
        modo = a.modo if a.modo != "auto" else ("par" if corr >= UMBRAL_CONTINUIDAD else "estadistico")
        if modo == "par":
            f = ajustar_par(primero, anterior)
        else:
            # el 01 ancla el aspecto; los dos anteriores aportan encuadres parecidos
            previos = sorted({0, max(0, i - 2), i - 1})
            referencia = np.vstack([correcciones[j](muestras_de(j)) for j in previos])
            f = ajustar_estadistico(muestras_de(i), referencia)
        # Flow pierde detalle en cada extensión; solo se puede medir si el plano continúa
        enfoque = 0.0 if a.sin_enfoque or modo != "par" else calibrar_enfoque(clips[i], f, nitidez(anterior))
        correcciones.append(f)
        enfoques.append(enfoque)
        # si continúa al anterior, su primer fotograma repite el último del anterior
        salto.append(1 if corr >= UMBRAL_CONTINUIDAD else 0)
        lut = f"{clips[i].stem}.cube"
        escribir_cube(f, dir_luts / lut, f"Igualar {clips[i].name} a {clips[0].name}")
        luts.append(lut)
        corregido = f(fotograma(clips[i], 0, enfoque).reshape(-1, 3)).reshape(primero.shape)
        if modo == "par":
            print(f"{clips[i].name}: continuidad {corr:.3f}, modo par | color en el corte dE "
                  f"{delta_e(anterior, primero):.2f} -> {delta_e(anterior, corregido):.2f} | nitidez "
                  f"{nitidez(primero):.0f} -> {nitidez(corregido):.0f} (objetivo {nitidez(anterior):.0f}, "
                  f"enfoque {enfoque:.2f})")
        else:
            # entre planos distintos solo tiene sentido comparar el color medio del clip
            lab_ref = rgb_a_lab(referencia).mean(0)
            antes = np.linalg.norm(rgb_a_lab(muestras_de(i)).mean(0) - lab_ref)
            despues = np.linalg.norm(rgb_a_lab(f(muestras_de(i))).mean(0) - lab_ref)
            print(f"{clips[i].name}: plano nuevo (continuidad {corr:.3f}), modo estadistico | color "
                  f"medio frente a la referencia dE {antes:.2f} -> {despues:.2f} | nitidez "
                  f"{nitidez(primero):.0f}  <- corrección aproximada, revisa el corte")

    ultimo = len(clips) - 1
    siguiente = str(int(clips[ultimo].stem) + 1).zfill(len(clips[ultimo].stem))
    inicio = (dir_final / f"inicio_para_{siguiente}.png").resolve()
    exportar_fotograma(clips[ultimo].resolve(), info[ultimo]["fotogramas"] - 1, luts[ultimo],
                       enfoques[ultimo], inicio, cwd=dir_luts)
    print(f"Fotograma inicial para el clip {siguiente} (súbelo en Flow como 'start frame'): {inicio}")
    if a.solo_inicio:
        return

    ganancias = []
    for c in clips:
        integrada, pico = sonoridad(c) if info[clips.index(c)]["audio"] else (LUFS_OBJETIVO, -99)
        g = min(LUFS_OBJETIVO - integrada, PICO_MAXIMO - pico)
        ganancias.append(g)
        print(f"{c.name}: {integrada:.1f} LUFS, pico {pico:.1f} dBTP -> ganancia {g:+.1f} dB")

    print("Escribiendo clips corregidos...")
    for i, c in enumerate(clips):
        if luts[i] is None and enfoques[i] == 0:
            continue
        codificar([c.resolve()], f"[0:v]{filtro_video(luts[i], enfoques[i])}[v]", ["[v]", "0:a?"],
                  (dir_corr / c.name).resolve(), cwd=dir_luts)

    print("Uniendo...")
    partes, pares = [], []
    for i, c in enumerate(clips):
        ini, fin, fps = salto[i], info[i]["fotogramas"], info[i]["fps"]
        dur = (fin - ini) / fps
        normalizar = ""
        if (info[i]["ancho"], info[i]["alto"], fps) != (ref["ancho"], ref["alto"], ref["fps"]):
            normalizar = f",fps={ref['fps']:g},scale={ref['ancho']}:{ref['alto']}:flags=lanczos"
        partes.append(f"[{i}:v]trim=start_frame={ini}:end_frame={fin},setpts=PTS-STARTPTS,"
                      f"{filtro_video(luts[i], enfoques[i])}{normalizar}[v{i}]")
        if info[i]["audio"]:
            partes.append(f"[{i}:a]atrim=start={ini / fps:.6f}:end={fin / fps:.6f},asetpts=PTS-STARTPTS,"
                          f"aformat=sample_rates=48000:channel_layouts=stereo,volume={ganancias[i]:.2f}dB,"
                          f"apad=whole_dur={dur:.6f},afade=t=in:d={FUNDIDO_AUDIO},"
                          f"afade=t=out:st={dur - FUNDIDO_AUDIO:.6f}:d={FUNDIDO_AUDIO}[a{i}]")
        else:
            partes.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={dur:.6f}[a{i}]")
        pares.append(f"[v{i}][a{i}]")
    filtro = ";".join(partes) + f";{''.join(pares)}concat=n={len(clips)}:v=1:a=1[v][a]"
    destino = (dir_final / a.salida).resolve()
    codificar([c.resolve() for c in clips], filtro, ["[v]", "[a]"], destino, cwd=dir_luts)
    total = sum((info[i]["fotogramas"] - salto[i]) / info[i]["fps"] for i in range(len(clips)))
    print(f"Listo: {destino} ({total:.1f} s)")


if __name__ == "__main__":
    main()
