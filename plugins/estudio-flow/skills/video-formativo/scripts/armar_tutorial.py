"""Arma el montaje de un tutorial en HyperFrames a partir de un guion y de la voz medida.

Uso:
    python armar_tutorial.py 04-montaje/tutorial.json --tiempos 04-montaje/tiempos.json

Deja en la carpeta de tutorial.json:
    index.html              composición completa, lista para `hyperframes check` y `render`
    assets/audio/banda.wav  música suave en apertura y cierre, barridos, clics y golpe final
    linea-de-tiempo.json    escenas y capítulos, para kit_formativo.py
    guion.txt               texto aprobado, para control_final.py --guion

La voz manda el tiempo: cada escena dura lo que duran sus tramos de narración. Cada marca se
sincroniza con la palabra que la nombra, así el botón se señala justo cuando se dice. La música
se mide y se calibra sola para quedar 14 dB bajo la voz.
El formato de tutorial.json está en references/plantilla-tutorial.md. Necesita Pillow.
"""
import argparse
import html
import json
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

from PIL import Image

from control_final import normalizar

LIENZOS = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080)}
ESCENARIOS = {"16:9": (64, 84, 1792, 876), "9:16": (36, 300, 1008, 1040), "1:1": (48, 110, 984, 800)}
TEXTOS = {"16:9": (112, 44, 34, 32), "9:16": (92, 42, 36, 32), "1:1": (84, 36, 32, 30)}
SOSTENER_S = 2.2
ZOOM_MAX_NITIDO = 1.7
MOVIMIENTO_MIN_S = 0.95
PARECIDO_PALABRA = 0.75
LUFS_VOZ = -18.0
MUSICA_BAJO_VOZ_DB = 14
CURSOR = '<path d="M4 3 L4 33 L12 25.5 L17.5 38 L24 35 L18.4 22.8 L29 22.8 Z" fill="#fff" stroke="#0b1422" stroke-width="2.4" stroke-linejoin="round"/>'
avisos = []


def marcar(texto):
    """*palabra* resalta en color de acento."""
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", html.escape(texto or ""))


def tamano_medio(ruta):
    if ruta.suffix.lower() in (".mp4", ".mov", ".webm", ".m4v"):
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", str(ruta)], capture_output=True, text=True)
        ancho, alto = r.stdout.strip().split(",")[:2]
        return int(ancho), int(alto)
    with Image.open(ruta) as i:
        return i.size


def duracion_medio(ruta):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def ajustar(ancho, alto, escenario):
    x, y, w, h = escenario
    k = min(w / ancho, h / alto)
    return x + (w - ancho * k) / 2, y + (h - alto * k) / 2, ancho * k, alto * k


def sonoridad(ruta, desde, hasta, volumen):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{desde:.2f}", "-to", f"{hasta:.2f}", "-i", str(ruta),
                          "-af", f"volume={volumen},ebur128", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return float(re.search(r"I:\s+(-?[\d.]+) LUFS", err[err.rfind("Summary:"):]).group(1))


def camara(px, py, zoom, W, foco_y, H, ventana):
    """Traslación que deja el punto en el centro sin mostrar vacío alrededor de la captura."""
    x0, y0, w, h = ventana
    def eje(p, centro, inicio, largo, lienzo):
        t = centro - zoom * p
        if largo * zoom <= lienzo:
            return (lienzo - largo * zoom) / 2 - zoom * inicio
        return min(-zoom * inicio, max(lienzo - largo * zoom - zoom * inicio, t))
    return eje(px, W / 2, x0, w, W), eje(py, foco_y, y0, h, H)


def momento(marca, escena, previo):
    """Segundo de la escena en que ocurre una marca."""
    if marca.get("palabra"):
        objetivo = normalizar(marca["palabra"].split()[0])
        for w in escena["palabras"]:
            if w["t"] >= previo and SequenceMatcher(None, normalizar(w["p"]), objetivo).ratio() >= PARECIDO_PALABRA:
                return w["t"]
        avisos.append(f'La voz no dijo «{marca["palabra"]}» en la escena {escena["n"]}: usé un tiempo aproximado')
    return marca.get("en", previo + 1.6)


def preparar_escenas(guion, tiempos, base):
    tramos = {t["n"]: t for t in tiempos["tramos"]}
    escenas = []
    for n, e in enumerate(guion["escenas"], 1):
        ids = e["tramos"] if isinstance(e["tramos"], list) else [e["tramos"]]
        faltan = [i for i in ids if i not in tramos]
        if faltan:
            sys.exit(f"La escena {n} pide los tramos {faltan}, que no existen en tiempos.json")
        inicio = tramos[ids[0]]["inicio"]
        palabras = [{"p": w["p"], "t": round(tramos[i]["inicio"] - inicio + w["t"], 3)} for i in ids for w in tramos[i]["palabras"]]
        escenas.append({**e, "n": n, "inicio": inicio, "dur": sum(tramos[i]["duracion"] for i in ids), "palabras": palabras,
                        "voz_desde": tramos[ids[0]]["desde"]})
    escenas[-1]["dur"] += SOSTENER_S
    return escenas


