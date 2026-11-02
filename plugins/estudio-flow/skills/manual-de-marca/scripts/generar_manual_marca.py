"""Genera el manual de marca en PDF a partir de 00-brief/marca.json.

Uso:
    python generar_manual_marca.py CARPETA_DE_TRABAJO [--salida 06-informe/Manual.pdf]

El diseño sale de la propia marca: sus colores, tipografías, logo e imágenes. Calcula
RGB, CMYK aproximado y contraste real de cada color. Imprime con Chrome sin interfaz.
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

ETIQUETAS_CONTRASTE = [(7, "AAA"), (4.5, "AA"), (3, "AA grande")]


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


def rgb(hexa):
    h = hexa.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def cmyk(hexa):
    r, g, b = [c / 255 for c in rgb(hexa)]
    k = 1 - max(r, g, b)
    if k == 1:
        return (0, 0, 0, 100)
    return tuple(round(100 * v) for v in ((1 - r - k) / (1 - k), (1 - g - k) / (1 - k), (1 - b - k) / (1 - k), k))


def luminancia(hexa):
    canales = []
    for c in rgb(hexa):
        c /= 255
        canales.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * canales[0] + 0.7152 * canales[1] + 0.0722 * canales[2]


def contraste(a, b):
    x, y = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def sobre(hexa):
    return "#FFFFFF" if contraste(hexa, "#FFFFFF") >= contraste(hexa, "#000000") else "#000000"


def nivel(valor):
    return next((n for t, n in ETIQUETAS_CONTRASTE if valor >= t), "Solo decorativo")


def ruta(carpeta, relativa):
    """Ruta desde 06-informe si el archivo existe; si no, vacío."""
    if not relativa:
        return ""
    return f"../{relativa}" if (carpeta / relativa).exists() else ""


def caras(tipografias, carpeta):
    css, enlaces = [], []
    for t in tipografias:
        if t.get("archivo") and (carpeta / t["archivo"]).exists():
            css.append(f'@font-face{{font-family:"{e(t["nombre"])}";src:url("../{e(t["archivo"])}");font-weight:{e(t.get("peso", 400))}}}')
        elif t.get("google"):
            enlaces.append(t["google"].replace(" ", "+"))
    enlace = ""
    if enlaces:
        familias = "&".join(f"family={f}:wght@400;600;700" for f in enlaces)
        enlace = f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{familias}&display=swap">'
    return enlace, "".join(css)


def estilo(m):
    colores = m["colores"]
    oscuro = min(colores, key=lambda c: luminancia(c["hex"]))["hex"]
    if luminancia(oscuro) > 0.05:
        oscuro = "#07090F"
    resto = [c for c in colores if contraste(c["hex"], oscuro) >= 3] or [{"hex": "#FFFFFF"}]
    acento = max(resto, key=lambda c: (c.get("rol", "").lower() == "acento", contraste(c["hex"], oscuro)))["hex"]
    a, b = (m.get("degradado") or [acento, resto[-1]["hex"]])[:2]
    letras = m.get("tipografias") or [{"nombre": "Segoe UI"}]
    titulo = next((t for t in letras if "tít" in t.get("rol", "").lower()), letras[0])["nombre"]
    cuerpo = next((t for t in letras if "tex" in t.get("rol", "").lower()), letras[-1])["nombre"]
    return {"oscuro": oscuro, "acento": acento, "a": a, "b": b, "titulo": titulo, "cuerpo": cuerpo}


CSS = """
@page{size:8.5in 11in;margin:0}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;background:var(--o);color:#f5f8fb;font:400 11pt/1.55 var(--cu),"Segoe UI",sans-serif}
.p{position:relative;width:8.5in;height:11in;overflow:hidden;break-after:page;background:var(--o)}
.p:last-child{break-after:auto}
.halo{background:radial-gradient(ellipse 80% 50% at 100% -8%,color-mix(in srgb,var(--b) 38%,transparent),transparent 70%),radial-gradient(ellipse 65% 42% at -10% 108%,color-mix(in srgb,var(--a) 26%,transparent),transparent 70%),var(--o)}
.in{position:absolute;inset:.7in .75in .85in;display:flex;flex-direction:column;gap:.2in}
.pie{position:absolute;left:.75in;right:.75in;bottom:.36in;display:flex;justify-content:space-between;align-items:center;font-size:8pt;color:#ffffffa0}
.pie img{height:.26in}
.eti{font:700 8pt/1 var(--cu);letter-spacing:.2em;text-transform:uppercase;color:var(--ac)}
h1,h2,h3{font-family:var(--ti),"Segoe UI",sans-serif;margin:0;font-weight:700;text-wrap:balance}
h2{font-size:32pt;line-height:1.05}
h3{font-size:14pt;line-height:1.2}
p{margin:0}
.intro{font-size:13pt;line-height:1.45;color:#dfe7ef;max-width:6.3in}
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.velo{position:absolute;inset:0;background:linear-gradient(180deg,color-mix(in srgb,var(--o) 60%,transparent) 0%,transparent 28%,transparent 55%,color-mix(in srgb,var(--o) 92%,transparent) 80%,var(--o) 100%)}
.port{position:absolute;left:.75in;right:.75in;bottom:.8in}
.port h1{font-size:62pt;line-height:.96}
.port .sub{font-size:15pt;color:#e7eef5;margin-top:.14in;max-width:5.6in}
.port .meta{display:flex;justify-content:space-between;margin-top:.26in;padding-top:.1in;border-top:1px solid #ffffff55;font-size:9pt;color:#d5dfe9}
.logo-sup{position:absolute;left:.75in;top:.65in;height:.74in}
.card{background:#ffffff0f;border:1px solid #ffffff22;border-radius:12px;padding:.17in .19in}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:.17in}
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:.15in}
.fig{width:100%;object-fit:cover;border-radius:12px;display:block}
.logo-caja{border-radius:12px;display:grid;place-items:center;padding:.3in;height:1.9in}
.logo-caja img{max-height:1.1in;max-width:80%}
.ma{display:flex;flex-direction:column;gap:.05in}
.ma span{font-size:9.4pt;color:#d4dde6}
.barra{display:flex;height:.42in;border-radius:9px;overflow:hidden}
.mues{border-radius:12px;padding:.14in .16in;min-height:2in;display:flex;flex-direction:column;justify-content:flex-end;gap:.02in}
.mues b{font:700 14pt/1.1 var(--ti);margin-bottom:.03in}
.mues span{font-size:8.6pt;line-height:1.35}
table{width:100%;border-collapse:collapse;font-size:9.6pt}
th{font-size:7.6pt;letter-spacing:.1em;text-transform:uppercase;text-align:left;color:var(--ac);padding:.07in .08in;border-bottom:1px solid var(--ac)}
td{padding:.075in .08in;border-bottom:1px solid #ffffff1f;vertical-align:middle}
.tin{display:inline-block;padding:.02in .1in;border-radius:6px;font-weight:700}
.chip{display:inline-block;font-size:8pt;font-weight:700;padding:.03in .1in;border-radius:20px;background:#ffffff1a}
.tipo{font-size:44pt;line-height:1.05}
.abc{font-size:15pt;line-height:1.35;color:#dfe7ef}
ul{margin:0;padding-left:.18in}
li{margin:.04in 0;color:#dfe7ef;font-size:10.4pt}
pre{margin:0;white-space:pre-wrap;overflow-wrap:anywhere;font:400 8.8pt/1.5 Consolas,monospace;color:#d7eaf6}
.tel{aspect-ratio:9/16;border-radius:14px;overflow:hidden;position:relative;background:var(--o);border:1px solid #ffffff2a}
.tel img.f{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.tel .v{position:absolute;inset:0;background:linear-gradient(180deg,transparent 35%,color-mix(in srgb,var(--o) 90%,transparent) 78%)}
.tel .t{position:absolute;left:9%;right:14%;top:50%;font:700 15pt/1.12 var(--ti)}
.tel .b{position:absolute;left:9%;top:75%;padding:.05in .1in;border-radius:6px;font-weight:800;font-size:8pt;color:#04121f;background:linear-gradient(95deg,var(--a),var(--b))}
.tel img.l{position:absolute;left:9%;top:6%;width:42%}
.acento{color:var(--ac)}
"""


def pie(m, n, logo):
    img = f'<img src="{e(logo)}" alt="">' if logo else "<span></span>"
    return f'<div class="pie">{img}<span>Manual de marca · {e(m["empresa"])}</span><b>{n}</b></div>'


def construir(carpeta, m):
    t = estilo(m)
    ima = m.get("imagenes", {})
    logos = m.get("logo", {})
    claro = ruta(carpeta, logos.get("oscuro"))  # la versión que se lee sobre fondo oscuro
    azul = ruta(carpeta, logos.get("claro"))
    portada = ruta(carpeta, ima.get("portada"))
    esencia = m.get("esencia", {})
    voz = m.get("voz", {})
    fecha = m.get("fecha") or date.today().isoformat()
    paginas, n = [], 1
    enlace, fuentes_css = caras(m.get("tipografias", []), carpeta)

    def agregar(cuerpo, fondo="halo"):
        nonlocal n
        n += 1
        paginas.append(f'<section class="p {fondo}"><div class="in">{cuerpo}</div>{pie(m, n, claro)}</section>')

    origen = {"web": "Construido con lo que la compañía publica en su sitio web.",
              "nueva": "Dirección de marca propuesta a partir de la entrevista."}.get(m.get("origen"), "")
    paginas.append(f'''<section class="p">
      {f'<img class="bg" src="{e(portada)}" alt="">' if portada else ""}<div class="velo"></div>
      {f'<img class="logo-sup" src="{e(claro)}" alt="">' if claro else ""}
      <div class="port"><div class="eti" style="font-size:10pt;color:#fff;margin-bottom:.14in">Manual de marca</div>
      <h1>{e(m["empresa"])}</h1><p class="sub">{e(m.get("lema", ""))}</p>
      <div class="meta"><span>{e(m.get("sitio", ""))}</span><span>{e(fecha)}</span></div></div></section>''')

    personalidad = "".join(f'<span class="chip" style="font-size:9.6pt">{e(x)}</span>' for x in esencia.get("personalidad", []))
    img_esencia = ruta(carpeta, ima.get("esencia"))
    agregar(f'''<div class="eti">La esencia</div><h2>Quiénes somos</h2>
      {f'<img class="fig" style="height:3.1in" src="{e(img_esencia)}" alt="">' if img_esencia else ""}
      <p class="intro">{e(esencia.get("proposito", ""))}</p>
      <div class="g2"><div class="card"><h3>Promesa</h3><p style="margin-top:.05in">{e(esencia.get("promesa", ""))}</p></div>
      <div class="card"><h3>Para quién</h3><p style="margin-top:.05in">{e(esencia.get("publico", ""))}</p></div></div>
      <div style="display:flex;flex-wrap:wrap;gap:.08in">{personalidad}</div>
      <p style="font-size:9.6pt;color:#ffffffb0">{e(origen)}</p>''')

    cajas = []
    if claro:
        cajas.append(f'<div class="ma"><div class="logo-caja" style="background:{t["oscuro"]};border:1px solid #ffffff2a"><img src="{e(claro)}" alt=""></div><span>Sobre fondo oscuro</span></div>')
    if azul:
        cajas.append(f'<div class="ma"><div class="logo-caja" style="background:#fff"><img src="{e(azul)}" alt=""></div><span>Sobre fondo claro</span></div>')
    elif claro:
        cajas.append(f'<div class="ma"><div class="logo-caja" style="background:linear-gradient(120deg,{t["a"]},{t["b"]})"><img src="{e(claro)}" alt=""></div><span>Sobre el degradado de marca</span></div>')
    malos = ""
    if claro:
        malos = f'''<div class="g3">
        <div class="ma"><div class="logo-caja" style="height:1.15in;background:{t["oscuro"]};border:1px solid #ffffff2a"><img src="{e(claro)}" alt="" style="transform:scaleX(1.35) scaleY(.7)"></div><span>No lo deformes</span></div>
        <div class="ma"><div class="logo-caja" style="height:1.15in;background:#e9edf1"><img src="{e(claro)}" alt=""></div><span>No lo uses sin contraste</span></div>
        <div class="ma"><div class="logo-caja" style="height:1.15in;background:{t["oscuro"]};border:1px solid #ffffff2a"><img src="{e(claro)}" alt="" style="transform:rotate(-14deg)"></div><span>No lo gires</span></div></div>'''
    agregar(f'''<div class="eti">Identidad</div><h2>El logo</h2>
      <p class="intro">Se usa completo y con aire a su alrededor. Deja libre, como mínimo, la altura de su símbolo dividida entre dos.</p>
      <div class="g2">{"".join(cajas)}</div><h3>Usos que debilitan la marca</h3>{malos}''')

    colores = m["colores"]
    total = sum(c.get("uso", 1) for c in colores) or 1
    barra = "".join(f'<div style="background:{e(c["hex"])};width:{c.get("uso", 1) / total * 100:.1f}%"></div>' for c in colores)
    muestras = []
    for c in colores:
        r, g, b = rgb(c["hex"])
        ci, ma, am, ne = cmyk(c["hex"])
        tx = sobre(c["hex"])
        borde = "border:1px solid #ffffff33;" if luminancia(c["hex"]) < 0.02 else ""
        muestras.append(f'<div class="mues" style="background:{e(c["hex"])};color:{tx};{borde}"><b>{e(c["nombre"])}</b><span>{e(c.get("rol", ""))}</span>'
                        f'<span>HEX {e(c["hex"].upper())}</span><span>RGB {r} {g} {b}</span><span>CMYK {ci} {ma} {am} {ne}</span></div>')
    agregar(f'''<div class="eti">Color</div><h2>La paleta</h2>
      <p class="intro">Los colores se reconocen por cuánto se usan, no solo por cuáles son. Esta barra muestra la proporción sugerida.</p>
      <div class="barra">{barra}</div><div class="g3">{"".join(muestras)}</div>
      <p style="font-size:9.2pt;color:#ffffffb0">CMYK calculado desde pantalla: pide una prueba de color antes de imprimir.</p>''')

    filas = []
    fondos = sorted(colores, key=lambda c: luminancia(c["hex"]))[:2] + [{"nombre": "Blanco", "hex": "#FFFFFF"}]
    for fondo in fondos:
        for texto in colores + [{"nombre": "Blanco", "hex": "#FFFFFF"}]:
            if texto["hex"].lower() == fondo["hex"].lower():
                continue
            v = contraste(fondo["hex"], texto["hex"])
            if v >= 3:
                filas.append((v, f'<tr><td><span class="tin" style="background:{e(fondo["hex"])};color:{e(texto["hex"])};border:1px solid #ffffff2a">Aa</span></td>'
                                 f'<td>{e(texto["nombre"])} sobre {e(fondo["nombre"])}</td><td>{v:.1f}:1</td><td>{nivel(v)}</td></tr>'))
    filas = [f for _, f in sorted(filas, key=lambda x: -x[0])[:8]]
    img_color = ruta(carpeta, ima.get("color"))
    agregar(f'''<div class="eti">Color</div><h2>Combinaciones que se leen</h2>
      <p class="intro">Contraste medido, no estimado. Para texto pequeño usa AA o AAA.</p>
      <table><thead><tr><th>Muestra</th><th>Combinación</th><th>Contraste</th><th>Nivel</th></tr></thead>{"".join(filas)}</table>
      {f'<img class="fig" style="height:2.6in" src="{e(img_color)}" alt="">' if img_color else ""}''')

    tipos = []
    for f in m.get("tipografias", []):
        tipos.append(f'''<div class="card"><div class="eti">{e(f.get("rol", ""))}</div>
          <div class="tipo" style="font-family:'{e(f["nombre"])}';font-weight:{e(f.get("peso", 400))};margin-top:.08in">{e(f["nombre"])}</div>
          <div class="abc" style="font-family:'{e(f["nombre"])}';font-weight:{e(f.get("peso", 400))}">ABCDEFGHIJKLMNÑOPQRSTUVWXYZ<br>abcdefghijklmnñopqrstuvwxyz 0123456789</div></div>''')
    agregar(f'<div class="eti">Tipografía</div><h2>Cómo escribimos</h2>{"".join(tipos)}')

    decimos = "".join(f"<li>{e(x)}</li>" for x in voz.get("decimos", []))
    evitamos = "".join(f"<li>{e(x)}</li>" for x in voz.get("evitamos", []))
    vf = m.get("voz_flow") or {}
    bloque_voz = ""
    if vf:
        bloque_voz = f'''<div class="card"><div class="eti">La voz en video</div><h3 style="margin:.06in 0 .04in">{e(vf.get("nombre", ""))}</h3>
        <p>Voz de Google Flow basada en {e(vf.get("base", ""))}. {e(vf.get("interpretacion", ""))}</p></div>'''
    agregar(f'''<div class="eti">Voz y tono</div><h2>Cómo sonamos</h2><p class="intro">{e(voz.get("tono", ""))}</p>
      <div class="g2"><div class="card"><h3>Decimos</h3><ul style="margin-top:.06in">{decimos}</ul></div>
      <div class="card"><h3>Evitamos</h3><ul style="margin-top:.06in">{evitamos}</ul></div></div>{bloque_voz}''')

    im = m.get("imagineria", {})
    fotos = [ruta(carpeta, x) for x in ima.get("imagineria", [])]
    fotos = "".join(f'<img class="fig" style="height:2.3in" src="{e(x)}" alt="">' for x in fotos if x)
    agregar(f'''<div class="eti">Imagen</div><h2>Cómo nos vemos</h2><p class="intro">{e(im.get("estilo", ""))}</p>
      <div class="g2">{fotos}</div>
      <div class="card"><div class="eti">Receta para Google Flow</div><pre style="margin-top:.08in">{e(im.get("prompt_base", ""))}</pre></div>
      <p style="font-size:9.6pt;color:#ffffffb0"><b>Evitar:</b> {e(im.get("evitar", ""))}</p>''')

    frases = (voz.get("decimos") or [m.get("lema", "")])
    bases = [ruta(carpeta, x) for x in ima.get("imagineria", [])][:3]
    telefonos = []
    for i, f in enumerate(bases):
        logo = f'<img class="l" src="{e(claro)}" alt="">' if claro else ""
        telefonos.append(f'<div class="tel"><img class="f" src="{e(f)}" alt=""><div class="v"></div>{logo}<div class="t">{e(frases[i % len(frases)])}</div></div>')
    agregar(f'''<div class="eti">En redes</div><h2>La marca en acción</h2>
      <p class="intro">Fondo con imagen, una sola frase, logo discreto. Todo el texto entre el 9 % y el 69 % de la altura para no chocar con la interfaz de la red.</p>
      <div class="g3">{"".join(telefonos)}</div>''')

    fuentes = "".join(f'<tr><td>{e(x.get("dato"))}</td><td>{e(x.get("origen"))}</td></tr>' for x in m.get("fuentes", []))
    pendientes = "".join(f"<li>{e(x)}</li>" for x in m.get("pendientes", []))
    agregar(f'''<div class="eti">Transparencia</div><h2>De dónde sale cada dato</h2>
      <table><thead><tr><th>Dato</th><th>Fuente</th></tr></thead>{fuentes}</table>
      <div class="card"><h3>Por confirmar con la compañía</h3><ul style="margin-top:.06in">{pendientes}</ul></div>
      <p style="font-size:9.6pt;color:#ffffffb0">Este documento organiza lo que se investigó. Se convierte en manual oficial cuando la compañía lo apruebe.</p>''')

    cierre = ruta(carpeta, ima.get("cierre"))
    paginas.append(f'''<section class="p">{f'<img class="bg" src="{e(cierre)}" alt="">' if cierre else ""}<div class="velo"></div>
      <div class="port">{f'<img src="{e(claro)}" alt="" style="height:1in;margin-bottom:.2in;display:block">' if claro else ""}
      <h1 style="font-size:38pt;line-height:1.08">{e(m.get("lema", ""))}</h1><p class="sub">{e(m.get("sitio", ""))}</p></div></section>''')

    variables = (f':root{{--o:{t["oscuro"]};--ac:{t["acento"]};--a:{t["a"]};--b:{t["b"]};'
                 f'--ti:"{e(t["titulo"])}";--cu:"{e(t["cuerpo"])}"}}')
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Manual de marca {e(m["empresa"])}</title>'
            f'{enlace}<style>{fuentes_css}{variables}{CSS}</style></head><body>{"".join(paginas)}</body></html>')


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("carpeta", type=Path)
    a.add_argument("--salida", type=Path)
    args = a.parse_args()
    carpeta = args.carpeta.resolve()
    origen = carpeta / "00-brief" / "marca.json"
    if not origen.exists():
        sys.exit(f"No existe {origen}")
    m = json.loads(origen.read_text(encoding="utf-8"))
    if not m.get("colores"):
        sys.exit("marca.json no trae colores.")
    destino = carpeta / "06-informe"
    destino.mkdir(exist_ok=True)
    pagina = destino / "manual-de-marca.html"
    pagina.write_text(construir(carpeta, m), encoding="utf-8")
    pdf = (args.salida or destino / f"Manual-de-Marca-{m['empresa'].replace(' ', '-')}.pdf").resolve()
    chrome = buscar_chrome()
    if not chrome:
        sys.exit("No encontré Chrome. Ejecuta: npx hyperframes browser ensure. El HTML quedó en " + str(pagina))
    subprocess.run([chrome, "--headless=new" if "headless-shell" not in chrome else "--headless",
                    "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer", "--virtual-time-budget=9000",
                    "--allow-file-access-from-files", f"--print-to-pdf={pdf}", pagina.as_uri()],
                   check=True, capture_output=True, timeout=180)
    print(f"Listo: {pdf} ({pdf.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
