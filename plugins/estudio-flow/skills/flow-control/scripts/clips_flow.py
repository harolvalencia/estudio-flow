"""Prepara los prompts de Flow antes de gastar puntos y revisa cada toma después de bajarla.

Uso:
    python clips_flow.py preparar 03-flow/clips.json [--ritmo 1.93] [--clip 01]
    python clips_flow.py revisar 03-flow/01.mp4 --clips 03-flow/clips.json --id 01
    python clips_flow.py revisar 03-flow/01.mp4 --frase "Lo que debía decir"

preparar calcula la duración de cada clip, su ventana de habla y sus puntos, y deja los prompts en
prompts.json, junto a clips.json. Si un prompt repite un error conocido, no deja nada y sale con código 1.
revisar compara la voz con el guion, busca palabras repetidas y cortes, mide el ritmo y deja una hoja de
fotogramas. Su veredicto es aprobar, reparar, regenerar, dudoso o «sin comprobar», y sale con código 0 solo
si es aprobar. No distingue un tartamudeo muy corto ni ve manos o caras: la hoja se mira siempre. El formato
de clips.json está en references/prompts-omni.md.

Omni rellena la ventana de habla repitiendo palabras si le sobra tiempo. Por eso la duración del clip se
calcula con el ritmo real de la voz y la ventana con uno 16 % más rápido. Sin medir, se usa el de techo.
"""
import argparse
import json
import math
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

RITMO_TECHO = 1.9
RELACION_VENTANA = 2.2 / 1.9
INICIO_S = 0.3
COLA_S = 0.6
DURACIONES = (4, 6, 8, 10)
COSTO = {"360p": {4: 4, 6: 5, 8: 6, 10: 7}, "720p": {4: 7, 6: 10, 8: 12, 10: 15}}
MARGEN = 1.3
CLASES = ("camara", "off", "muda", "narracion")
COINCIDENCIA_APROBAR = 0.85
COINCIDENCIA_REGENERAR = 0.6
SONIDO_TRAS_FRASE_S = 0.5
FINAL_VOZ_MAX_S = 0.8
HOJA_CADA_S = 0.5
NUMEROS = {"cero": 0, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
           "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15, "dieciseis": 16, "diecisiete": 17, "dieciocho": 18,
           "diecinueve": 19, "veinte": 20, "veintiuno": 21, "veintidos": 22, "veintitres": 23, "veinticuatro": 24, "veinticinco": 25,
           "veintiseis": 26, "veintisiete": 27, "veintiocho": 28, "veintinueve": 29, "treinta": 30, "cuarenta": 40, "cincuenta": 50,
           "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90, "cien": 100, "ciento": 100, "doscientos": 200, "trescientos": 300,
           "cuatrocientos": 400, "quinientos": 500, "seiscientos": 600, "setecientos": 700, "ochocientos": 800, "novecientos": 900}

AUDIO_BASE = "only the voice and soft ambience, no music"
EVITAR_BASE = ("cuts, new camera angles, a different location, extra people, objects appearing out of nowhere, objects changing "
               "hands, extra or different dialogue, repeated words, filler words, talking after the sentence, subtitles, "
               "on-screen text, extra logos, blur")
REGLA_DIALOGO = ("say only the sentence in script, exactly once and word for word, at a natural pace; "
                 "never repeat or add a word; stay silent after it")

MOVIMIENTO = re.compile(r"\b(pans?|panning|zooms?|zooming|dolly|tilts?|orbits?|tracking|push[- ]?in|pull[- ]?(back|out)|crane|whip|"
                        r"handheld|paneo|acercamiento|alejar)\b|camera (moves|turns|rotates|follows)", re.I)
# En una acción, «tilts her head» no mueve la cámara: ahí solo cuenta si la nombra
MOVIMIENTO_EN_ACCION = re.compile(r"\bcamera\b.*\b(moves?|turns?|rotates?|follows?|pans?|tilts?|zooms?|pushes|pulls)\b|\bzoom", re.I)
TEXTO_EN_IMAGEN = re.compile(r"\b(text|titles?|captions?|subtitles?|logos?|signage|letters|letreros?|texto|t[ií]tulos?|subt[ií]tulos?)\b", re.I)
# «illumination» no va en la lista: «global illumination» es una técnica de luz
ESTUDIOS = re.compile(r"\b(pixar|disney|dreamworks|ghibli|marvel|minions?|shrek|mickey|nintendo|pok[eé]mon|"
                      r"looney|simpsons?|peppa)\b", re.I)