def medio_html(e, escena, base, ventana=False):
    """Video o imagen de la escena. Un video a cámara arranca donde arranca su voz para no perder los labios."""
    ruta = escena.get("video") or escena.get("imagen")
    if not ruta or not (base / ruta).exists():
        sys.exit(f"Escena {escena['n']}: falta el archivo {ruta}")
    if not escena.get("video"):
        return f'<img src="{ruta}" alt="" />'
    disponible = duracion_medio(base / ruta)
    if ventana:
        desde, hasta = escena.get("desde", 0), escena.get("hasta", disponible)
        velocidad = (hasta - desde) / escena["dur"]
        if not 0.5 <= velocidad <= 3:
            avisos.append(f"Escena {escena['n']}: la grabación va a {velocidad:.2f}×; ajusta el guion o el tramo grabado")
        return (f'<video id="{e}m" class="clip" src="{ruta}" muted playsinline data-start="{escena["inicio"]:.3f}" '
                f'data-duration="{escena["dur"]:.3f}" data-media-start="{desde:.3f}" data-playback-rate="{velocidad:.3f}" '
                f'data-track-index="3"></video>')
    desde = escena["voz_desde"] if escena.get("sincronizar") else 0
    dur = min(escena["dur"], disponible - desde)
    sosten = ""
    if dur < escena["dur"]:
        # La escena dura más que el clip: su último cuadro queda debajo para sostener la imagen
        final = Path(ruta).with_name(Path(ruta).stem + "-fin.jpg").as_posix()
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i", str(base / ruta), "-frames:v", "1", "-q:v", "2",
                        str(base / final)], check=True)
        sosten = f'<img src="{final}" alt="" />'
    return (f'{sosten}<video id="{e}m" class="clip" src="{ruta}" muted playsinline data-start="{escena["inicio"]:.3f}" '
            f'data-duration="{dur:.3f}" data-media-start="{desde:.3f}" data-track-index="3"></video>')


def escena_apertura(escena, tl, base, ctx):
    e, ini = f'e{escena["n"]}', escena["inicio"]
    items = "".join(f'<li id="{e}o{i}"><b></b><span>{marcar(o)}</span></li>' for i, o in enumerate(escena.get("objetivos", [])))
    tl.append(f'tl.fromTo("#{e}f", {{scale:1.02}}, {{scale:1.09, duration:{escena["dur"]:.2f}, ease:"none"}}, {ini:.3f});')
    if ini > 0:
        tl.append(f'tl.fromTo("#{e}t .linea > span", {{yPercent:104}}, {{yPercent:0, duration:.5, stagger:.1, ease:"power4.out"}}, {ini + .1:.3f});')
    for i in range(len(escena.get("objetivos", []))):
        t = ini + escena["dur"] * (0.35 + 0.5 * i / max(1, len(escena["objetivos"])))
        tl.append(f'tl.fromTo("#{e}o{i}", {{opacity:0, x:-30}}, {{opacity:1, x:0, duration:.4, ease:"power3.out"}}, {t:.3f});')
    lineas = "".join(f'<span class="linea"><span>{marcar(x)}</span></span>' for x in escena["titulo"].split("|"))
    return f'''<div class="fondo" id="{e}f">{medio_html(e, escena, base)}</div><div class="velo"></div>
        <div class="portada"><div class="etiqueta">{marcar(escena.get("etiqueta", ""))}</div><h1 id="{e}t">{lineas}</h1><ul class="objetivos">{items}</ul></div>'''


