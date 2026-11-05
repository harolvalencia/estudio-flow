"""Comprueba que una lección enseña los pasos en un orden que se pueda seguir.

Uso:
    python validar_secuencia.py 00-brief/secuencia.json [--tutorial 04-montaje/tutorial.json]

Cada paso dice qué necesita y qué deja. Un paso no puede necesitar algo que se crea más adelante. Si el orden
falla, propone uno válido que cambia lo menos posible. Con --tutorial comprueba además que el video
enseña esos mismos pasos, en ese orden y sin saltarse ninguno.

Imprime un JSON y sale con código 1 si algo falla. El formato está en references/secuencia-logica.md.
"""
import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

PARECIDO_TITULO = 0.5


def limpiar(texto):
    return re.sub(r"\s+", " ", re.sub(r"[*|]", " ", texto or "")).strip().lower()


def orden_valido(pasos, inicio):
    """El primero de la lista que ya se puede hacer, una y otra vez. None si unos pasos se necesitan entre sí."""
    disponible, pendientes, orden = set(inicio), list(pasos), []
    while pendientes:
        siguiente = next((p for p in pendientes if set(p.get("necesita", [])) <= disponible), None)
        if siguiente is None:
            return None
        orden.append(siguiente)
        disponible |= set(siguiente.get("deja", []))
        pendientes.remove(siguiente)
    return orden


def revisar_secuencia(datos):
    fallos, avisos = [], []
    pasos = datos.get("pasos", [])
    if not pasos:
        return ["La secuencia no trae pasos"], avisos
    if not datos.get("caso_hilo"):
        fallos.append("Falta «caso_hilo»: el mismo registro de prueba debe atravesar toda la lección")
    if [p.get("n") for p in pasos] != list(range(1, len(pasos) + 1)):
        fallos.append("Los pasos deben ir numerados 1, 2, 3... sin saltos")
    for p in pasos:
        faltan = [c for c in ("titulo", "pantalla", "accion", "resultado") if not p.get(c)]
        if faltan:
            fallos.append(f'Paso {p.get("n")}: falta {", ".join(faltan)}')
    inicio = set(datos.get("punto_de_partida", []))
    disponible, crea_en = set(inicio), {}
    for p in pasos:
        for cosa in p.get("deja", []):
            crea_en.setdefault(cosa, p.get("n"))
    for p in pasos:
        for cosa in p.get("necesita", []):
            if cosa in disponible:
                continue
            if cosa in crea_en:
                fallos.append(f'Paso {p.get("n")} («{p.get("titulo")}») necesita «{cosa}», que se crea más adelante, en el paso {crea_en[cosa]}')
            else:
                fallos.append(f'Paso {p.get("n")} («{p.get("titulo")}») necesita «{cosa}» y ningún paso lo crea: agrégalo a «punto_de_partida» o enseña cómo se crea')
        disponible |= set(p.get("deja", []))
    usadas = {c for p in pasos for c in p.get("necesita", [])}
    for p in pasos[:-1]:
        if p.get("deja") and not set(p["deja"]) & usadas:
            avisos.append(f'Paso {p.get("n")} («{p.get("titulo")}»): nada de lo que deja se usa después. Revisa si sobra o si falta conectarlo')
    return fallos, avisos


def pasos_del_tutorial(guion):
    """Número de paso de cada escena, en el orden del video: el campo `paso` o una etiqueta «Paso 4 de 8»."""
    salida = []
    for n, e in enumerate(guion.get("escenas", []), 1):
        numero = e.get("paso")
        if numero is None:
            m = re.match(r"\s*paso\s+(\d+)", e.get("etiqueta") or "", re.I)
            numero = int(m.group(1)) if m else None
        if numero is not None:
            salida.append((n, int(numero), e.get("titulo", "")))
    return salida


def comparar_tutorial(datos, guion):
    fallos, avisos = [], []
    previo, vistos = 0, {}
    total = len(datos.get("pasos", []))
    for escena, numero, titulo in pasos_del_tutorial(guion):
        if numero < previo:
            fallos.append(f"Escena {escena}: va al paso {numero} después del paso {previo}. El video debe seguir el orden aprobado")
        elif numero > previo + 1:
            faltan = ", ".join(str(x) for x in range(previo + 1, numero))
            fallos.append(f"Escena {escena}: salta del paso {previo} al {numero}. Falta enseñar: {faltan}")
        previo = max(previo, numero)
        vistos.setdefault(numero, titulo)
    if previo < total:
        fallos.append(f"El video termina en el paso {previo} y la secuencia aprobada tiene {total}")
    elif previo > total:
        fallos.append(f"El video llega al paso {previo} y la secuencia aprobada tiene {total}")
    for p in datos.get("pasos", []):
        visto = vistos.get(p.get("n"))
        if visto and SequenceMatcher(None, limpiar(visto), limpiar(p.get("titulo"))).ratio() < PARECIDO_TITULO:
            avisos.append(f'Paso {p.get("n")}: en la secuencia es «{p.get("titulo")}» y en el video, «{limpiar(visto)}». Confirma que sea el mismo')
    return fallos, avisos


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("secuencia", type=Path)
    p.add_argument("--tutorial", type=Path, help="tutorial.json para comparar contra lo aprobado")
    a = p.parse_args()
    datos = json.loads(a.secuencia.read_text(encoding="utf-8"))
    fallos, avisos = revisar_secuencia(datos)
    informe = {"pasos": len(datos.get("pasos", []))}
    if fallos and datos.get("pasos"):
        orden = orden_valido(datos["pasos"], datos.get("punto_de_partida", []))
        if orden:
            informe["orden_sugerido"] = [f'{x.get("n")}. {x.get("titulo")}' for x in orden]
        else:
            informe["orden_sugerido"] = "Ninguno: unos pasos se necesitan entre sí, o algo no lo crea ningún paso"
    if a.tutorial:
        f, v = comparar_tutorial(datos, json.loads(a.tutorial.read_text(encoding="utf-8")))
        fallos += f
        avisos += v
    informe.update({"aprobada": not fallos, "fallos": fallos, "avisos": avisos})
    print(json.dumps(informe, ensure_ascii=False, indent=1))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
