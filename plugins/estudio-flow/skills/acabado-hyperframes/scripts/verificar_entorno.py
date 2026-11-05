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
# Homebrew no deja instalar paquetes en su Python: en Mac van a este entorno, que crean las guías
ENTORNO_MAC = Path.home() / ".estudio-flow" / "bin" / "python3"
PAQUETES = {"numpy": "numpy", "PIL": "pillow", "faster_whisper": "faster-whisper"}


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
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome") or "",
        shutil.which("chromium") or "",
        shutil.which("chromium-browser") or "",
    ]
    return next((c for c in candidatos if c and Path(c).exists()), "")


def comando_python():
    """En Mac y Linux no existe `python`: el comando es `python3` o el del entorno de Mac."""
    if platform.system() == "Windows":
        return "python"
    return str(ENTORNO_MAC) if ENTORNO_MAC.exists() else "python3"


def comando_instalar(paquetes):
    if platform.system() == "Windows":
        return f"python -m pip install {paquetes}"
    if platform.system() != "Darwin":
        return f"python3 -m pip install {paquetes}"
    if ENTORNO_MAC.exists():
        return f"{ENTORNO_MAC} -m pip install {paquetes}"
    return f"brew install python@3.13 && python3.13 -m venv ~/.estudio-flow && ~/.estudio-flow/bin/pip install {paquetes}"


def main():
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    node = correr(["node", "-v"])
    version_node = int(re.search(r"v(\d+)", node).group(1)) if re.search(r"v(\d+)", node) else 0
    ffmpeg = correr(["ffmpeg", "-version"]).splitlines()
    libres = shutil.disk_usage(carpeta if carpeta.exists() else Path.cwd()).free / 1e9
    # En Mac, los paquetes se buscan en su entorno aunque este script corra con otro Python
    interprete = str(ENTORNO_MAC) if ENTORNO_MAC.exists() else sys.executable
    modulos = {m: subprocess.run([interprete, "-c", f"import {m}"], capture_output=True).returncode == 0 for m in PAQUETES}
    info = {
        "sistema": platform.system(),
        "ruta": {"Windows": "windows", "Darwin": "mac"}.get(platform.system(), "cowork"),
        "comando_python": comando_python(),
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
        siguiente.append("Instala Node desde nodejs.org o usa Desktop Commander para trabajar en tu computador.")
    if not info["ffmpeg"]:
        faltantes.append("ffmpeg")
        siguiente.append("Instala ffmpeg o usa Desktop Commander para trabajar en tu computador.")
    if not info["chrome"]:
        faltantes.append("navegador para render")
        siguiente.append("Ejecuta: npx hyperframes browser ensure")
    sin_instalar = [p for m, p in PAQUETES.items() if not modulos[m]]
    if sin_instalar:
        faltantes += sin_instalar
        siguiente.append("Ejecuta: " + comando_instalar(" ".join(sin_instalar)))
    if libres < 5:
        faltantes.append("espacio en disco (mínimo 5 GB)")
        siguiente.append("Libera espacio: el render guarda fotogramas temporales.")
    if info["ruta"] == "cowork":
        siguiente.append("Usa Desktop Commander si está disponible: esta terminal no llega al modelo de voz y sus comandos pueden pedir aprobación.")
    info["listo"] = not faltantes
    info["faltantes"] = faltantes
    info["siguiente"] = siguiente
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
