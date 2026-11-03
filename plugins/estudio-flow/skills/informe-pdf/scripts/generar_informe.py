"""Genera el PDF del proceso a partir de 00-brief/proceso.json.

Uso:
    python generar_informe.py CARPETA_DE_TRABAJO [--salida 06-informe/Proceso.pdf]

Lee proceso.json y, si existen, 02-storyboard/plan.json y la portada del video. Escribe
06-informe/informe.html y lo imprime a PDF con Chrome o Chromium sin interfaz.
"""
import argparse
import html
import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


def e(valor):
    return html.escape(str(valor if valor is not None else ""))


def buscar_chrome():
    candidatos = [os.environ.get("HYPERFRAMES_BROWSER_PATH", "")]
    cache = Path.home() / ".cache" / "hyperframes" / "chrome"
    if cache.exists():
        candidatos += [str(p) for p in cache.rglob("chrome-headless-shell*") if p.is_file()]
    candidatos += [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("google-chrome") or "",
        shutil.which("chromium") or "",
        shutil.which("chromium-browser") or "",
    ]
    return next((c for c in candidatos if c and Path(c).exists()), "")


def ruta_relativa(carpeta, relativa):
    """Ruta desde 06-informe si el archivo existe; si no, vacío."""
    if not relativa:
        return ""
    return f"../{relativa}" if (carpeta / relativa).exists() else ""


def tabla(encabezados, filas):
    th = "".join(f"<th>{e(h)}</th>" for h in encabezados)
    tr = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in fila) + "</tr>" for fila in filas)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>"


ESTILO = """
@page{size:Letter;margin:0}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;font:400 10.5pt/1.55 'Manrope','Segoe UI',Arial,sans-serif;color:#17202b;background:#fff}
.portada{height:11in;padding:.9in .8in;background:#05070c;color:#fff;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden;break-after:page}
.portada::before{content:"";position:absolute;inset:auto -2in -3in auto;width:8in;height:8in;border-radius:50%;background:radial-gradient(circle,var(--acento),transparent 68%);opacity:.5}
.portada>*{position:relative}
.portada img.logo{height:.55in;align-self:flex-start}
.portada h1{font:700 40pt/1.08 'Sora','Segoe UI',sans-serif;margin:0 0 .15in;max-width:6in}
.portada p{font-size:12pt;color:#c7d2de;margin:0;max-width:5.4in}
.portada .pie{font-size:9pt;color:#9aa8b8}
.hoja{padding:.7in .8in;break-after:page}
.hoja:last-child{break-after:auto}
h2{font:700 19pt/1.2 'Sora','Segoe UI',sans-serif;margin:0 0 .12in;color:#0b1320}
h2 small{display:block;font:600 8.5pt/1 'Manrope',sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--marca);margin-bottom:.08in}
h3{font:700 11.5pt/1.3 'Sora','Segoe UI',sans-serif;margin:.2in 0 .05in}
p{margin:.04in 0 .1in}
.ficha{display:grid;grid-template-columns:1.5in 1fr;gap:.05in .2in;margin:.12in 0}
.ficha b{color:#5b6877;font-weight:600}
table{width:100%;border-collapse:collapse;font-size:9pt;margin:.1in 0 .18in}
th{text-align:left;font-weight:700;background:#eef2f7;color:#34404e}
th,td{padding:.06in .08in;border-bottom:1px solid #dde3ea;vertical-align:top}
tr{break-inside:avoid}
.prop{display:grid;grid-template-columns:repeat(3,1fr);gap:.16in;margin:.12in 0}
.prop>div{border:1px solid #dde3ea;border-radius:8px;overflow:hidden;break-inside:avoid}
.prop .elegida{border:2px solid var(--marca)}
.prop .fotos{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:#000}
.prop img{width:100%;aspect-ratio:9/16;object-fit:cover;display:block}
.prop .txt{padding:.08in .1in;font-size:9pt}
.prop b{display:block;font:700 10pt/1.25 'Sora',sans-serif}
.sello{display:inline-block;background:var(--marca);color:#fff;font-size:7.5pt;font-weight:700;padding:1px 6px;border-radius:4px;margin-top:3px}
pre{white-space:pre-wrap;word-break:break-word;font:8pt/1.45 Consolas,'Courier New',monospace;background:#f3f6f9;padding:.08in;border-radius:6px;margin:.04in 0 .12in}
.final{display:grid;grid-template-columns:2in 1fr;gap:.25in;align-items:start}
.final img{width:100%;border-radius:8px;display:block}
ul{margin:.04in 0 .1in;padding-left:.2in}
"""


