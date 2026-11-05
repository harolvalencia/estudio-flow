"""Mide un video de referencia para entender cómo está hecho: ritmo, gancho, voz y cierre.

Uso:
    python analizar_referencia.py "01-referencias/video.mp4" --salida 01-referencias/referente

Deja en la carpeta de salida:
    medidas.json        duración, formato, cortes, duración de cada plano, voz y sonoridad
    hoja-inicio.jpg     los primeros 3 s, cada medio segundo: ahí se decide el gancho
    hoja-planos.jpg     un cuadro por plano, y varios en los planos largos, hasta 24
    hoja-final.jpg      los últimos 3 s: cómo cierra y a qué invita

Son medidas, no conclusiones: no dicen por qué funcionó un video. Los cortes duros se detectan bien; una
transición con destello o fundido puede no contarse o contarse doble, así que mira la hoja. La interpretación
sigue references/analisis-de-referencia.md. Sin el transcriptor sigue sin la voz y lo avisa.
Necesita ffmpeg, numpy y Pillow.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from statistics import median

from control_final import cortes, duracion, ffmpeg_filtro, hoja, palabras

INICIO_S = 3.0
FINAL_S = 3.0
PASO_S = 0.5
PLANOS_MAX = 24
PLANO_LARGO_S = 4.0


def formato(ruta):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(ruta)],
                       capture_output=True, text=True)
    ancho, alto = (int(x) for x in r.stdout.strip().split(",")[:2])
    tipo = "vertical" if alto > ancho * 1.1 else "horizontal" if ancho > alto * 1.1 else "cuadrado"
    return {"ancho": ancho, "alto": alto, "tipo": tipo}


def sonoridad(ruta, desde=None, hasta=None):
    args = ["ffmpeg", "-hide_banner"] + (["-ss", f"{desde:.2f}", "-to", f"{hasta:.2f}"] if desde is not None else [])
    err = subprocess.run([*args, "-i", str(ruta), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", err[err.rfind("Summary:"):])
    return float(m.group(1)) if m else None


def medir_planos(lista_cortes, total):
    bordes = [0.0, *lista_cortes, total]
    duraciones = [round(b - a, 2) for a, b in zip(bordes, bordes[1:]) if b - a > 0]
    return {"cantidad": len(duraciones), "promedio_s": round(sum(duraciones) / len(duraciones), 2), "mediana_s": round(median(duraciones), 2),
            "mas_corto_s": min(duraciones), "mas_largo_s": max(duraciones), "primer_corte_s": lista_cortes[0] if lista_cortes else None,
            "cortes_cada_10_s": round(len(lista_cortes) / total * 10, 1), "duraciones_s": duraciones}


def medir_voz(lista, texto, total):
    if lista is None:
        return {"estado": "sin comprobar: falta el transcriptor o su modelo. Sigue sin la voz y dilo en el análisis"}
    if not lista:
        return {"estado": "no se detectó voz: puede ser solo música o texto"}
    hablado = sum(fin - ini for _, ini, fin in lista)
    huecos = [round(b[1] - a[2], 2) for a, b in zip(lista, lista[1:])]
    primeras = [p for p, ini, _ in lista if ini < INICIO_S]
    cierre = [p for p, ini, _ in lista if ini >= total - 2 * FINAL_S]
    return {"estado": "transcrita", "primera_palabra_s": round(lista[0][1], 2), "ultima_palabra_s": round(lista[-1][2], 2), "palabras": len(lista),
            "palabras_por_segundo": round(len(lista) / max(0.1, lista[-1][2] - lista[0][1]), 2), "cobertura": round(hablado / total, 2),
            "pausa_mayor_s": max(huecos, default=0), "primeros_3_s": " ".join(primeras), "ultimos_6_s": " ".join(cierre), "transcripcion": texto}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video", type=Path)
    p.add_argument("--salida", type=Path, required=True)
    p.add_argument("--idioma", help="código como es o en; por defecto se detecta")
    p.add_argument("--sin-voz", action="store_true", help="no transcribir")
    a = p.parse_args()
    if not a.video.exists():
        sys.exit(f"No existe {a.video}")
    a.salida.mkdir(parents=True, exist_ok=True)
    total = duracion(a.video)
    lista_cortes = cortes(a.video)
    planos = medir_planos(lista_cortes, total)
    bordes = [0.0, *lista_cortes, total]
    centros = []
    for x, y in zip(bordes, bordes[1:]):
        # Una transición con destello o fundido puede no contar como corte: un plano largo se muestra varias veces
        veces = max(1, round((y - x) / PLANO_LARGO_S))
        centros += [round(x + (y - x) * (i + 0.5) / veces, 2) for i in range(veces)]
    if len(centros) > PLANOS_MAX:
        salto = len(centros) / PLANOS_MAX
        centros = [centros[int(i * salto)] for i in range(PLANOS_MAX)]
    pasos_inicio = [round(i * PASO_S, 2) for i in range(int(min(INICIO_S, total) / PASO_S))]
    desde_final = max(0.0, total - FINAL_S - 0.1)
    pasos_final = [round(desde_final + i * PASO_S, 2) for i in range(int(FINAL_S / PASO_S))]
    hojas = {"inicio": hoja(a.video, a.salida / "hoja-inicio.jpg", pasos_inicio), "planos": hoja(a.video, a.salida / "hoja-planos.jpg", centros),
             "final": hoja(a.video, a.salida / "hoja-final.jpg", pasos_final)}
    lista, texto = (None, "") if a.sin_voz else palabras(a.video, None, a.idioma)
    volumen = sonoridad(a.video)
    medidas = {"video": a.video.name, "duracion_s": round(total, 2), "formato": formato(a.video), "cortes_s": lista_cortes, "planos": planos,
               "voz": medir_voz(lista, texto, total),
               "sonido": {"lufs": volumen, "lufs_primeros_3_s": sonoridad(a.video, 0, min(INICIO_S, total)), "lufs_ultimos_3_s": sonoridad(a.video, desde_final, total),
                          "silencios_s": re.findall(r"silence_start:\s*(-?[\d.]+)", ffmpeg_filtro(a.video, audio="silencedetect=n=-45dB:d=0.7"))},
               "hojas": hojas}
    (a.salida / "medidas.json").write_text(json.dumps(medidas, ensure_ascii=False, indent=1), encoding="utf-8")
    resumen = {k: medidas[k] for k in ("video", "duracion_s", "formato", "sonido")}
    resumen["planos"] = {k: v for k, v in planos.items() if k != "duraciones_s"}
    resumen["voz"] = {k: v for k, v in medidas["voz"].items() if k != "transcripcion"}
    resumen["archivos"] = str(a.salida)
    print(json.dumps(resumen, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