def escena_pantalla(escena, tl, base, ctx):
    e, ini, dur = f'e{escena["n"]}', escena["inicio"], escena["dur"]
    W, H, foco_y = ctx["W"], ctx["H"], ctx["foco_y"]
    ruta = escena.get("video") or escena.get("imagen")
    ancho, alto = tamano_medio(base / ruta)
    x0, y0, w, h = ventana = ajustar(ancho, alto, ctx["escenario"])
    capas, notas, previo = [], [], 0.25
    cursor = (x0 + w * 0.62, y0 + h * 0.74)
    zoom_previo = 1.0
    tl.append(f'tl.fromTo("#{e}d", {{scale:1}}, {{scale:1.018, duration:{dur:.2f}, ease:"none"}}, {ini:.3f});')
    tl.append(f'tl.set("#{e}k", {{x:{cursor[0]:.1f}, y:{cursor[1]:.1f}, scale:1}}, {ini:.3f});')
    tl.append(f'tl.set("#{e}c", {{x:0, y:0, scale:1}}, {ini:.3f});')
    tl.append(f'tl.fromTo("#{e}v", {{opacity:0, scale:.965}}, {{opacity:1, scale:1, duration:.5, ease:"power3.out"}}, {ini + .05:.3f});')
    for i, m in enumerate(escena.get("marcas", [])):
        t = max(momento(m, escena, previo), previo + MOVIMIENTO_MIN_S)
        px, py = x0 + w * m["x"], y0 + h * m["y"]
        zoom = m.get("zoom", 1.9)
        if zoom * w / ancho > ZOOM_MAX_NITIDO:
            avisos.append(f"Escena {escena['n']}: la captura mide {ancho}×{alto} y se amplía {zoom * w / ancho:.1f} veces; se verá borrosa, recaptura con más resolución")
        tx, ty = camara(px, py, zoom, W, foco_y, H, ventana)
        caja_w, caja_h = w * m.get("ancho", 0.1), h * m.get("alto", 0.1)
        radio = max(caja_w, caja_h) * 0.95
        inicio_mov = max(previo + 0.05, t - 0.75)
        a = ini + inicio_mov
        tl.append(f'tl.to("#{e}c", {{x:{tx:.1f}, y:{ty:.1f}, scale:{zoom}, duration:{t - inicio_mov:.2f}, ease:"power2.inOut"}}, {a:.3f});')
        tl.append(f'tl.to("#{e}k", {{x:{px:.1f}, y:{py:.1f}, scale:{1 / zoom:.3f}, duration:{t - inicio_mov:.2f}, ease:"power2.inOut"}}, {a:.3f});')
        capas.append(f'<div class="foco" id="{e}f{i}" style="left:{x0:.1f}px;top:{y0:.1f}px;width:{w:.1f}px;height:{h:.1f}px;'
                     f'-webkit-mask-image:radial-gradient(ellipse {radio * 1.35:.0f}px {radio:.0f}px at {px - x0:.0f}px {py - y0:.0f}px,transparent 55%,#000 100%);'
                     f'mask-image:radial-gradient(ellipse {radio * 1.35:.0f}px {radio:.0f}px at {px - x0:.0f}px {py - y0:.0f}px,transparent 55%,#000 100%)"></div>')
        capas.append(f'<div class="caja" id="{e}b{i}" style="left:{px - caja_w / 2:.1f}px;top:{py - caja_h / 2:.1f}px;width:{caja_w:.1f}px;height:{caja_h:.1f}px;border-width:{3.2 / zoom:.2f}px;border-radius:{12 / zoom:.1f}px"></div>')
        capas.append(f'<div class="pulso" id="{e}p{i}" style="left:{px:.1f}px;top:{py:.1f}px"></div>')
        tl.append(f'tl.to("#{e}f{i}", {{opacity:1, duration:.4, ease:"power2.out"}}, {ini + t - .35:.3f});')
        tl.append(f'tl.fromTo("#{e}b{i}", {{opacity:0, scale:1.14}}, {{opacity:1, scale:1, duration:.32, ease:"back.out(2)"}}, {ini + t - .2:.3f});')
        fin_marca = ini + dur
        if i + 1 < len(escena["marcas"]):
            fin_marca = ini + max(momento(escena["marcas"][i + 1], escena, t), t + MOVIMIENTO_MIN_S) - .8
            tl.append(f'tl.to("#{e}f{i}", {{opacity:0, duration:.3}}, {fin_marca:.3f});')
            tl.append(f'tl.to("#{e}b{i}", {{opacity:0, duration:.25}}, {fin_marca:.3f});')
        if m.get("clic", True):
            ctx["clics"].append(ini + t)
            tl.append(f'tl.to("#{e}k", {{scale:{0.8 / zoom:.3f}, duration:.08, ease:"power2.in"}}, {ini + t:.3f});')
            tl.append(f'tl.to("#{e}k", {{scale:{1 / zoom:.3f}, duration:.14, ease:"power2.out"}}, {ini + t + .08:.3f});')
            tl.append(f'tl.fromTo("#{e}p{i}", {{opacity:1, scale:{.3 / zoom:.3f}}}, {{opacity:0, scale:{1.5 / zoom:.3f}, duration:.6, ease:"power2.out"}}, {ini + t:.3f});')
        if m.get("nota"):
            sx, sy = zoom * px + tx, zoom * py + ty
            ancho_nota = len(m["nota"].replace("*", "")) * ctx["t_nota"] * 0.58 + 56
            mitad_w, mitad_h = zoom * caja_w / 2, zoom * max(caja_h, 60) / 2
            if sx + mitad_w + 34 + ancho_nota < W - 40:
                nx, ny, ax = sx + mitad_w + 34, sy - ctx["t_nota"] * 0.95, 0
            elif sx - mitad_w - 34 - ancho_nota > 40:
                nx, ny, ax = sx - mitad_w - 34, sy - ctx["t_nota"] * 0.95, -100
            else:
                nx, ax = min(max(sx, W * 0.17), W * 0.83), -50
                ny = sy - mitad_h - 96 if sy + mitad_h + 130 > H - 120 else sy + mitad_h + 28
            notas.append(f'<div class="nota" id="{e}n{i}" style="left:{nx:.0f}px;top:{ny:.0f}px">{marcar(m["nota"])}</div>')
            tl.append(f'tl.set("#{e}n{i}", {{xPercent:{ax}}}, {ini:.3f});')
            tl.append(f'tl.fromTo("#{e}n{i}", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:.34, ease:"power3.out"}}, {ini + t - .1:.3f});')
            if i + 1 < len(escena["marcas"]):
                tl.append(f'tl.to("#{e}n{i}", {{opacity:0, duration:.2}}, {fin_marca:.3f});')
        previo, zoom_previo = t, zoom
    numero = escena.get("paso")
    chip = ""
    if numero:
        chip = f'<div class="paso" id="{e}s"><b>{numero}</b><span><small>Paso {numero} de {ctx["pasos"]}</small>{marcar(escena.get("titulo", ""))}</span></div>'
        tl.append(f'tl.fromTo("#{e}s", {{opacity:0, x:-34}}, {{opacity:1, x:0, duration:.42, ease:"power3.out"}}, {ini + .1:.3f});')
    medio = medio_html(e, escena, base, ventana=True)
    return f'''<div class="deriva" id="{e}d"><div class="camara" id="{e}c">
          <div class="ventana" id="{e}v" style="left:{x0:.1f}px;top:{y0:.1f}px;width:{w:.1f}px;height:{h:.1f}px">{medio}</div>
          {"".join(capas)}
          <svg class="cursor" id="{e}k" viewBox="0 0 44 44">{CURSOR}</svg>
        </div></div>{"".join(notas)}{chip}'''


