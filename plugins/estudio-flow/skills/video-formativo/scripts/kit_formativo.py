"""Prepara el material que acompaña a un video formativo: subtítulos, capítulos y transcripción.

Uso:
    python kit_formativo.py 05-final/leccion.mp4 --guion 04-montaje/guion.txt
                            --linea 04-montaje/linea-de-tiempo.json [--destino 05-final]

Deja junto al video:
    <nombre>.srt                subtítulos para YouTube y la mayoría de plataformas
    <nombre>.vtt                subtítulos para sitios web y plataformas de cursos
    <nombre>-capitulos.txt      capítulos para pegar en la descripción de YouTube
    <nombre>-transcripcion.md   texto completo por capítulos, alternativa accesible al video

El texto sale del guion aprobado y los tiempos de la voz real, así que las palabras técnicas
quedan bien escritas. Necesita faster-whisper y sale con código 1 si algo no cumple.
"""
import argparse
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

from control_final import COINCIDENCIA_MIN, duracion, normalizar, palabras, vocabulario

CARACTERES_LINEA = 42
LINEAS_POR_SUBTITULO = 2
SUBTITULO_MIN_S = 1.0
SUBTITULO_MAX_S = 6.0
CARACTERES_POR_SEGUNDO = 17
CAPITULOS_MIN = 3
CAPITULO_MIN_S = 10


def alinear(escritas, oidas):
    """Da a cada palabra del guion el tiempo de la palabra oída que le corresponde.

    Las que no se reconocieron se reparten entre sus vecinas.
    """
    a = [normalizar(p) for p in escritas]
    b = [normalizar(p[0]) for p in oidas]
    tiempos = [None] * len(a)
    bloques = SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks()
    for bloque in bloques:
        for k in range(bloque.size):
            tiempos[bloque.a + k] = (oidas[bloque.b + k][1], oidas[bloque.b + k][2])
    conocidos = [i for i, x in enumerate(tiempos) if x]
    if not conocidos:
        sys.exit("La voz no se parece al guion: revisa que sean el mismo texto.")
    for i, x in enumerate(tiempos):
        if x:
            continue
        antes = max((j for j in conocidos if j < i), default=None)
        despues = min((j for j in conocidos if j > i), default=None)
        if antes is None:
            tiempos[i] = (tiempos[despues][0], tiempos[despues][0])
        elif despues is None:
            tiempos[i] = (tiempos[antes][1], tiempos[antes][1])
        else:
            hueco = tiempos[despues][0] - tiempos[antes][1]
            ini = tiempos[antes][1] + hueco * (i - antes) / (despues - antes)
            tiempos[i] = (ini, ini + hueco / (despues - antes))
    aciertos = sum(b.size for b in bloques) / max(1, len(a))
    return tiempos, aciertos


def agrupar(escritas, tiempos):
    """Parte el texto en subtítulos que se puedan leer: corta en puntuación y por largo."""
    limite = CARACTERES_LINEA * LINEAS_POR_SUBTITULO
    grupos, actual = [], []
    for i, palabra in enumerate(escritas):
        texto = " ".join(escritas[j] for j in actual + [i])
        if actual and (len(texto) > limite or tiempos[i][1] - tiempos[actual[0]][0] > SUBTITULO_MAX_S):
            grupos.append(actual)
            actual = []
        actual.append(i)
        if palabra[-1] in ".?!:" or (palabra[-1] in ",;" and len(" ".join(escritas[j] for j in actual)) > CARACTERES_LINEA * 0.7):
            grupos.append(actual)
            actual = []
    if actual:
        grupos.append(actual)
    return grupos


def repartir_lineas(texto):
    """Dos líneas parejas, cortando lo más cerca posible de la mitad."""
    if len(texto) <= CARACTERES_LINEA:
        return texto
    palabras_texto = texto.split()
    mejor = min(range(1, len(palabras_texto)),
                key=lambda k: abs(len(" ".join(palabras_texto[:k])) - len(" ".join(palabras_texto[k:]))))
    return " ".join(palabras_texto[:mejor]) + "\n" + " ".join(palabras_texto[mejor:])


