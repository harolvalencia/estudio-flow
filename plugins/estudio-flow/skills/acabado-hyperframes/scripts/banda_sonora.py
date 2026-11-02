"""Compone una banda sonora original para el montaje: música, barridos, riser y golpe.

Uso:
    python banda_sonora.py --duracion 17.5 --cambios 3.9,9.7 --golpe 15 --salida assets/audio/banda.wav
                           [--perfil epico|sereno] [--activa 0-6,100-112] [--clics 12.3,20.8]
                           [--musica 0.3] [--tempo 100] [--semilla 7]

  --cambios   segundos donde cae un barrido, normalmente los cortes entre escenas
  --clics     segundos donde suena un clic, para los tutoriales de pantalla
  --golpe     segundo del golpe final; el riser crece justo antes y solo ocurre una vez
  --perfil    epico para piezas promocionales; sereno para tutoriales y capacitaciones
  --activa    tramos donde suena la música; el resto queda en silencio para que se oiga la voz
  --musica    ganancia de la música sin tocar los efectos; 1 la deja igual

Todo sale de síntesis, sin muestras de terceros, así que no hay licencias que revisar.
Deja un WAV estéreo a 48 kHz con pico de -1 dBFS. Solo necesita numpy.
"""
import argparse
import wave
from pathlib import Path

import numpy as np

SR = 48000
PICO_DBFS = -1.0
# Progresión en la menor, en Hz: la, fa, do y sol
ACORDES = {
    "epico": [(110.0, 164.81, 220.0, 261.63), (87.31, 130.81, 174.61, 220.0),
              (130.81, 196.0, 261.63, 329.63), (98.0, 146.83, 196.0, 246.94)],
    "sereno": [(130.81, 196.0, 246.94, 329.63), (110.0, 164.81, 220.0, 293.66),
               (87.31, 174.61, 220.0, 329.63), (98.0, 196.0, 246.94, 293.66)],
}


def paso_bajo(senal, corte):
    """Filtro de un polo por FFT: más rápido que recorrer la señal muestra a muestra."""
    f = np.fft.rfftfreq(len(senal), 1 / SR)
    return np.fft.irfft(np.fft.rfft(senal) / (1 + 1j * f / corte), len(senal))


def banda(senal, bajo, alto):
    f = np.fft.rfftfreq(len(senal), 1 / SR)
    return np.fft.irfft(np.fft.rfft(senal) * ((f >= bajo) & (f <= alto)), len(senal))


def sierra(t, frecuencia):
    return 2 * (t * frecuencia % 1) - 1


def reverberar(senal, segundos=1.8, mezcla=0.28, rng=None):
    """Convolución con ruido que decae, por FFT: da el aire de una sala grande."""
    n = int(segundos * SR)
    respuesta = rng.normal(0, 1, n) * np.exp(-np.linspace(0, 7, n))
    largo = len(senal) + n
    humedo = np.fft.irfft(np.fft.rfft(senal, largo) * np.fft.rfft(respuesta, largo), largo)[:len(senal)]
    humedo *= np.abs(senal).max() / (np.abs(humedo).max() + 1e-9)
    return senal * (1 - mezcla) + humedo * mezcla


def colchon(t, perfil, compas):
    """Acordes sostenidos, dos voces apenas desafinadas por nota."""
    pista = np.zeros_like(t)
    acordes = ACORDES[perfil]
    n_compases = int(t[-1] / compas) + 1
    transicion = 0.06
    for i in range(n_compases):
        inicio = i * compas
        mascara = ((t >= inicio - transicion) & (t < inicio + compas + transicion)).astype(float)
        cruce = np.clip((t - inicio + transicion) / transicion, 0, 1) * np.clip((inicio + compas + transicion - t) / transicion, 0, 1)
        for frecuencia in acordes[i % len(acordes)]:
            pista += mascara * cruce * (sierra(t, frecuencia * 0.997) + sierra(t, frecuencia * 1.003)) * 0.12
    return paso_bajo(pista, 900 if perfil == "epico" else 520)


def pulso(t, pulso_s, crecer):
    """Bajo que late en cada tiempo y gana fuerza hacia el final."""
    fase = (t % pulso_s) / pulso_s
    caida = np.exp(-fase * 7)
    return np.sin(2 * np.pi * 55 * t) * caida * (0.35 + 0.65 * crecer)


def arpegio(t, perfil, pulso_s, entrada):
    """Notas cortas en semicorcheas, una octava arriba del acorde."""
    pista = np.zeros_like(t)
    paso = pulso_s / 2
    acordes = ACORDES[perfil]
    for i in range(int(t[-1] / paso)):
        momento = i * paso
        if momento < entrada:
            continue
        acorde = acordes[int(momento / (pulso_s * 4)) % len(acordes)]
        frecuencia = acorde[i % len(acorde)] * 4
        desde, hasta = int(momento * SR), min(len(t), int((momento + 0.5) * SR))
        tramo = t[desde:hasta] - momento
        pista[desde:hasta] += np.sin(2 * np.pi * frecuencia * tramo) * np.exp(-tramo * 9)
    return pista * 0.1


def barrido(n, rng):
    """Ráfaga de aire que sube y baja, para los cortes."""
    ruido = rng.normal(0, 1, n)
    grave, agudo = banda(ruido, 200, 1800), banda(ruido, 1800, 9000)
    x = np.linspace(0, 1, n)
    cuerpo = np.sin(np.pi * x) ** 2.4
    return (grave * (1 - x) + agudo * x) * cuerpo


