"""Mide cuánto duró una producción a partir de las fechas de sus archivos. Solo lee.

Uso:
    python medir_tiempos.py CARPETA_DE_TRABAJO

Las pausas incluyen lo que tardó la persona en responder: las fechas no lo separan.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

IGNORAR = {"node_modules", ".hyperframes", "__pycache__", "_estudio"}
PAUSA_MIN_S = 60


def hora(t):
    return datetime.fromtimestamp(t).strftime("%H:%M:%S")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    base = Path(sys.argv[1])
    archivos = sorted((f.stat().st_mtime, f.relative_to(base).as_posix()) for f in base.rglob("*")
                      if f.is_file() and not set(f.relative_to(base).parts) & IGNORAR)
    if not archivos:
        sys.exit(f"No hay archivos en {base}")
    carpetas = {}
    for t, ruta in archivos:
        carpetas.setdefault(ruta.split("/")[0], []).append(t)
    informe = {
        "inicio": hora(archivos[0][0]),
        "fin": hora(archivos[-1][0]),
        "total_min": round((archivos[-1][0] - archivos[0][0]) / 60, 1),
        "carpetas": [{"carpeta": c, "desde": hora(l[0]), "hasta": hora(l[-1]), "min": round((l[-1] - l[0]) / 60, 1), "archivos": len(l)}
                     for c, l in sorted(carpetas.items(), key=lambda x: x[1][0])],
        "pausas": [{"min": round((b - a) / 60, 1), "desde": hora(a), "tras": ra, "antes_de": rb}
                   for (a, ra), (b, rb) in zip(archivos, archivos[1:]) if b - a > PAUSA_MIN_S],
    }
    print(json.dumps(informe, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
