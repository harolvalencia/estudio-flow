"""Termina en segundos un clip de Flow con voz: logo, frase y llamado a la acción.

Uso:
    python pieza_rapida.py CLIP.mp4 --frase "Tu próxima gran idea empieza hoy" --accion "Agenda tu diagnóstico"
                           [--color "#19E3E6"] [--logo logo.png] [--salida 05-final/prueba-rapida.mp4]
                           [--sosten 1.5]

Es la ruta del modo rápido: no usa HyperFrames, Node ni Chrome, solo ffmpeg y Pillow. La frase
se ve durante todo el clip, el botón entra al final y el último cuadro se sostiene para leerlo.
Imprime en JSON lo entregado, medido sobre el archivo real.
"""
import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont

FUENTES = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
           "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
FONDO = (2, 4, 10)
BOTON_S = 3.0


def fuente(tamano):
    for ruta in FUENTES:
        if Path(ruta).exists():
            return ImageFont.truetype(ruta, tamano)
    sys.exit("No encontré una fuente en negrita en este equipo.")


def sondear(ruta):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-show_entries", "format=duration", "-of", "json", str(ruta)], capture_output=True, text=True)
    datos = json.loads(r.stdout)
    video = datos["streams"][0]
    return int(video["width"]), int(video["height"]), float(datos["format"]["duration"])


def partir(texto, letra, ancho):
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if letra.getlength(prueba) > ancho and actual:
            lineas.append(actual)
            actual = palabra
        else:
            actual = prueba
    return lineas + [actual]


def con_sombra(lienzo, dibujar, radio):
    sombra = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
    dibujar(ImageDraw.Draw(sombra), (0, 0, 0, 210))
    lienzo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(radio)))
    dibujar(ImageDraw.Draw(lienzo), None)


def capa_base(W, H, frase, color, logo, destino):
    """Velo inferior, logo y frase. En vertical respeta la zona libre de los botones de la red."""
    vertical = H > W
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    velo = Image.new("L", (1, H))
    inicio = int(H * (0.42 if vertical else 0.45))
    for y in range(H):
        velo.putpixel((0, y), min(225, int(max(0, y - inicio) / (H - inicio) * 330)))
    capa.paste(Image.new("RGBA", (W, H), (*FONDO, 255)), (0, 0), velo.resize((W, H)))
    margen = int(W * (0.07 if vertical else 0.05))
    if logo:
        marca = Image.open(logo).convert("RGBA")
        ancho = int(W * (0.3 if vertical else 0.16))
        marca = marca.resize((ancho, round(marca.height * ancho / marca.width)), Image.LANCZOS)
        capa.alpha_composite(marca, (margen, int(H * (0.09 if vertical else 0.06))))
    tamano = int(W * (0.075 if vertical else 0.046))
    letra = fuente(tamano)
    lineas = partir(frase, letra, W * (0.78 if vertical else 0.7))
    alto = int(tamano * 1.16)
    y0 = int(H * 0.53) if vertical else int(H * 0.72) - alto * len(lineas)

    def escribir(lapiz, tinta):
        for n, linea in enumerate(lineas):
            lapiz.text((margen, y0 + n * alto), linea, font=letra, fill=tinta or (255, 255, 255, 255))

    con_sombra(capa, escribir, max(4, tamano // 7))
    barra = int(W * 0.1)
    ImageDraw.Draw(capa).rounded_rectangle((margen, y0 - tamano // 2, margen + barra, y0 - tamano // 2 + max(5, tamano // 10)),
                                           radius=3, fill=color)
    capa.save(destino)
    return y0 + alto * len(lineas)


def capa_boton(W, H, accion, color, y, destino):
    vertical = H > W
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tamano = int(W * (0.05 if vertical else 0.03))
    letra = fuente(tamano)
    ancho_texto = letra.getlength(accion)
    relleno = int(tamano * 0.9)
    margen = int(W * (0.07 if vertical else 0.05))
    alto = int(tamano * 2.3)
    x1 = margen + ancho_texto + relleno * 2
    y += int(tamano * 0.7)
    brillo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(brillo).rounded_rectangle((margen, y, x1, y + alto), radius=alto // 3, fill=(*color[:3], 170))
    capa.alpha_composite(brillo.filter(ImageFilter.GaussianBlur(tamano)))
    lapiz = ImageDraw.Draw(capa)
    lapiz.rounded_rectangle((margen, y, x1, y + alto), radius=alto // 3, fill=color)
    luz = sum(c * p for c, p in zip(color[:3], (0.299, 0.587, 0.114)))
    tinta = (*FONDO, 255) if luz > 140 else (255, 255, 255, 255)
    lapiz.text((margen + relleno, y + alto / 2), accion, font=letra, fill=tinta, anchor="lm")
    capa.save(destino)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("clip", type=Path)
    p.add_argument("--frase", required=True)
    p.add_argument("--accion", required=True)
    p.add_argument("--color", default="#19E3E6")
    p.add_argument("--logo", type=Path)
    p.add_argument("--salida", type=Path, default=Path("05-final/prueba-rapida.mp4"))
    p.add_argument("--sosten", type=float, default=1.5, help="segundos que se sostiene el último cuadro")
    a = p.parse_args()
    if not a.clip.exists():
        sys.exit(f"No existe {a.clip}")
    inicio_reloj = time.time()
    W, H, dur = sondear(a.clip)
    W, H = W - W % 2, H - H % 2
    color = (*ImageColor.getrgb(a.color)[:3], 255)
    total = dur + a.sosten
    desde = max(0.5, total - BOTON_S)
    a.salida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        base, boton = Path(tmp) / "base.png", Path(tmp) / "boton.png"
        fin_texto = capa_base(W, H, a.frase, color, a.logo, base)
        capa_boton(W, H, a.accion, color, fin_texto, boton)
        filtro = (f"[0:v]scale={W}:{H},tpad=stop_mode=clone:stop_duration={a.sosten}[v0];"
                  f"[1:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1[b];[v0][b]overlay=0:0:shortest=0[v1];"
                  f"[2:v]format=rgba,fade=t=in:st={desde:.2f}:d=0.3:alpha=1[c];[v1][c]overlay=0:0,format=yuv420p[v];"
                  f"[0:a]apad=whole_dur={total:.3f},loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[a]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a.clip), "-loop", "1", "-t", f"{total:.3f}", "-i", str(base),
                        "-loop", "1", "-t", f"{total:.3f}", "-i", str(boton), "-filter_complex", filtro, "-map", "[v]", "-map", "[a]",
                        "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", str(a.salida)], check=True)
    _, _, final = sondear(a.salida)
    print(json.dumps({"archivo": str(a.salida), "resolucion": f"{W}x{H}", "duracion_s": round(final, 2),
                      "peso_mb": round(a.salida.stat().st_size / 1e6, 1), "segundos_de_proceso": round(time.time() - inicio_reloj, 1)},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