def reloj(segundos, separador):
    ms = round(segundos * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{separador}{ms:03d}"


def subtitulos(grupos, escritas, tiempos, total):
    salida = []
    for n, grupo in enumerate(grupos):
        texto = " ".join(escritas[i] for i in grupo)
        ini = tiempos[grupo[0]][0]
        fin = max(tiempos[grupo[-1]][1], ini + SUBTITULO_MIN_S)
        siguiente = tiempos[grupos[n + 1][0]][0] if n + 1 < len(grupos) else total
        fin = min(fin + 0.15, siguiente - 0.02, total)
        salida.append((ini, fin, repartir_lineas(texto)))
    return salida


def escribir_srt(cues, ruta):
    bloques = [f"{n}\n{reloj(i, ',')} --> {reloj(f, ',')}\n{t}\n" for n, (i, f, t) in enumerate(cues, 1)]
    ruta.write_text("\n".join(bloques), encoding="utf-8")


def escribir_vtt(cues, ruta):
    bloques = [f"{reloj(i, '.')} --> {reloj(f, '.')}\n{t}\n" for i, f, t in cues]
    ruta.write_text("WEBVTT\n\n" + "\n".join(bloques), encoding="utf-8")


def marca_capitulo(segundos, con_horas):
    total = int(segundos)
    h, resto = divmod(total, 3600)
    m, s = divmod(resto, 60)
    return f"{h}:{m:02d}:{s:02d}" if con_horas else f"{m}:{s:02d}"


def revisar_capitulos(capitulos, total):
    """YouTube ignora todos los capítulos si uno solo incumple estas condiciones."""
    avisos = []
    if len(capitulos) < CAPITULOS_MIN:
        avisos.append(f"Hay {len(capitulos)} capítulos: YouTube pide al menos {CAPITULOS_MIN}")
    if capitulos and capitulos[0]["inicio"] != 0:
        avisos.append("El primer capítulo debe empezar en 0:00")
    for i, c in enumerate(capitulos):
        fin = capitulos[i + 1]["inicio"] if i + 1 < len(capitulos) else total
        if fin - c["inicio"] < CAPITULO_MIN_S:
            avisos.append(f"«{c['titulo']}» dura {fin - c['inicio']:.1f} s: cada capítulo debe durar al menos {CAPITULO_MIN_S} s")
    return avisos


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video", type=Path)
    p.add_argument("--guion", type=Path, required=True)
    p.add_argument("--linea", type=Path, required=True)
    p.add_argument("--destino", type=Path)
    a = p.parse_args()
    destino = a.destino or a.video.parent
    nombre = a.video.stem
    total = duracion(a.video)
    linea = json.loads(a.linea.read_text(encoding="utf-8"))
    guion = a.guion.read_text(encoding="utf-8")
    oidas, _ = palabras(a.video, vocabulario(guion))
    if not oidas:
        sys.exit("No se pudo transcribir la voz: instala faster-whisper y revisa que el video tenga narración.")
    escritas = guion.split()
    tiempos, aciertos = alinear(escritas, oidas)
    grupos = agrupar(escritas, tiempos)
    cues = subtitulos(grupos, escritas, tiempos, total)
    escribir_srt(cues, destino / f"{nombre}.srt")
    escribir_vtt(cues, destino / f"{nombre}.vtt")

    capitulos = linea["capitulos"]
    con_horas = total >= 3600
    (destino / f"{nombre}-capitulos.txt").write_text(
        "".join(f'{marca_capitulo(c["inicio"], con_horas)} {c["titulo"]}\n' for c in capitulos), encoding="utf-8")

    partes = [f"# Transcripción: {nombre}\n"]
    for i, c in enumerate(capitulos):
        fin = capitulos[i + 1]["inicio"] if i + 1 < len(capitulos) else total + 1
        frases = [t.replace("\n", " ") for ini, _, t in cues if c["inicio"] - 0.2 <= ini < fin - 0.2]
        partes.append(f'## {marca_capitulo(c["inicio"], con_horas)} {c["titulo"]}\n\n{" ".join(frases)}\n')
    (destino / f"{nombre}-transcripcion.md").write_text("\n".join(partes), encoding="utf-8")

    rapidos = [t.replace("\n", " ") for i, f, t in cues if len(t) / max(0.1, f - i) > CARACTERES_POR_SEGUNDO * 1.25]
    avisos = revisar_capitulos(capitulos, total)
    if rapidos:
        avisos.append(f"Subtítulos rápidos de leer: {len(rapidos)}. El primero: «{rapidos[0][:40]}»")
    informe = {"subtitulos": len(cues), "capitulos": len(capitulos), "coincidencia_guion": round(aciertos, 2), "avisos": avisos,
               "archivos": [f"{nombre}.srt", f"{nombre}.vtt", f"{nombre}-capitulos.txt", f"{nombre}-transcripcion.md"]}
    print(json.dumps(informe, ensure_ascii=False, indent=1))
    sys.exit(0 if aciertos >= COINCIDENCIA_MIN else 1)


if __name__ == "__main__":
    main()