def escena_idea(escena, tl, base, ctx):
    e, ini = f'e{escena["n"]}', escena["inicio"]
    fondo = ""
    if escena.get("video") or escena.get("imagen"):
        fondo = f'<div class="fondo" id="{e}z">{medio_html(e, escena, base)}</div><div class="velo"></div>'
        tl.append(f'tl.fromTo("#{e}z", {{scale:1.02}}, {{scale:1.09, duration:{escena["dur"]:.2f}, ease:"none"}}, {ini:.3f});')
    tl.append(f'tl.fromTo("#{e}g", {{xPercent:-5, yPercent:-3, scale:1.06}}, {{xPercent:5, yPercent:3, scale:1.16, duration:{escena["dur"]:.2f}, ease:"none"}}, {ini:.3f});')
    tl.append(f'tl.fromTo("#{e}a", {{opacity:0, y:22}}, {{opacity:1, y:0, duration:.4, ease:"power3.out"}}, {ini + .1:.3f});')
    tl.append(f'tl.fromTo("#{e}t .linea > span", {{yPercent:104}}, {{yPercent:0, duration:.5, stagger:.1, ease:"power4.out"}}, {ini + .2:.3f});')
    tl.append(f'tl.fromTo("#{e}x", {{opacity:0, y:24}}, {{opacity:1, y:0, duration:.5, ease:"power3.out"}}, {ini + .7:.3f});')
    lineas = "".join(f'<span class="linea"><span>{marcar(x)}</span></span>' for x in escena["titulo"].split("|"))
    return f'''<div class="degradado" id="{e}g"></div>{fondo}<div class="tarjeta"><div class="etiqueta" id="{e}a">{marcar(escena.get("etiqueta", ""))}</div>
        <h2 id="{e}t">{lineas}</h2><p id="{e}x">{marcar(escena.get("texto", ""))}</p></div>'''


def escena_pregunta(escena, tl, base, ctx):
    e, ini, dur = f'e{escena["n"]}', escena["inicio"], escena["dur"]
    revela = momento({k: v for k, v in escena.get("revelar", {}).items()} or {"en": dur * 0.7}, escena, 0.5)
    opciones = ""
    for i, o in enumerate(escena["opciones"]):
        opciones += f'<div class="opcion" id="{e}o{i}"><b>{"ABCD"[i]}</b><span>{marcar(o)}</span></div>'
        tl.append(f'tl.fromTo("#{e}o{i}", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.4, ease:"power3.out"}}, {ini + .45 + i * .22:.3f});')
    tl.append(f'tl.fromTo("#{e}g", {{xPercent:-4, scale:1.08}}, {{xPercent:4, scale:1.16, duration:{dur:.2f}, ease:"none"}}, {ini:.3f});')
    tl.append(f'tl.fromTo("#{e}t", {{opacity:0, y:24}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {ini + .1:.3f});')
    correcta = escena["correcta"]
    tl.append(f'tl.to("#{e}o{correcta}", {{scale:1.04, background:"linear-gradient(95deg,{ctx["acento"]},{ctx["primario"]})", color:"#02131f", duration:.34, ease:"back.out(2)"}}, {ini + revela:.3f});')
    for i in range(len(escena["opciones"])):
        if i != correcta:
            tl.append(f'tl.to("#{e}o{i}", {{opacity:.34, duration:.3}}, {ini + revela:.3f});')
    ctx["clics"].append(ini + revela)
    return f'''<div class="degradado" id="{e}g"></div><div class="tarjeta"><div class="etiqueta">{marcar(escena.get("etiqueta", "Comprueba"))}</div>
        <h2 class="pregunta" id="{e}t">{marcar(escena["pregunta"])}</h2><div class="opciones">{opciones}</div></div>'''