DOS_OBJETOS = re.compile(r"\bhold(s|ing)?\b.*\b(and|y)\s+(a|an|the|un|una)\b", re.I)
LUZ = re.compile(r"light|glow|lumin|backlit|sunlit|neon|\bluz\b|contraluz", re.I)
PROFUNDIDAD = re.compile(r"depth|layer|foreground|background|bokeh|volumetric|wide|macro|scale|epic|cinematic|"
                         r"profundidad|escala|[ée]pic|cinematogr", re.I)


def contar(linea):
    return len(re.findall(r"\w+", linea or ""))


def tiempos(linea, ritmo=RITMO_TECHO):
    """Duración del clip y segundo en que debe terminar de hablar. La duración es None si la frase no cabe."""
    n = contar(linea)
    fin_real = INICIO_S + n / ritmo
    fin_habla = round(INICIO_S + n / (ritmo * RELACION_VENTANA), 1)
    return next((d for d in DURACIONES if fin_real + COLA_S <= d), None), fin_habla


def afirmaciones(texto):
    """Quita las frases negadas: «no pan, no zoom» no pide mover la cámara."""
    partes = re.split(r"[,;.]", texto or "")
    return " ".join(p for p in partes if not re.search(r"\b(no|never|without|sin|nunca)\b", p, re.I))


def campo(clip, plan, nombre):
    return clip.get(nombre) or plan.get(nombre) or ""


def revisar_clip(clip, plan, ritmo):
    """Errores que ya gastaron puntos en producciones reales. Cada uno se corrige gratis antes de generar."""
    fallos, cid, clase = [], clip.get("id", "?"), clip.get("clase", "camara")
    if clase not in CLASES:
        return [f"{cid}: «clase» debe ser una de {', '.join(CLASES)}"]
    linea = clip.get("linea", "")
    if clase != "muda" and not linea.strip():
        fallos.append(f"{cid}: falta «linea», lo que dice la voz")
    if clase == "muda" and clip.get("duracion") not in DURACIONES:
        fallos.append(f"{cid}: un clip sin voz necesita «duracion» de {DURACIONES} s")
    if linea and tiempos(linea, ritmo)[0] is None:
        maximo = int((DURACIONES[-1] - INICIO_S - COLA_S) * ritmo)
        fallos.append(f"{cid}: {contar(linea)} palabras no caben en 10 s a {ritmo:.2f} palabras/s. Parte la frase: máximo {maximo}")
    textos = [campo(clip, plan, n) for n in ("camara", "lugar", "personaje", "sujeto", "estilo")] + [clip.get("accion", ""), clip.get("manos", ""), linea]
    if any("@" in t for t in textos):
        fallos.append(f"{cid}: quita la «@»: en el cuadro abre el buscador de recursos. El personaje va como ficha y se nombra sin ella")
    if any(ESTUDIOS.search(t) for t in textos):
        fallos.append(f"{cid}: no nombres estudios ni personajes de terceros. Describe el estilo: forma, material, luz y color")
    visibles = [campo(clip, plan, n) for n in ("lugar", "personaje", "sujeto")] + [clip.get("accion", ""), clip.get("manos", "")]
    if any(TEXTO_EN_IMAGEN.search(afirmaciones(t)) for t in visibles):
        fallos.append(f"{cid}: no pidas texto ni logos a Flow: salen deformados. Déjale el espacio y agrégalos en el montaje")
    if clase == "camara":
        if MOVIMIENTO.search(afirmaciones(campo(clip, plan, "camara"))) or MOVIMIENTO_EN_ACCION.search(afirmaciones(clip.get("accion", ""))):
            fallos.append(f"{cid}: con alguien hablando la cámara queda fija. Pedir moverla hizo que Omni cortara a otra toma")
        if len(clip.get("objetos", [])) > 1 or DOS_OBJETOS.search(clip.get("manos", "")):
            fallos.append(f"{cid}: un solo objeto a la vez y siempre en la misma mano. Con dos aparecieron cosas de la nada")
    if clase != "narracion":
        for nombre in ("camara", "lugar", "estilo"):
            if not campo(clip, plan, nombre):
                fallos.append(f"{cid}: falta «{nombre}»")
        mirada = campo(clip, plan, "estilo") + " " + campo(clip, plan, "lugar")
        if not (LUZ.search(mirada) and PROFUNDIDAD.search(mirada)):
            fallos.append(f"{cid}: el estilo no pide luz ni profundidad o escala. Cada plano debe poder ser la portada")
    return fallos