def subida(n, rng):
    """Riser: ruido que se abre y un tono que sube, ambos acelerando."""
    x = np.linspace(0, 1, n)
    ruido = rng.normal(0, 1, n)
    tono = np.sin(2 * np.pi * np.cumsum(180 + 1500 * x ** 3) / SR)
    return (banda(ruido, 500, 12000) * 0.5 + tono * 0.22) * x ** 2.6


def impacto(n, rng):
    """Golpe: una caída grave más un destello de ruido y un brillo que queda."""
    t = np.arange(n) / SR
    grave = np.sin(2 * np.pi * np.cumsum(38 + 90 * np.exp(-t * 9)) / SR) * np.exp(-t * 1.7)
    chasquido = banda(rng.normal(0, 1, n), 80, 5000) * np.exp(-t * 11) * 0.8
    brillo = sum(np.sin(2 * np.pi * f * t) for f in (880, 1318.5, 1760, 2637)) * np.exp(-t * 1.6) * 0.06
    return grave + chasquido + brillo


def clic(rng):
    """Toque seco y corto, como el de un ratón."""
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return (banda(rng.normal(0, 1, n), 1500, 7000) * 0.6 + np.sin(2 * np.pi * 1900 * t) * 0.5) * np.exp(-t * 170)


def tramos_activos(texto, t):
    """Envolvente con entradas y salidas suaves de 1,2 s en cada tramo."""
    if not texto:
        return np.ones_like(t)
    env = np.zeros_like(t)
    for parte in texto.split(","):
        ini, fin = (float(x) for x in parte.split("-"))
        env = np.maximum(env, np.clip((t - ini) / 1.2 + 1, 0, 1) * np.clip((fin - t) / 1.2, 0, 1))
    return env


def sumar(pista, sonido, segundo, ganancia=1.0):
    desde = int(segundo * SR)
    if desde >= pista.shape[0]:
        return
    hasta = min(pista.shape[0], desde + len(sonido))
    pista[desde:hasta] += sonido[:hasta - desde] * ganancia


def componer(a):
    rng = np.random.default_rng(a.semilla)
    t = np.arange(int(a.duracion * SR)) / SR
    pulso_s = 60 / a.tempo
    compas = pulso_s * 4
    crecer = np.clip(t / (a.golpe or a.duracion), 0, 1) ** 1.5
    if a.golpe:
        crecer[t >= a.golpe] = 1
    epico = a.perfil == "epico"
    musica = colchon(t, a.perfil, compas) * ((0.35 + 0.65 * crecer) if epico else 0.8)
    if epico:
        musica += pulso(t, pulso_s, crecer) * 0.9 + arpegio(t, a.perfil, pulso_s, a.duracion * 0.2) * (0.5 + crecer)
    else:
        musica += arpegio(t, a.perfil, pulso_s * 2, 0) * 0.7
    musica *= tramos_activos(a.activa, t)
    if a.golpe:
        # La música respira un instante antes del golpe, para que pegue más fuerte
        hueco = 1 - 0.75 * np.clip((t - (a.golpe - 0.45)) / 0.4, 0, 1) * (t < a.golpe)
        musica *= hueco
    izquierda, derecha = musica.copy(), np.roll(musica, int(0.011 * SR))
    efectos = np.zeros_like(t)
    fuerza = 0.5 if epico else 0.22
    for cambio in a.cambios:
        sonido = barrido(int(0.75 * SR), rng)
        sumar(efectos, sonido / (np.abs(sonido).max() + 1e-9), cambio - 0.42, fuerza)
    for momento in a.clics:
        sonido = clic(rng)
        sumar(efectos, sonido / (np.abs(sonido).max() + 1e-9), momento, 0.3)
    if a.golpe:
        largo = 2.6 if epico else 1.6
        sonido = subida(int(largo * SR), rng)
        sumar(efectos, sonido / (np.abs(sonido).max() + 1e-9), a.golpe - largo, 0.8 if epico else 0.25)
        sonido = impacto(int(min(4.0, a.duracion - a.golpe + 0.05) * SR), rng)
        sumar(efectos, sonido / (np.abs(sonido).max() + 1e-9), a.golpe, 1.4 if epico else 0.4)
    fondo = np.stack([reverberar(izquierda, rng=rng), reverberar(derecha, rng=rng)], 1)
    golpes = reverberar(efectos, rng=rng)[:, None]
    # La escala sale de la mezcla a ganancia 1: así --musica no sube los efectos al bajar la música
    escala = 10 ** (PICO_DBFS / 20) / (np.abs(fondo + golpes).max() + 1e-9)
    salida_suave = np.clip((a.duracion - t) / 0.25, 0, 1)[:, None]
    return (fondo * a.musica + golpes) * escala * salida_suave


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--duracion", type=float, required=True)
    p.add_argument("--cambios", type=lambda s: [float(x) for x in s.split(",") if x], default=[])
    p.add_argument("--clics", type=lambda s: [float(x) for x in s.split(",") if x], default=[])
    p.add_argument("--golpe", type=float)
    p.add_argument("--perfil", choices=ACORDES, default="epico")
    p.add_argument("--activa", help="tramos con música, por ejemplo 0-6,100-112")
    p.add_argument("--musica", type=float, default=1.0)
    p.add_argument("--tempo", type=float, default=100)
    p.add_argument("--semilla", type=int, default=7)
    p.add_argument("--salida", type=Path, required=True)
    a = p.parse_args()
    a.salida.parent.mkdir(parents=True, exist_ok=True)
    pcm = (componer(a) * 32767).astype(np.int16)
    with wave.open(str(a.salida), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"Listo: {a.salida} ({a.duracion:g} s, perfil {a.perfil})")


if __name__ == "__main__":
    main()