def escena_cierre(escena, tl, base, ctx):
    e, ini, dur = f'e{escena["n"]}', escena["inicio"], escena["dur"]
    t = momento({"palabra": escena.get("palabra"), "en": dur * 0.45}, escena, 0.3)
    ctx["golpe"] = ini + t
    tl.append(f'tl.fromTo("#{e}f", {{scale:1.02}}, {{scale:1.1, duration:{dur:.2f}, ease:"none"}}, {ini:.3f});')
    tl.append(f'tl.fromTo("#{e}t .linea > span", {{yPercent:104}}, {{yPercent:0, duration:.55, stagger:.12, ease:"power4.out"}}, {ini + .15:.3f});')
    tl.append(f'tl.fromTo("#{e}h", {{opacity:0, scale:1.5}}, {{opacity:1, scale:1, duration:.2, ease:"power3.in"}}, {ini + t - .2:.3f});')
    tl.append(f'tl.to("#{e}h", {{opacity:0, duration:.7, ease:"power2.out"}}, {ini + t:.3f});')
    tl.append(f'tl.fromTo("#{e}b", {{opacity:0, y:46, scale:.9}}, {{opacity:1, y:0, scale:1, duration:.5, ease:"back.out(1.8)"}}, {ini + t:.3f});')
    tl.append(f'tl.fromTo("#{e}l", {{opacity:0, scale:1.2}}, {{opacity:1, scale:1, duration:.55, ease:"power4.out"}}, {ini + t + .2:.3f});')
    tl.append(f'tl.fromTo("#{e}x", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:.4, ease:"power2.out"}}, {ini + t + .45:.3f});')
    ctx["chispas"] = (ini + t, ini + dur)
    lineas = "".join(f'<span class="linea"><span>{marcar(x)}</span></span>' for x in escena["frase"].split("|"))
    return f'''<div class="fondo" id="{e}f">{medio_html(e, escena, base)}</div><div class="velo-final"></div><div id="chispas"></div>
        <div class="final"><img class="logo-final" id="{e}l" src="{ctx["logo"]}" alt="{html.escape(ctx["marca"])}" />
        <h1 id="{e}t">{lineas}</h1><div class="boton" id="{e}b">{marcar(escena.get("boton", ""))}</div><div class="pie" id="{e}x">{marcar(escena.get("texto", ""))}</div></div>
        <div class="luz-final" id="{e}h"></div>'''


TIPOS = {"apertura": escena_apertura, "pantalla": escena_pantalla, "idea": escena_idea,
         "pregunta": escena_pregunta, "cierre": escena_cierre}


def subtitulos_quemados(escenas, tl):
    """Solo para piezas verticales cortas: en horizontal los subtítulos van en una pista aparte."""
    grupos, salida = [], ""
    for escena in escenas:
        actual = []
        for w in escena["palabras"]:
            actual.append(w)
            if len(actual) == 6 or w["p"][-1:] in ".,;:?!":
                grupos.append((escena["inicio"] + actual[0]["t"], " ".join(x["p"] for x in actual)))
                actual = []
        if actual:
            grupos.append((escena["inicio"] + actual[0]["t"], " ".join(x["p"] for x in actual)))
    for i, (t, texto) in enumerate(grupos):
        salida += f'<div class="quemado" id="q{i}">{html.escape(texto)}</div>'
        tl.append(f'tl.set("#q{i}", {{opacity:1}}, {t:.3f});')
        if i + 1 < len(grupos):
            tl.append(f'tl.set("#q{i}", {{opacity:0}}, {grupos[i + 1][0]:.3f});')
    return salida


