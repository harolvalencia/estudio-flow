"""Arma el storyboard interactivo: un solo HTML con las imágenes incrustadas.

Uso:
    python armar_storyboard.py 02-storyboard/plan.json [--salida 02-storyboard/storyboard.html]

Las rutas de `imagen` en plan.json son relativas a la carpeta del plan. Cada imagen se
reduce a 540 px de ancho para que el artefacto pese poco. Solo necesita Pillow.
"""
import argparse
import base64
import html
import io
import json
import sys
from pathlib import Path

from PIL import Image

PALABRAS_POR_SEGUNDO = 2.9
PALABRAS_POR_SEGUNDO_FORMATIVO = 2.5
LECCION_MAX_S = 360
ORIGENES = ("pantalla", "flow", "grafico")
CIERRES_FORMATIVOS = ("pregunta", "practica", "caso", "resumen", "invitacion", "siguiente")
CIERRES_CON_COMPROBACION = ("pregunta", "practica", "caso")
ANCHO = 540
CALIDAD = 76
LIMITE_MB = 15
PLANTILLA = Path(__file__).resolve().parent.parent / "assets" / "plantilla.html"
if not PLANTILLA.exists():
    PLANTILLA = Path(__file__).resolve().parent / "plantilla.html"


def a_data_uri(ruta):
    img = Image.open(ruta).convert("RGB")
    if img.width > ANCHO:
        img = img.resize((ANCHO, round(img.height * ANCHO / img.width)), Image.LANCZOS)
    salida = io.BytesIO()
    img.save(salida, "JPEG", quality=CALIDAD, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(salida.getvalue()).decode()


def revisar(plan):
    """Una propuesta sin voz en alguna escena o sin cierre no se muestra. Un plan sin los campos nuevos valida como antes."""
    fallos = []
    formativo = plan.get("tipo") == "formativo"
    cierre = plan.get("cierre_formativo")
    if cierre and cierre not in CIERRES_FORMATIVOS:
        fallos.append(f'"cierre_formativo" debe ser uno de: {", ".join(CIERRES_FORMATIVOS)}')
    if formativo:
        for campo in ("objetivos", "fuente", "valida"):
            if not plan.get(campo):
                fallos.append(f'Falta "{campo}": un video formativo necesita objetivos, fuente y quién valida')
        for prop in plan["propuestas"]:
            if (not cierre or cierre in CIERRES_CON_COMPROBACION) and not any(e.get("practica") for e in prop["escenas"]):
                fallos.append(f'{prop["id"]}: falta una comprobación, una escena con "practica": true')
            pasos = [e["paso"] for e in prop["escenas"] if e.get("paso") is not None]
            if pasos != sorted(pasos):
                fallos.append(f'{prop["id"]}: los pasos van en desorden ({pasos}). Todas las propuestas siguen la secuencia aprobada')
            if prop["escenas"][-1]["fin"] > LECCION_MAX_S and not plan.get("largo_aprobado"):
                fallos.append(f'{prop["id"]}: pasa de {LECCION_MAX_S // 60} minutos, divídela en una serie')
            for n, e in enumerate(prop["escenas"], 1):
                if e.get("origen") not in ORIGENES:
                    fallos.append(f'{prop["id"]}, escena {n}: "origen" debe ser pantalla, flow o grafico')
    if plan.get("sin_voz"):
        return fallos
    ritmo = plan.get("ritmo") or (PALABRAS_POR_SEGUNDO_FORMATIVO if formativo else PALABRAS_POR_SEGUNDO)
    for prop in plan["propuestas"]:
        for n, e in enumerate(prop["escenas"], 1):
            voz = (e.get("locucion") or "").strip()
            if not voz:
                fallos.append(f'{prop["id"]}, escena {n}: falta la locución')
            elif len(voz.split()) / ritmo > e["fin"] - e["inicio"]:
                fallos.append(f'{prop["id"]}, escena {n}: la locución no cabe en {e["fin"] - e["inicio"]} s a {ritmo} palabras por segundo')
        if not prop["escenas"][-1].get("cta"):
            fallos.append(f'{prop["id"]}: la última escena debe marcarse como cierre con "cta": true')
    return fallos


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("plan", type=Path)
    p.add_argument("--salida", type=Path)
    a = p.parse_args()
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
    fallos = revisar(plan)
    if fallos:
        sys.exit("El plan no cumple el estándar:\n- " + "\n- ".join(fallos))
    base = a.plan.parent
    for propuesta in plan["propuestas"]:
        for escena in propuesta["escenas"]:
            ruta = base / escena["imagen"]
            if not ruta.exists():
                sys.exit(f"Falta la imagen {ruta}")
            escena["imagen"] = a_data_uri(ruta)
    marca = plan.get("marca", {})
    logo = marca.get("logo")
    if logo and (base / logo).exists():
        marca["logo"] = "data:image/png;base64," + base64.b64encode((base / logo).read_bytes()).decode()
    else:
        marca["logo"] = ""
    datos = json.dumps(plan, ensure_ascii=False).replace("</", "<\\/")
    pagina = (PLANTILLA.read_text(encoding="utf-8")
              .replace("__TITULO__", html.escape(plan["pieza"]))
              .replace("__PRIMARIO__", marca.get("primario", "#2EA3F2"))
              .replace("__ACENTO__", marca.get("acento", "#00C2D1"))
              .replace("__DATOS__", datos))
    salida = a.salida or base / "storyboard.html"
    salida.write_text(pagina, encoding="utf-8")
    peso = salida.stat().st_size / 1e6
    print(f"Listo: {salida} ({peso:.1f} MB)")
    if peso > LIMITE_MB:
        sys.exit(f"Pesa más de {LIMITE_MB} MB: usa menos escenas por propuesta.")


if __name__ == "__main__":
    main()