def construir(carpeta, p):
    marca = p.get("marca", {})
    b = p.get("brief", {})
    plan_ruta = carpeta / "02-storyboard" / "plan.json"
    plan = json.loads(plan_ruta.read_text(encoding="utf-8")) if plan_ruta.exists() else {}
    logo = ruta_relativa(carpeta, marca.get("logo"))
    fecha = (p.get("fechas") or {}).get("fin") or date.today().isoformat()

    portada = f"""<section class="portada">
      {f'<img class="logo" src="{e(logo)}" alt="">' if logo else '<div></div>'}
      <div><h1>{e(p.get("pieza", "Producción"))}</h1>
      <p>Informe del proceso: de la idea al video final.</p></div>
      <div class="pie">{e(marca.get("nombre", ""))} · {e(fecha)}</div></section>"""

    ficha = "".join(f"<b>{e(k)}</b><span>{e(v)}</span>" for k, v in [
        ("Objetivo", b.get("objetivo")), ("Público", b.get("publico")),
        ("Redes", ", ".join(b.get("redes", []))), ("Formato", b.get("formato")),
        ("Duración", f'{b.get("duracion_s", "")} s'), ("Llamado a la acción", b.get("cta"))] if v)

    tarjetas = []
    elegidas = {x.get("id") for x in p.get("propuestas", []) if x.get("elegida")}
    for prop in plan.get("propuestas", p.get("propuestas", [])):
        fotos = "".join(f'<img src="../02-storyboard/{e(s["imagen"])}" alt="">'
                        for s in prop.get("escenas", [])[:3]
                        if (carpeta / "02-storyboard" / s["imagen"]).exists())
        sello = '<span class="sello">Elegida</span>' if prop.get("id") in elegidas else ""
        clase = ' class="elegida"' if prop.get("id") in elegidas else ""
        tarjetas.append(f'<div{clase}><div class="fotos">{fotos}</div><div class="txt">'
                        f'<b>{e(prop.get("id"))}. {e(prop.get("nombre"))}</b>{sello}'
                        f'<p>{e(prop.get("concepto"))}</p></div></div>')

    pres = p.get("presupuesto", {})
    clips = p.get("clips", [])
    gastados = sum(c.get("puntos", 0) for c in clips)
    resumen_clips = tabla(["Clip", "Modelo", "Modo", "Intentos", "Puntos", "Notas"],
                          [[c.get("n"), c.get("modelo"), c.get("modo"), c.get("intentos"), c.get("puntos"),
                            c.get("notas", "")] for c in clips]) if clips else "<p>Esta pieza no usó clips generados.</p>"
    prompts = "".join(f'<h3>Clip {e(c.get("n"))}</h3><pre>{e(c.get("prompt", ""))}</pre>'
                      for c in clips if c.get("prompt"))
    elementos = "".join(f"<li>{e(x)}</li>" for x in p.get("montaje", {}).get("elementos", []))
    entregables = p.get("entregables", [])
    tabla_final = tabla(["Archivo", "Destino", "Resolución", "Duración", "Peso"],
                        [[x.get("archivo"), x.get("red"), x.get("resolucion"), f'{x.get("duracion_s")} s',
                          f'{x.get("peso_mb")} MB'] for x in entregables])
    imagen_final = next((ruta_relativa(carpeta, x["archivo"]) for x in entregables
                         if x.get("archivo", "").endswith(".jpg")), "")
    portadas = sorted((carpeta / "05-final").glob("*portada*.jpg")) if (carpeta / "05-final").exists() else []
    if not imagen_final and portadas:
        imagen_final = f"../05-final/{portadas[0].name}"
    lecciones = "".join(f"<li>{e(x)}</li>" for x in p.get("lecciones", []))
    retro = "".join(f"<li>{e(x)}</li>" for x in p.get("retroalimentacion", []))

    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{e(p.get("pieza", "Proceso"))}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&family=Sora:wght@600;700&display=swap">
<style>:root{{--marca:{e(marca.get("primario", "#1893F8"))};--acento:{e(marca.get("acento", "#00C2D1"))}}}{ESTILO}</style></head><body>
{portada}
<section class="hoja"><h2><small>1. El encargo</small>Qué se pidió</h2><div class="ficha">{ficha}</div>
<h2 style="margin-top:.3in"><small>2. Las propuestas</small>Los caminos y la decisión</h2>
<div class="prop">{"".join(tarjetas)}</div>
{f"<h3>Retroalimentación</h3><ul>{retro}</ul>" if retro else ""}</section>
<section class="hoja"><h2><small>3. Producción en Flow</small>Lo que se generó</h2>
<p>Puntos aprobados: <b>{e(pres.get("puntos_aprobados", 0))}</b> · Puntos usados: <b>{gastados}</b> · Saldo inicial: <b>{e(pres.get("saldo_inicial", ""))}</b></p>
{resumen_clips}{prompts}</section>
<section class="hoja"><h2><small>4. Acabado</small>Montaje con HyperFrames</h2>
{f"<ul>{elementos}</ul>" if elementos else ""}
<h2 style="margin-top:.3in"><small>5. Entrega</small>Archivos finales</h2>
<div class="final">{f'<img src="{e(imagen_final)}" alt="">' if imagen_final else "<div></div>"}<div>{tabla_final}
{f"<h3>Lecciones para la próxima pieza</h3><ul>{lecciones}</ul>" if lecciones else ""}</div></div></section>
</body></html>"""


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("carpeta", type=Path)
    a.add_argument("--salida", type=Path)
    args = a.parse_args()
    carpeta = args.carpeta.resolve()
    proceso = carpeta / "00-brief" / "proceso.json"
    if not proceso.exists():
        sys.exit(f"No existe {proceso}")
    p = json.loads(proceso.read_text(encoding="utf-8"))
    destino = carpeta / "06-informe"
    destino.mkdir(exist_ok=True)
    pagina = destino / "informe.html"
    pagina.write_text(construir(carpeta, p), encoding="utf-8")
    pdf = (args.salida or destino / f"Proceso-{p.get('pieza', 'pieza').replace(' ', '-')}.pdf").resolve()
    chrome = buscar_chrome()
    if not chrome:
        sys.exit("No encontré Chrome. Ejecuta: npx hyperframes browser ensure. El HTML quedó en " + str(pagina))
    subprocess.run([chrome, "--headless=new" if "headless-shell" not in chrome else "--headless",
                    "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                    "--allow-file-access-from-files", f"--print-to-pdf={pdf}", pagina.as_uri()],
                   check=True, capture_output=True, timeout=180)
    print(f"Listo: {pdf} ({pdf.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
