"""Une la voz de los clips de Flow en una sola narración y mide cada tramo.

Uso:
    python narracion_desde_clips.py 03-flow/voz --salida 04-montaje/assets/audio/voz.wav
                                    --tiempos 04-montaje/tiempos.json --guion 04-montaje/tutorial.json
                                    [--pausa 0.35]

Toma los clips numerados de la carpeta (01.mp4, 02.mp4...), recorta el silencio de cada uno,
los iguala a -18 LUFS y deja un solo WAV con una pausa corta entre tramos. En tiempos.json
queda dónde empieza cada tramo y, con faster-whisper, cuándo se dice cada palabra: de ahí
sale que la pantalla señale un botón justo cuando la voz lo nombra.

Solo necesita ffmpeg. Sin faster-whisper funciona, pero sin tiempos por palabra.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

LUFS_TRAMO = -18.0
UMBRAL_DB = -38
MARGEN_S = 0.06
SR = 48000


def ffmpeg_stderr(args):
    return subprocess.run(["ffmpeg", "-hide_banner", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stderr


def duracion_audio(ruta):
    """Largo real de la pista de audio: el contenedor puede durar más que ella."""
    crudo = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ruta), "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                           capture_output=True, check=True).stdout
    return len(crudo) / 16000


def limites_de_voz(ruta):
    """Primer y último instante con sonido: Flow deja silencio al empezar y al terminar."""
    total = duracion_audio(ruta)
    err = ffmpeg_stderr(["-i", str(ruta), "-vn", "-af", f"silencedetect=n={UMBRAL_DB}dB:d=0.12", "-f", "null", "-"])
    inicios = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d.]+)", err)]
    finales = [float(x) for x in re.findall(r"silence_end:\s*(-?[\d.]+)", err)]
    desde, hasta = 0.0, total
    if inicios and inicios[0] <= 0.05 and finales:
        desde = finales[0]
    if len(inicios) > len(finales) or (inicios and finales and finales[-1] >= total - 0.05):
        hasta = inicios[-1]
    return max(0.0, desde - MARGEN_S), min(total, hasta + MARGEN_S)


def sonoridad(ruta, desde, hasta):
    err = ffmpeg_stderr(["-ss", str(desde), "-to", str(hasta), "-i", str(ruta), "-af", "ebur128", "-f", "null", "-"])
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", err[err.rfind("Summary:"):])
    return float(m.group(1)) if m else LUFS_TRAMO


def texto_del_guion(ruta):
    """Acepta tutorial.json, con su lista `guion`, o un archivo de texto."""
    if not ruta:
        return ""
    contenido = ruta.read_text(encoding="utf-8")
    return " ".join(json.loads(contenido)["guion"]) if ruta.suffix == ".json" else contenido


def transcribir(ruta, guion):
    """Palabras con tiempos, si el control final y su transcriptor están disponibles."""
    try:
        from control_final import palabras, vocabulario
    except ImportError:
        return []
    lista, _ = palabras(ruta, vocabulario(guion) or None)
    return lista or []


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("carpeta", type=Path)
    p.add_argument("--salida", type=Path, required=True)
    p.add_argument("--tiempos", type=Path, required=True)
    p.add_argument("--guion", type=Path, help="tutorial.json o texto, para reconocer bien los términos técnicos")
    p.add_argument("--pausa", type=float, default=0.35, help="silencio entre tramos, en segundos")
    a = p.parse_args()
    clips = sorted((c for c in a.carpeta.glob("*.mp4") if re.fullmatch(r"\d+", c.stem)), key=lambda c: int(c.stem))
    if not clips:
        sys.exit(f"No hay clips numerados en {a.carpeta}")
    a.salida.parent.mkdir(parents=True, exist_ok=True)
    a.tiempos.parent.mkdir(parents=True, exist_ok=True)

    tramos, partes, cursor = [], [], 0.0
    with tempfile.TemporaryDirectory() as tmp:
        for n, clip in enumerate(clips, 1):
            desde, hasta = limites_de_voz(clip)
            ganancia = LUFS_TRAMO - sonoridad(clip, desde, hasta)
            parte = Path(tmp) / f"{n:03d}.wav"
            fin_pausa = hasta - desde + a.pausa
            filtro = (f"atrim={desde:.3f}:{hasta:.3f},asetpts=PTS-STARTPTS,aformat=sample_rates={SR}:channel_layouts=mono,"
                      f"volume={ganancia:.2f}dB,afade=t=in:d=0.015,afade=t=out:st={hasta - desde - 0.03:.3f}:d=0.03,"
                      f"apad=whole_dur={fin_pausa:.3f}")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-af", filtro, str(parte)], check=True)
            partes.append(parte)
            tramos.append({"n": n, "clip": clip.name, "desde": round(desde, 3), "hasta": round(hasta, 3),
                           "inicio": round(cursor, 3), "duracion": round(fin_pausa, 3), "voz_s": round(hasta - desde, 3),
                           "palabras": []})
            cursor += fin_pausa
        lista = Path(tmp) / "lista.txt"
        lista.write_text("".join(f"file '{x.as_posix()}'\n" for x in partes), encoding="utf-8")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                        "-c:a", "pcm_s16le", str(a.salida)], check=True)

    for palabra, inicio, fin in transcribir(a.salida, texto_del_guion(a.guion)):
        tramo = next((t for t in reversed(tramos) if inicio >= t["inicio"] - 0.05), tramos[0])
        tramo["palabras"].append({"p": palabra, "t": round(max(0.0, inicio - tramo["inicio"]), 3), "fin": round(fin - tramo["inicio"], 3)})
    a.tiempos.write_text(json.dumps({"total": round(cursor, 3), "tramos": tramos}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"tramos": len(tramos), "total_s": round(cursor, 2),
                      "palabras": sum(len(t["palabras"]) for t in tramos)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
