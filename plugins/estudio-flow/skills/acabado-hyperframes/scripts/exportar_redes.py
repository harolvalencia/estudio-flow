"""Convierte el video maestro en los archivos finales para redes.

Uso:
    python exportar_redes.py MAESTRO.mp4 --nombre reel --destino 05-final [--liviana] [--lufs -16]
                             [--portada 1.0] [--sufijo 9x16]

Deja en DESTINO:
    <nombre>-<sufijo>.mp4           H.264, yuv420p, AAC 48 kHz, audio normalizado, faststart
    <nombre>-<sufijo>-liviano.mp4   con --liviana; recodifica el video y copia el audio
    <nombre>-<sufijo>-portada.jpg   fotograma en el segundo indicado

Imprime en JSON lo entregado, medido sobre los archivos reales.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PICO_DBTP = -1.0


def correr(args):
    return subprocess.run(args, capture_output=True, text=True)


def sondear(ruta):
    r = correr(["ffprobe", "-v", "error", "-show_entries",
                "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt",
                "-of", "json", str(ruta)])
    datos = json.loads(r.stdout)
    video = next(s for s in datos["streams"] if s["codec_type"] == "video")
    audio = next((s for s in datos["streams"] if s["codec_type"] == "audio"), None)
    num, den = map(int, video["r_frame_rate"].split("/"))
    return {"archivo": ruta.name, "resolucion": f'{video["width"]}x{video["height"]}',
            "fps": round(num / den, 2), "codec": video["codec_name"], "pixel": video["pix_fmt"],
            "audio": audio["codec_name"] if audio else None,
            "duracion_s": round(float(datos["format"]["duration"]), 2),
            "peso_mb": round(int(datos["format"]["size"]) / 1e6, 1)}


def medir_audio(ruta, lufs):
    """Primera pasada de loudnorm: sus medidas hacen exacta la segunda."""
    filtro = f"loudnorm=I={lufs}:TP={PICO_DBTP}:LRA=11:print_format=json"
    err = correr(["ffmpeg", "-hide_banner", "-i", str(ruta), "-af", filtro, "-f", "null", "-"]).stderr
    bloques = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", err)
    if not bloques:
        sys.exit("ffmpeg no entregó la medición de sonoridad:\n" + err[-600:])
    return json.loads(bloques[-1])


def tiene_audio(ruta):
    return sondear(ruta)["audio"] is not None


def exportar_maestro(maestro, salida, lufs):
    args = ["ffmpeg", "-v", "error", "-y", "-i", str(maestro), "-map", "0:v:0"]
    if tiene_audio(maestro):
        m = medir_audio(maestro, lufs)
        filtro = (f"loudnorm=I={lufs}:TP={PICO_DBTP}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                  f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                  f"offset={m['target_offset']}:linear=true,aresample=48000")
        args += ["-map", "0:a:0", "-af", filtro, "-c:a", "aac", "-b:a", "192k"]
    args += ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(salida)]
    subprocess.run(args, check=True)


def exportar_liviana(origen, salida):
    args = ["ffmpeg", "-v", "error", "-y", "-i", str(origen), "-c:v", "libx264", "-preset", "slow",
            "-crf", "26", "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "copy",
            "-movflags", "+faststart", str(salida)]
    subprocess.run(args, check=True)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("maestro", type=Path)
    p.add_argument("--nombre", required=True)
    p.add_argument("--destino", type=Path, default=Path("05-final"))
    p.add_argument("--sufijo", default="9x16")
    p.add_argument("--lufs", type=float, default=-16.0)
    p.add_argument("--liviana", action="store_true")
    p.add_argument("--portada", type=float, default=1.0, help="segundo del que sale la portada")
    a = p.parse_args()
    if not a.maestro.exists():
        sys.exit(f"No existe {a.maestro}")
    a.destino.mkdir(parents=True, exist_ok=True)
    base = f"{a.nombre}-{a.sufijo}"
    principal = a.destino / f"{base}.mp4"
    exportar_maestro(a.maestro, principal, a.lufs)
    entregables = [principal]
    if a.liviana:
        liviano = a.destino / f"{base}-liviano.mp4"
        exportar_liviana(principal, liviano)
        entregables.append(liviano)
    portada = a.destino / f"{base}-portada.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.portada), "-i", str(principal),
                    "-frames:v", "1", "-q:v", "2", str(portada)], check=True)
    print(json.dumps({"entregables": [sondear(e) for e in entregables], "portada": portada.name},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