def armar_prompt(clip, plan, ritmo):
    clase, linea = clip.get("clase", "camara"), clip.get("linea", "")
    audio = campo(clip, plan, "audio") or AUDIO_BASE
    evitar = ", ".join(x for x in (EVITAR_BASE, campo(clip, plan, "evitar")) if x)
    idioma = plan.get("idioma", "Spanish (Colombia)")
    if clase == "narracion":
        dur, fin = tiempos(linea, ritmo)
        return dur, fin, {
            "shot": "fixed camera, no people", "location": "plain dark background", "subject": "the supplied image stays still",
            "audio": "off-screen narrator voice, clean studio recording, no music, no ambience, no sound effects", "duration": f"{dur}s",
            "dialogue": {"language": idioma, "script": [{"t": f"{INICIO_S}-{fin}s", "line": linea}], "rule": REGLA_DIALOGO},
            "avoid": "music, ambience, sound effects, people talking"}
    p = {"shot": "one continuous shot with no cuts, " + campo(clip, plan, "camara"), "location": campo(clip, plan, "lugar")}
    if campo(clip, plan, "personaje") and clase == "camara":
        p["character"] = campo(clip, plan, "personaje")
    if campo(clip, plan, "sujeto"):
        p["subject"] = campo(clip, plan, "sujeto")
    if clase == "camara":
        p["hands"] = clip.get("manos") or "holds nothing in the hands"
    p["style"] = campo(clip, plan, "estilo")
    if clase == "muda":
        dur = clip["duracion"]
        p.update({"audio": audio, "duration": f"{dur}s",
                  "timeline": [{"t": f"0-{dur - 1}s", "action": clip.get("accion", "")}, {"t": f"{dur - 1}-{dur}s", "action": "still frame, a pulse of light"}],
                  "avoid": evitar})
        return dur, 0, p
    dur, fin = tiempos(linea, ritmo)
    if clase == "off":
        audio = campo(clip, plan, "audio") or "off-screen narrator voice, no person speaking on screen, soft ambience, no music"
        cierre = "silent, still frame, a pulse of light"
    else:
        cierre = "silent, mouth closed, holds still looking at the camera"
        if clip.get("objetos") or re.search(r"\bhold(s|ing)?\s+(?!nothing)", clip.get("manos", ""), re.I):
            cierre += ", keeping the same object in the same hand"
    p.update({"audio": audio, "duration": f"{dur}s",
              "timeline": [{"t": f"0-{fin}s", "action": clip.get("accion", "")}, {"t": f"{fin}-{dur}s", "action": cierre}],
              "dialogue": {"language": idioma, "script": [{"t": f"{INICIO_S}-{fin}s", "line": linea}], "rule": REGLA_DIALOGO},
              "avoid": evitar})
    return dur, fin, p


def preparar(a):
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
    clips = plan.get("clips", [])
    if not clips:
        sys.exit("clips.json no trae clips")
    ritmo = a.ritmo or plan.get("ritmo") or RITMO_TECHO
    fallos = [f for c in clips for f in revisar_clip(c, plan, ritmo)]
    ids = [c.get("id") for c in clips]
    if len(set(ids)) < len(ids):
        fallos.append("Hay clips con el mismo «id»")
    if fallos:
        print(json.dumps({"listo": False, "ritmo": ritmo, "fallos": fallos}, ensure_ascii=False, indent=1))
        sys.exit(1)
    avisos, filas, prompts = [], [], {}
    for c in clips:
        dur, fin, p = armar_prompt(c, plan, ritmo)
        clase = c.get("clase", "camara")
        if "no music" not in p["audio"]:
            avisos.append(f'{c["id"]}: pide «no music» en el audio: así la música no se corta entre clips')
        prompts[c["id"]] = json.dumps(p, ensure_ascii=False, separators=(",", ":"))
        filas.append({"id": c["id"], "clase": clase, "palabras": contar(c.get("linea")), "duracion_s": dur, "habla_hasta_s": fin,
                      "puntos_360p": COSTO["360p"][dur], "puntos_720p": COSTO["360p"][dur] if clase == "narracion" else COSTO["720p"][dur]})
    if a.clip:
        if a.clip not in prompts:
            sys.exit(f"No existe el clip {a.clip}")
        print(prompts[a.clip])
        return
    con_voz = [c for c in clips if c.get("linea") and c.get("clase") != "narracion"] or clips
    piloto = next((c for c in clips if c.get("piloto")), None) or max(con_voz, key=lambda c: (bool(c.get("objetos")), contar(c.get("linea"))))
    salida = a.plan.with_name("prompts.json")
    salida.write_text(json.dumps(prompts, ensure_ascii=False, indent=1), encoding="utf-8")
    ahorro, directo = sum(f["puntos_360p"] for f in filas), sum(f["puntos_720p"] for f in filas)
    print(json.dumps({"listo": True, "ritmo": ritmo, "ritmo_medido": bool(a.ritmo or plan.get("ritmo")), "piloto": piloto["id"], "clips": filas,
                      "puntos": {"360p_escalado_a_720p": {"base": ahorro, "con_margen": math.ceil(ahorro * MARGEN)},
                                 "720p_directo": {"base": directo, "con_margen": math.ceil(directo * MARGEN)}},
                      "prompts": str(salida), "avisos": avisos}, ensure_ascii=False, indent=1))


