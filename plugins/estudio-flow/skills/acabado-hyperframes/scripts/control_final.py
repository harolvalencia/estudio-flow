"""Revisa un video antes de entregarlo y lo rechaza si no cumple el estándar.

Uso:
    python control_final.py VIDEO.mp4 [--cierre 4] [--sin-voz] [--pausa 1.5]

Comprueba:
  - Fotogramas negros y tramos congelados, con ffmpeg.
  - Silencios totales y sonoridad.
  - Voz de principio a fin y voz en el cierre, con faster-whisper.

Instala el transcriptor con: pip install faster-whisper
Imprime un JSON y sale con código 1 si algo falla.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

LUFS_MIN, LUFS_MAX = -18.0, -13.0
PICO_MAX = -0.5
INICIO_VOZ_MAX = 1.5


def ffmpeg_filtro(ruta, video=None, audio=None):
    args = ["ffmpeg", "-hide_banner", "-i", str(ruta)]
    if video:
        args += ["-vf", video]
    if audio:
        args += ["-af", audio]
    args += ["-f", "null", "-"]
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace").stderr


def duracion(ruta):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def tramos(texto, inicio, fin):
    a = [float(x) for x in re.findall(inicio + r"[:=]\s*(-?[\d.]+)", texto)]
    b = [float(x) for x in re.findall(fin + r"[:=]\s*(-?[\d.]+)", texto)]
    return [(round(x, 2), round(y, 2)) for x, y in zip(a, b)]


def palabras(ruta):
    """Palabras con tiempos, o None si no hay transcriptor instalado."""
    try:
        import numpy as np
        from faster_whisper import WhisperModel
    except ImportError:
        return None, ""
    crudo = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ruta), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                           capture_output=True, check=True).stdout
    audio = np.frombuffer(crudo, dtype=np.int16).astype(np.float32) / 32768.0
    modelo = WhisperModel("base", device="cpu", compute_type="int8")
    segmentos, _ = modelo.transcribe(audio, language="es", word_timestamps=True, vad_filter=False)
    lista, texto = [], []
    for s in segmentos:
        texto.append(s.text.strip())
        lista += [(w.start, w.end) for w in (s.words or [])]
    return lista, " ".join(texto)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video", type=Path)
    p.add_argument("--cierre", type=float, default=4.0, help="segundos finales donde debe haber voz")
    p.add_argument("--pausa", type=float, default=1.5, help="mayor pausa de voz permitida")
    p.add_argument("--sin-voz", action="store_true", help="la persona pidió expresamente una pieza sin voz")
    a = p.parse_args()
    if not a.video.exists():
        sys.exit(f"No existe {a.video}")

    total = duracion(a.video)
    fallos, avisos = [], []

    negro = tramos(ffmpeg_filtro(a.video, video="blackdetect=d=0.4:pix_th=0.06"), "black_start", "black_end")
    if negro:
        fallos.append(f"Fotogramas negros en {negro}")

    congelado = tramos(ffmpeg_filtro(a.video, video="freezedetect=n=-55dB:d=2.5"), "lavfi.freezedetect.freeze_start", "lavfi.freezedetect.freeze_end")
    medio = [t for t in congelado if t[1] < total - 2.2]
    if medio:
        fallos.append(f"Imagen congelada más de 2,5 s en {medio}")

    mudo = tramos(ffmpeg_filtro(a.video, audio="silencedetect=n=-45dB:d=0.7"), "silence_start", "silence_end")
    if mudo:
        fallos.append(f"Silencio total en {mudo}")

    medida = ffmpeg_filtro(a.video, audio="ebur128=peak=true")
    resumen = medida[medida.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", resumen)
    pico = re.search(r"Peak:\s+(-?[\d.]+) dBFS", resumen)
    lufs = float(i.group(1)) if i else None
    if lufs is None:
        fallos.append("El video no tiene audio medible")
    elif not LUFS_MIN <= lufs <= LUFS_MAX:
        fallos.append(f"Sonoridad de {lufs} LUFS, fuera de {LUFS_MIN} a {LUFS_MAX}")
    if pico and float(pico.group(1)) > PICO_MAX:
        fallos.append(f"Pico de {pico.group(1)} dBFS, demasiado alto")

    voz = {}
    if a.sin_voz:
        avisos.append("Revisión de voz omitida: pieza sin voz por pedido expreso")
    else:
        lista, texto = palabras(a.video)
        if lista is None:
            fallos.append("Falta faster-whisper: instálalo para comprobar la voz de punta a punta")
        elif not lista:
            fallos.append("No se detectó voz en el video")
        else:
            huecos = [(round(x[1], 2), round(y[0], 2)) for x, y in zip(lista, lista[1:]) if y[0] - x[1] > a.pausa]
            cola = round(total - lista[-1][1], 2)
            cubierto = sum(e - s for s, e in lista) / total
            voz = {"primera_palabra_s": round(lista[0][0], 2), "ultima_palabra_s": round(lista[-1][1], 2),
                   "palabras": len(lista), "cobertura": round(cubierto, 2), "pausas_largas": huecos, "transcripcion": texto}
            if lista[0][0] > INICIO_VOZ_MAX:
                fallos.append(f"La voz arranca tarde, en {lista[0][0]:.1f} s")
            if huecos:
                fallos.append(f"Tramos sin voz de más de {a.pausa} s: {huecos}")
            if cola > a.cierre:
                fallos.append(f"La voz termina {cola} s antes del final: el cierre debe ser hablado")

    informe = {"video": a.video.name, "duracion_s": round(total, 2), "lufs": lufs, "voz": voz,
               "aprobado": not fallos, "fallos": fallos, "avisos": avisos}
    print(json.dumps(informe, ensure_ascii=False, indent=2))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