CSS = """
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: __W__px; height: __H__px; overflow: hidden; background: var(--fondo); }
      :root { --fondo: __FONDO__; --primario: __PRIMARIO__; --acento: __ACENTO__; --titulo: "__FTITULO__", sans-serif; --texto: "__FTEXTO__", sans-serif; }
      #root { position: relative; width: __W__px; height: __H__px; overflow: hidden; background: var(--fondo); color: #fff; font-family: var(--texto); }
      em { font-style: normal; color: var(--acento); }
      #luz { position: absolute; inset: 0; background: radial-gradient(62% 72% at 80% 10%, color-mix(in srgb, var(--primario) 30%, transparent), transparent 72%), radial-gradient(52% 62% at 8% 94%, color-mix(in srgb, var(--acento) 18%, transparent), transparent 72%); }
      .escena { position: absolute; inset: 0; overflow: hidden; opacity: 0; }
      .deriva, .camara, .fondo { position: absolute; inset: 0; }
      .deriva { transform-origin: 50% 46%; }
      .camara { transform-origin: 0 0; }
      .fondo img, .fondo video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      .velo { position: absolute; inset: 0; background: linear-gradient(100deg, rgba(2,4,10,.9) 0%, rgba(2,4,10,.66) 44%, rgba(2,4,10,.12) 78%), linear-gradient(0deg, rgba(2,4,10,.7) 0%, rgba(2,4,10,0) 40%); }
      .ventana { position: absolute; overflow: hidden; border-radius: 16px; background: #fff; box-shadow: 0 0 0 1px rgba(255,255,255,.16), 0 34px 100px rgba(0,0,0,.65), 0 0 110px color-mix(in srgb, var(--acento) 22%, transparent); }
      .ventana img, .ventana video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: fill; }
      .foco { position: absolute; opacity: 0; background: rgba(2,6,14,.6); border-radius: 16px; }
      .caja { position: absolute; opacity: 0; border-style: solid; border-color: var(--acento); box-shadow: 0 0 26px color-mix(in srgb, var(--acento) 75%, transparent), inset 0 0 14px color-mix(in srgb, var(--acento) 30%, transparent); }
      .pulso { position: absolute; width: 150px; height: 150px; margin: -75px 0 0 -75px; border-radius: 50%; border: 5px solid var(--acento); opacity: 0; }
      .cursor { position: absolute; left: 0; top: 0; width: 44px; height: 44px; transform-origin: 4px 3px; filter: drop-shadow(0 3px 7px rgba(0,0,0,.55)); }
      .nota { position: absolute; padding: 16px 26px; border-radius: 14px; background: #fff; color: #06121f; font-weight: 800; font-size: __TNOTA__px; white-space: nowrap; opacity: 0; box-shadow: 0 16px 48px rgba(0,0,0,.5); }
      .nota em { color: var(--primario); }
      .paso { position: absolute; left: 64px; bottom: 22px; display: flex; align-items: center; gap: 16px; padding: 8px 26px 8px 8px; border-radius: 44px; background: rgba(6,12,24,.9); box-shadow: 0 0 0 1px rgba(255,255,255,.12), 0 14px 40px rgba(0,0,0,.5); font-weight: 700; font-size: __TPASO__px; line-height: 1.1; }
      .paso b { display: grid; place-items: center; width: 58px; height: 58px; border-radius: 50%; background: linear-gradient(135deg, var(--acento), var(--primario)); color: #02131f; font-family: var(--titulo); font-size: 30px; }
      .paso small { display: block; font-size: 28px; font-weight: 600; letter-spacing: .02em; color: var(--acento); }
      .etiqueta { font-weight: 800; font-size: __TPASO__px; letter-spacing: .06em; text-transform: uppercase; color: var(--acento); }
      .portada { position: absolute; left: 96px; right: 40%; top: 50%; transform: translateY(-50%); display: grid; gap: 26px; }
      h1, h2 { font-family: var(--titulo); font-weight: 700; line-height: 1.04; word-spacing: .14em; }
      h1 { font-size: __TTITULO__px; }
      h2 { font-size: calc(__TTITULO__px * .86); }
      .linea { display: block; overflow: hidden; padding-bottom: .1em; }
      .linea > span { display: block; }
      .objetivos { list-style: none; display: grid; gap: 14px; font-size: __TCUERPO__px; font-weight: 600; line-height: 1.2; }
      .objetivos li { display: flex; align-items: center; gap: 16px; }
      .objetivos b { width: 28px; height: 28px; flex: none; border-radius: 50%; background: linear-gradient(135deg, var(--acento), var(--primario)); }
      .degradado { position: absolute; inset: -12%; background: radial-gradient(46% 56% at 74% 30%, color-mix(in srgb, var(--primario) 62%, transparent), transparent 72%), radial-gradient(40% 50% at 18% 78%, color-mix(in srgb, var(--acento) 34%, transparent), transparent 72%); }
      .tarjeta { position: absolute; left: 96px; right: 96px; top: 50%; transform: translateY(-50%); display: grid; gap: 26px; }
      .tarjeta p { font-size: __TCUERPO__px; font-weight: 500; line-height: 1.34; max-width: 26em; color: #dbe9f4; }
      .opciones { display: grid; gap: 16px; margin-top: 8px; max-width: 1300px; }
      .opcion { display: flex; align-items: center; gap: 20px; padding: 18px 28px; border-radius: 18px; background: rgba(255,255,255,.08); box-shadow: 0 0 0 1px rgba(255,255,255,.16); font-size: __TCUERPO__px; font-weight: 700; line-height: 1.2; transform-origin: left center; }
      .opcion b { font-family: var(--titulo); }
      .velo-final { position: absolute; inset: 0; background: radial-gradient(62% 74% at 50% 50%, rgba(2,4,10,.78) 0%, rgba(2,4,10,.62) 58%, rgba(2,4,10,.2) 100%); }
      .final h1 { text-shadow: 0 6px 38px rgba(0,0,0,.75); }
      .final { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 30px; padding: 0 96px; text-align: center; }
      .logo-final { width: min(440px, 46vw); opacity: 0; }
      .boton { padding: 26px 46px; border-radius: 18px; background: linear-gradient(95deg, var(--acento), var(--primario)); color: #02131f; font-weight: 800; font-size: __TCUERPO__px; box-shadow: 0 0 80px color-mix(in srgb, var(--acento) 55%, transparent); opacity: 0; }
      .pie { font-size: __TPASO__px; font-weight: 600; color: #d9f7fb; opacity: 0; }
      .luz-final { position: absolute; inset: 0; opacity: 0; mix-blend-mode: screen; background: radial-gradient(circle at 50% 50%, #ffffff 0%, var(--acento) 34%, var(--primario) 70%, #0c3f90 100%); }
      #chispas { position: absolute; inset: 0; mix-blend-mode: screen; }
      #chispas i { position: absolute; display: block; border-radius: 50%; opacity: 0; background: radial-gradient(circle, #ffffff 0%, #9ff6ff 34%, rgba(25,227,230,0) 72%); }
      #capitulos { position: absolute; left: 64px; right: 64px; top: 34px; height: 8px; display: flex; gap: 10px; }
      .cap { overflow: hidden; border-radius: 4px; background: rgba(255,255,255,.18); }
      .cap i { display: block; height: 100%; background: linear-gradient(90deg, var(--acento), var(--primario)); transform: scaleX(0); transform-origin: left; }
      #marca { position: absolute; right: 64px; bottom: 26px; height: 66px; opacity: .95; }
      #barrido { position: absolute; top: -10%; bottom: -10%; left: -20%; width: 140%; transform: translateX(-120%) skewX(-12deg); background: linear-gradient(90deg, rgba(2,4,10,0) 0%, var(--primario) 26%, var(--acento) 46%, #ffffff 50%, var(--acento) 54%, var(--primario) 74%, rgba(2,4,10,0) 100%); }
      .quemado { position: absolute; left: 76px; right: 170px; top: 1120px; font-family: var(--titulo); font-size: 70px; line-height: 1.08; font-weight: 700; opacity: 0; text-shadow: 0 4px 30px rgba(0,0,0,.9); }
"""


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("tutorial", type=Path)
    p.add_argument("--tiempos", type=Path, required=True)
    a = p.parse_args()
    base = a.tutorial.parent
    guion = json.loads(a.tutorial.read_text(encoding="utf-8"))
    tiempos = json.loads(a.tiempos.read_text(encoding="utf-8"))
    formato = guion.get("formato", "16:9")
    W, H = LIENZOS[formato]
    marca = guion["marca"]
    t_titulo, t_cuerpo, t_nota, t_paso = TEXTOS[formato]
    escenas = preparar_escenas(guion, tiempos, base)
    total = escenas[-1]["inicio"] + escenas[-1]["dur"]
    ctx = {"W": W, "H": H, "foco_y": H * 0.46, "escenario": ESCENARIOS[formato], "clics": [], "golpe": None, "chispas": None,
           "pasos": max((e.get("paso") or 0) for e in escenas), "acento": marca["acento"], "t_nota": t_nota, "primario": marca["primario"],
           "logo": marca["logo"], "marca": marca["nombre"]}
    tl, cuerpo = [], ""
    for escena in escenas:
        contenido = TIPOS[escena["tipo"]](escena, tl, base, ctx)
        # La escena no es un clip: un video con tiempo no puede ir dentro de otro elemento con tiempo
        cuerpo += f'\n      <div id="e{escena["n"]}" class="escena">\n        {contenido}\n      </div>'
        tl.append(f'tl.set("#e{escena["n"]}", {{opacity:1}}, {escena["inicio"]:.3f});')
        tl.append(f'tl.set("#e{escena["n"]}", {{opacity:0}}, {escena["inicio"] + escena["dur"]:.3f});')
    cortes = [e["inicio"] for e in escenas[1:]]
    for c in cortes:
        tl.append(f'tl.fromTo("#barrido", {{x:"-120%", skewX:-12}}, {{x:"120%", skewX:-12, duration:.62, ease:"power2.inOut", immediateRender:false}}, {c - .31:.3f});')

    capitulos = [{"inicio": e["inicio"], "titulo": e["capitulo"]} for e in escenas if e.get("capitulo")]
    if not capitulos or capitulos[0]["inicio"] > 0:
        capitulos.insert(0, {"inicio": 0.0, "titulo": guion.get("titulo", "Inicio")})
    barras = ""
    for i, c in enumerate(capitulos):
        fin = capitulos[i + 1]["inicio"] if i + 1 < len(capitulos) else total
        barras += f'<div class="cap" style="flex:{fin - c["inicio"]:.2f}"><i id="c{i}"></i></div>'
        tl.append(f'tl.to("#c{i}", {{scaleX:1, duration:{fin - c["inicio"]:.2f}, ease:"none"}}, {c["inicio"]:.3f});')

    quemados = subtitulos_quemados(escenas, tl) if guion.get("subtitulos") == "quemados" else ""
    if ctx["chispas"]:
        ini, fin = ctx["chispas"]
        tl.append(f'''let semilla = 11;
      const azar = () => (semilla = (semilla * 16807) % 2147483647) / 2147483647;
      for (let i = 0; i < 70; i++) {{
        const c = document.createElement("i"), lado = 8 + azar() * 22, t = {ini:.3f} + azar() * 1.4;
        c.style.cssText = `left:${{azar() * {W}}}px;top:${{azar() * {H}}}px;width:${{lado}}px;height:${{lado}}px`;
        document.getElementById("chispas").append(c);
        tl.fromTo(c, {{ y: 0 }}, {{ y: -(180 + azar() * 380), x: (azar() - .5) * 140, duration: {fin:.3f} - t, ease: "none" }}, t);
        tl.fromTo(c, {{ opacity: 0 }}, {{ opacity: .5 + azar() * .5, duration: .3, ease: "power2.out" }}, t);
      }}''')

    apertura = next((e for e in escenas if e["tipo"] == "apertura"), None)
    cierre = escenas[-1]
    activa = [f'0-{apertura["dur"] + 0.6:.2f}'] if apertura else []
    activa.append(f'{cierre["inicio"] - 0.6:.2f}-{total:.2f}')
    banda = base / "assets/audio/banda.wav"
    volumen = guion.get("volumen_banda", 0.36)

    def componer_banda(musica):
        subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "banda_sonora.py"), "--duracion", f"{total:.2f}",
                        "--perfil", "sereno", "--activa", ",".join(activa), "--cambios", ",".join(f"{c:.3f}" for c in cortes),
                        "--clics", ",".join(f"{c:.3f}" for c in ctx["clics"]), *(["--golpe", f'{ctx["golpe"]:.3f}'] if ctx["golpe"] else []),
                        "--musica", f"{musica:.4f}", "--salida", str(banda)], check=True, stdout=subprocess.DEVNULL)

    # Se mide donde suena junto a la voz, antes del golpe, y se compone de nuevo con la ganancia justa
    componer_banda(1)
    ventana = (0.5, apertura["dur"] - 0.5) if apertura else (cierre["inicio"], cierre["inicio"] + 3)
    objetivo = LUFS_VOZ - MUSICA_BAJO_VOZ_DB
    componer_banda(10 ** ((objetivo - sonoridad(banda, *ventana, volumen)) / 20))
    musica_lufs = sonoridad(banda, *ventana, volumen)

    fuentes = "".join(f'@font-face {{ font-family: "{f["familia"]}"; src: url("{f["src"]}"); font-weight: {f.get("peso", 700)}; }}\n      '
                      for f in marca.get("fuentes", []))
    css = CSS
    for clave, valor in {"__W__": W, "__H__": H, "__FONDO__": marca.get("fondo", "#02040A"), "__PRIMARIO__": marca["primario"],
                         "__ACENTO__": marca["acento"], "__FTITULO__": marca.get("fuente_titulo", "Montserrat"),
                         "__FTEXTO__": marca.get("fuente_texto", "Inter"), "__TTITULO__": t_titulo, "__TCUERPO__": t_cuerpo,
                         "__TNOTA__": t_nota, "__TPASO__": t_paso}.items():
        css = css.replace(clave, str(valor))
    lineas_tl = "\n      ".join(tl)
    resolucion = {"16:9": "landscape", "9:16": "portrait", "1:1": "square"}[formato]
    pagina = f'''<!doctype html>
<html lang="es" data-resolution="{resolucion}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      {fuentes}{css}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total:.3f}" data-width="{W}" data-height="{H}">
      <div id="luz"></div>{cuerpo}
      {quemados}
      <div id="capitulos">{barras}</div>
      <img id="marca" src="{marca["logo"]}" alt="{html.escape(marca["nombre"])}" />
      <div id="barrido"></div>
      <audio id="voz" class="clip" src="assets/audio/voz.wav" data-start="0" data-duration="{tiempos["total"]:.3f}" data-track-index="8" data-volume="1"></audio>
      <audio id="banda" class="clip" src="assets/audio/banda.wav" data-start="0" data-duration="{total:.3f}" data-track-index="9" data-volume="{volumen}"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {lineas_tl}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
    (base / "index.html").write_text(pagina, encoding="utf-8")
    linea = {"total": round(total, 3), "capitulos": [{"inicio": round(c["inicio"], 2), "titulo": c["titulo"]} for c in capitulos],
             "escenas": [{"n": e["n"], "tipo": e["tipo"], "inicio": round(e["inicio"], 2), "duracion": round(e["dur"], 2)} for e in escenas]}
    (base / "linea-de-tiempo.json").write_text(json.dumps(linea, ensure_ascii=False, indent=1), encoding="utf-8")
    (base / "guion.txt").write_text("\n".join(guion["guion"]) + "\n", encoding="utf-8")
    print(json.dumps({"duracion_s": round(total, 2), "escenas": len(escenas), "capitulos": len(capitulos),
                      "musica_bajo_voz_db": round(LUFS_VOZ - musica_lufs, 1), "avisos": avisos}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