def en_cifras(palabras):
    """«dos mil veintiséis» pasa a «2026»: el transcriptor escribe cifras. Devuelve cada token y dónde empieza y termina."""
    salida, i = [], 0
    while i < len(palabras):
        if palabras[i] not in NUMEROS and palabras[i] != "mil":
            salida.append((palabras[i], i, i))
            i += 1
            continue
        total, actual, ultimo, j = 0, 0, 10 ** 9, i
        while j < len(palabras):
            w = palabras[j]
            if w == "mil":
                total, actual, ultimo = total + (actual or 1) * 1000, 0, 10 ** 9
            elif w in NUMEROS and NUMEROS[w] < ultimo:
                actual, ultimo = actual + NUMEROS[w], NUMEROS[w]
            elif w == "y" and 30 <= ultimo < 100 and j + 1 < len(palabras) and palabras[j + 1] in NUMEROS and NUMEROS[palabras[j + 1]] < 10:
                pass
            else:
                break
            j += 1
        salida.append((str(total + actual), i, j - 1))
        i = j
    return salida


def parecido_a(frase, lista, normalizar):
    """Se compara por letras: «mueve te» y «muévete» son lo mismo, y una cifra equivocada sí cuenta."""
    a = "".join(t for t, _, _ in en_cifras([n for n in map(normalizar, frase.split()) if n]))
    b = "".join(t for t, _, _ in en_cifras([n for n in (normalizar(p[0]) for p in lista) if n]))
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def comparar(frase, lista, normalizar):
    """Qué sobra y qué falta respecto al guion, con el segundo donde ocurre para poder cortarlo."""
    a = [t for t, _, _ in en_cifras([n for n in map(normalizar, frase.split()) if n])]
    voz = [x for x in ((normalizar(p), i, f) for p, i, f in lista) if x[0]]
    limpias = [(t, voz[d][1], voz[h][2]) for t, d, h in en_cifras([x[0] for x in voz])]
    b = [x[0] for x in limpias]
    sobran, faltan, cambian = [], [], []
    for op, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "insert":
            tramo = b[j1:j2]
            previas = b[max(0, j1 - len(tramo)):j1]
            sobran.append({"texto": " ".join(tramo), "desde": round(limpias[j1][1], 2), "hasta": round(limpias[j2 - 1][2], 2),
                           "repetida": tramo == previas or tramo[0] in a[max(0, i1 - 3):i1 + 1]})
        elif op == "delete":
            faltan.append(" ".join(a[i1:i2]))
        elif op == "replace":
            cambian.append({"guion": " ".join(a[i1:i2]), "dijo": " ".join(b[j1:j2])})
    return sobran, faltan, cambian


