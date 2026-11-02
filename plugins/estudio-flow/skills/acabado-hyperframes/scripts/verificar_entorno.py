"""Revisa qué hay disponible para montar y renderizar, y lo imprime en JSON.

Uso:
    python verificar_entorno.py [CARPETA_DE_TRABAJO]

No instala nada. Si falta algo, `faltantes` dice qué y `siguiente` qué hacer.
"""
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

NODE_MINIMO = 22


def correr(args, tiempo=60):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=tiempo,
                           shell=platform.system() == "Windows")
        return (r.stdout + r.stderr).strip()
    except (OSError, subprocess.SubprocessError):
        return ""


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


def main():
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    node = correr(["node", "-v"])
    version_node = int(re.search(r"v(\d+)", node).group(1)) if re.search(r"v(\d+)", node) else 0
    ffmpeg = correr(["ffmpeg", "-version"]).splitlines()
    libres = shutil.disk_usage(carpeta if carpeta.exists() else Path.cwd()).free / 1e9
    modulos = {}
    for m in ("numpy", "PIL", "faster_whisper"):
        try:
            __import__(m)
            modulos[m] = True
        except ImportError:
            modulos[m] = False
    info = {
        "sistema": platform.system(),
        "ruta": "windows" if platform.system() == "Windows" else "cowork",
        "python": platform.python_version(),
        "node": node or None,
        "ffmpeg": ffmpeg[0].split(" Copyright")[0] if ffmpeg else None,
        "hyperframes": correr(["npx", "--yes", "hyperframes", "--version"], 120).splitlines()[-1:] or None,
        "chrome": buscar_chrome() or None,
        "modulos_python": modulos,
        "disco_libre_gb": round(libres, 1),
    }
    faltantes, siguiente = [], []
    if version_node < NODE_MINIMO:
        faltantes.append(f"Node {NODE_MINIMO} o superior")
        siguiente.append("Instala Node desde nodejs.org o usa Desktop Commander para trabajar en Windows.")
    if not info["ffmpeg"]:
        faltantes.append("ffmpeg")
        siguiente.append("Instala ffmpeg o usa Desktop Commander para trabajar en Windows.")
    if not info["chrome"]:
        faltantes.append("navegador para render")
        siguiente.append("Ejecuta: npx hyperframes browser ensure")
    if not modulos["numpy"]:
        faltantes.append("numpy")
        siguiente.append("Ejecuta: pip install numpy")
    if not modulos["PIL"]:
        faltantes.append("Pillow")
        siguiente.append("Ejecuta: pip install pillow")
    if not modulos["faster_whisper"]:
        faltantes.append("faster-whisper")
        siguiente.append("Ejecuta: pip install faster-whisper")
    if libres < 5:
        faltantes.append("espacio en disco (mínimo 5 GB)")
        siguiente.append("Libera espacio: el render guarda fotogramas temporales.")
    info["listo"] = not faltantes
    info["faltantes"] = faltantes
    info["siguiente"] = siguiente
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
