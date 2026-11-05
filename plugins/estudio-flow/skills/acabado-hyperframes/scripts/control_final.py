"""Revisa un video antes de entregarlo y lo rechaza si no cumple el estándar.

Uso:
    python control_final.py VIDEO.mp4 [--tipo promocional|formativo] [--cierre 4]
                            [--pausa N] [--guion guion.txt] [--sin-voz]

Comprueba:
  - Fotogramas negros y tramos congelados, con ffmpeg.
  - Silencios totales y sonoridad.
  - Voz de principio a fin y voz en el cierre, con faster-whisper.
  - Con --guion, que la voz diga lo que dice el guion aprobado.

El tipo formativo admite pausas para mirar la pantalla y más tiempo sobre un mismo cuadro.
Para instalar el transcriptor, sigue lo que indica verificar_entorno.py.
Imprime un JSON y sale con código 1 si algo falla.
"""
import argparse
import json
import re
import subprocess
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

LUFS_MIN, LUFS_MAX = -18.0, -13.0
PICO_MAX = -0.5
INICIO_VOZ_MAX = 1.5
COINCIDENCIA_MIN = 0.85
VOCABULARIO_MAX = 60
LECCION_MAX_S = 360
PERFILES = {
    "promocional": {"pausa": 1.5, "congelado": 2.5, "silencio": 0.7},
    "formativo": {"pausa": 3.5, "congelado": 8.0, "silencio": 2.5},
}


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


def normalizar(palabra):
    """Minúsculas, sin tildes ni puntuación: así se comparan guion y transcripción."""
    return "".join(c for c in unicodedata.normalize("NFD", palabra.lower()) if c.isalnum())


def coincidencia(guion, lista):
    a = [n for n in map(normalizar, guion.split()) if n]
    b = [n for n in (normalizar(p[0]) for p in lista) if n]
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def vocabulario(guion):
    """Palabras largas del guion, para que el transcriptor no confunda términos técnicos."""
    limpias = [p.strip(".,;:¿?¡!«»()") for p in guion.split()]
    return " ".join(list(dict.fromkeys(p for p in limpias if len(p) >= 5))[:VOCABULARIO_MAX])


def palabras(ruta, pistas=None):
    """Lista de (palabra, inicio, fin), o None si falta el transcriptor o su modelo."""
    try:
        import numpy as np
        from faster_whisper import WhisperModel
    except ImportError:
        return None, ""
    crudo = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ruta), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                           capture_output=True, check=True).stdout
    audio = np.frombuffer(crudo, dtype=np.int16).astype(np.float32) / 32768.0
    try:
        modelo = WhisperModel("base", device="cpu", compute_type="int8")
    except Exception:  # El modelo viene de Hugging Face, y la terminal de la sesión no llega allí
        return None, ""
    # Sin filtro de voz, las pistas hacen que repita frases en los silencios y esconda un final mudo
    segmentos, _ = modelo.transcribe(audio, language="es", word_timestamps=True, vad_filter=True,
                                     vad_parameters={"min_silence_duration_ms": 300, "speech_pad_ms": 120}, hotwords=pistas)
    lista, texto = [], []
    for s in segmentos:
        texto.append(s.text.strip())
        lista += [(w.word.strip(), w.start, w.end) for w in (s.words or [])]
    return lista, " ".join(texto)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video", type=Path)
    p.add_argument("--tipo", choices=PERFILES, default="promocional", help="promocional o formativo")
    p.add_argument("--cierre", type=float, default=4.0, help="segundos finales donde debe haber voz")
    p.add_argument("--pausa", type=float, help="mayor pausa de voz permitida; por defecto la del tipo")
    p.add_argument("--guion", type=Path, help="texto aprobado que la voz debe decir")
    p.add_argument("--sin-voz", action="store_true", help="la persona pidió expresamente una pieza sin voz")
    a = p.parse_args()
    if not a.video.exists():
        sys.exit(f"No existe {a.video}")
    perfil = PERFILES[a.tipo]
    pausa = a.pausa if a.pausa is not None else perfil["pausa"]

    total = duracion(a.video)
    fallos, avisos = [], []
    if a.tipo == "formativo" and total > LECCION_MAX_S:
        avisos.append(f"Dura {total / 60:.1f} min: considera dividirlo en lecciones más cortas")

    negro = tramos(ffmpeg_filtro(a.video, video="blackdetect=d=0.4:pix_th=0.06"), "black_start", "black_end")
    if negro:
        fallos.append(f"Fotogramas negros en {negro}")

    congelado = tramos(ffmpeg_filtro(a.video, video=f"freezedetect=n=-55dB:d={perfil['congelado']}"), "lavfi.freezedetect.freeze_start", "lavfi.freezedetect.freeze_end")
    medio = [t for t in congelado if t[1] < total - 2.2]
    if medio:
        fallos.append(f"Imagen congelada más de {perfil['congelado']} s en {medio}")

    mudo = tramos(ffmpeg_filtro(a.video, audio=f"silencedetect=n=-45dB:d={perfil['silencio']}"), "silence_start", "silence_end")
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
        guion = a.guion.read_text(encoding="utf-8") if a.guion else ""
        lista, texto = palabras(a.video, vocabulario(guion) or None)
        if lista is None:
            fallos.append("Voz sin comprobar: falta faster-whisper o su modelo. No lo busques en otras fuentes: sigue «Si falta el transcriptor» en la skill acabado-hyperframes")
        elif not lista:
            fallos.append("No se detectó voz en el video")
        else:
            huecos = [(round(x[2], 2), round(y[1], 2)) for x, y in zip(lista, lista[1:]) if y[1] - x[2] > pausa]
            cola = round(total - lista[-1][2], 2)
            cubierto = sum(e - s for _, s, e in lista) / total
            voz = {"primera_palabra_s": round(lista[0][1], 2), "ultima_palabra_s": round(lista[-1][2], 2),
                   "palabras": len(lista), "cobertura": round(cubierto, 2), "pausas_largas": huecos, "transcripcion": texto}
            if lista[0][1] > INICIO_VOZ_MAX:
                fallos.append(f"La voz arranca tarde, en {lista[0][1]:.1f} s")
            if huecos:
                fallos.append(f"Tramos sin voz de más de {pausa} s: {huecos}")
            if cola > a.cierre:
                fallos.append(f"La voz termina {cola} s antes del final: el cierre debe ser hablado")
            if guion:
                parecido = coincidencia(guion, lista)
                voz["coincidencia_guion"] = round(parecido, 2)
                if parecido < COINCIDENCIA_MIN:
                    fallos.append(f"La voz no sigue el guion: coincidencia de {parecido:.0%}")

    informe = {"video": a.video.name, "tipo": a.tipo, "duracion_s": round(total, 2), "lufs": lufs, "voz": voz,
               "aprobado": not fallos, "fallos": fallos, "avisos": avisos}
    print(json.dumps(informe, ensure_ascii=False, indent=2))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