def revisar(a):
    from control_final import cortes, duracion, hoja, normalizar, palabras
    from narracion_desde_clips import limites_de_voz
    if not a.video.exists():
        sys.exit(f"No existe {a.video}")
    frase, clase = a.frase or "", "camara"
    if a.clips and a.id:
        plan = json.loads(a.clips.read_text(encoding="utf-8"))
        clip = next((c for c in plan["clips"] if c.get("id") == a.id), {})
        frase, clase = clip.get("linea", ""), clip.get("clase", "camara")
    total = duracion(a.video)
    carpeta = a.salida or a.video.parent / "revision"
    pasos = [round(x * HOJA_CADA_S, 2) for x in range(int(total / HOJA_CADA_S))]
    informe = {"video": a.video.name, "duracion_s": round(total, 2), "hoja": hoja(a.video, carpeta / f"{a.video.stem}.jpg", pasos)}
    razones_regenerar, razones_reparar, razones_duda = [], [], []
    internos = [t for t in cortes(a.video) if 0.3 < t < total - 0.3]
    informe["cortes"] = internos
    # En un tramo de narración la imagen no se ve. Sin persona, un destello se mide como corte:
    # un rollo de película que se vuelve un haz de luz marcó uno, y la toma era perfecta.
    if internos and clase == "camara":
        razones_regenerar.append(f"Hay un corte dentro del clip en {internos}: Omni cambió de toma")
    elif internos and clase != "narracion":
        razones_duda.append(f"Posible corte en {internos}: sin persona puede ser un destello. Míralo en la hoja antes de gastar otra toma")
    sin_transcripcion = True
    if frase:
        # Sin pistas de vocabulario: con ellas pierde frases de tomas buenas y esconde los tartamudeos
        lista, texto = palabras(a.video)
        if lista is None:
            desde, hasta = limites_de_voz(a.video)
            informe["voz"] = "sin comprobar: falta el transcriptor"
            if hasta > desde:
                informe["ritmo_palabras_s"] = round(contar(frase) / (hasta - desde), 2)
        elif not lista:
            razones_regenerar.append("No se detectó voz")
            sin_transcripcion = False
        else:
            sin_transcripcion = False
            parecido = parecido_a(frase, lista, normalizar)
            sobran, faltan, cambian = comparar(frase, lista, normalizar)
            _, sonido_hasta = limites_de_voz(a.video)
            # El transcriptor adelanta el final de la última palabra: el sonido lo corrige, sin contar el ambiente
            fin_voz = max(lista[-1][2], min(sonido_hasta, lista[-1][2] + FINAL_VOZ_MAX_S))
            informe.update({"transcripcion": texto, "coincidencia": round(parecido, 2), "sobran": sobran, "faltan": faltan, "cambian": cambian,
                            "ritmo_palabras_s": round(contar(frase) / max(0.1, fin_voz - lista[0][1]), 2)})
            if sonido_hasta - lista[-1][2] > SONIDO_TRAS_FRASE_S:
                informe["sonido_tras_la_frase"] = {"desde": round(lista[-1][2], 2), "hasta": round(sonido_hasta, 2)}
            if parecido < COINCIDENCIA_REGENERAR:
                razones_regenerar.append(f"La voz no dice el guion: coincidencia de {parecido:.0%}")
            else:
                for s in sobran:
                    razones_reparar.append(f"Sobra «{s['texto']}» de {s['desde']} a {s['hasta']} s: corta en un silencio o dentro del mismo sonido")
                if parecido < COINCIDENCIA_APROBAR and not sobran:
                    razones_duda.append(f"Coincidencia de {parecido:.0%}: puede ser el transcriptor. Compara «cambian» y «faltan», y pide escucharla antes de gastar otra toma")
    if razones_regenerar:
        veredicto = "regenerar"
    elif razones_reparar:
        veredicto = "reparar"
    elif razones_duda:
        veredicto = "dudoso"
    elif frase and sin_transcripcion:
        veredicto = "sin comprobar"
    else:
        veredicto = "aprobar"
    informe.update({"veredicto": veredicto, "razones": razones_regenerar + razones_reparar + razones_duda,
                    "falta_mirar": "La hoja: manos, objetos, cara, lugar y si el plano podría ser la portada. Esto no lo mide el script."})
    print(json.dumps(informe, ensure_ascii=False, indent=1))
    sys.exit(0 if veredicto == "aprobar" else 1)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    orden = p.add_subparsers(dest="orden", required=True)
    pre = orden.add_parser("preparar", help="escribe los prompts y calcula los puntos")
    pre.add_argument("plan", type=Path, help="03-flow/clips.json")
    pre.add_argument("--ritmo", type=float, help="palabras por segundo medidas en el clip piloto")
    pre.add_argument("--clip", help="imprime solo el prompt de este clip")
    pre.set_defaults(funcion=preparar)
    rev = orden.add_parser("revisar", help="revisa una toma ya descargada")
    rev.add_argument("video", type=Path)
    rev.add_argument("--frase", help="lo que debía decir la voz")
    rev.add_argument("--clips", type=Path, help="clips.json, en lugar de --frase")
    rev.add_argument("--id", help="id del clip en clips.json")
    rev.add_argument("--salida", type=Path, help="carpeta de la hoja de fotogramas; por defecto, revision/ junto al video")
    rev.set_defaults(funcion=revisar)
    a = p.parse_args()
    a.funcion(a)


if __name__ == "__main__":
    main()
