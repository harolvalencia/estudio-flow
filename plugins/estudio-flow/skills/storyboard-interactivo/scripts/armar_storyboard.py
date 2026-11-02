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


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("plan", type=Path)
    p.add_argument("--salida", type=Path)
    a = p.parse_args()
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
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
