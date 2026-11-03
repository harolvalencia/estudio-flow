# Modo rápido

Es la prueba para una clase o una demostración: un video vertical de unos 9 s con un solo clip de Flow. La meta es tenerlo en menos de 5 minutos.

Se activa cuando la persona escribe **«modo rápido»** o **«prueba rápida»**.

## Qué cambia

| Se omite | Se mantiene |
|---|---|
| Entrevista larga, investigación web y manual de marca | Pedir la carpeta |
| Propuestas, storyboard y presupuesto en tabla | Decir el costo antes de gastar |
| HyperFrames, varios clips y `control_final.py` | Voz de Flow y cierre dicho y escrito |

Las reglas de siempre siguen: no escribir contraseñas, no resolver CAPTCHAs, no publicar y no inventar datos.

## Pasos

1. **Carpeta.** Pídela y no pidas Descargas si la persona ya la autorizó.
2. **Datos.** Toma del mensaje la empresa, el color, la escena, la frase y la acción. Si falta algo, haz **una sola pregunta** con todo lo que falte. Sin color usa `#19E3E6`.
3. **Costo.** Si el mensaje no dice «Apruebo 12 puntos», pídelo en una línea y espera el sí.
4. **Imagen.** En un proyecto nuevo de Flow genera una imagen 9:16 con Nano Banana 2.1, `x1`. Tarda unos 15 s y cuesta 0 puntos.
5. **Clip.** Pasa a `Vídeo`, `Ingredientes`, `Omni 1.1 Flash`, 9:16, 720p, 8 s, `x1`. Agrega esa imagen y la voz `Sulafat` del catálogo, sin personalizarla. Confirma las dos fichas y el costo, y genera. Tarda cerca de 1 minuto.
6. **Descarga.** Baja el tamaño original de 720p. No pidas 1080p: tarda más y aquí no hace falta.
7. **Acabado.** Copia `pieza_rapida.py` de la skill `acabado-hyperframes` a `_estudio/` y ejecútalo:

```
python _estudio/pieza_rapida.py 03-flow/01.mp4 --frase "<frase>" --accion "<acción>" --color "<color>" --logo 01-referencias/logo.png --salida 05-final/prueba-rapida.mp4
```

`--logo` es opcional: úsalo solo si hay un logo en la carpeta. El proceso tarda unos 2 s y solo necesita ffmpeg y Pillow.

8. **Entrega.** Mira un fotograma del medio y otro del final. Muestra el video y di los puntos gastados.

## Guion

Voz total: máximo 17 palabras, frase y acción juntas. El clip debe terminar con la acción dicha.

## Prompt del clip

Escribe todo en una línea:

```json
{"shot":"slow push-in, medium shot","location":"<lugar de la escena>","subject":"<qué pasa, con luz en el color de la marca>","style":"epic premium commercial, volumetric light, high contrast","audio":"warm confident voice, soft ambience, no music","duration":"8s","timeline":[{"t":"0-7s","action":"<acción mientras habla>"},{"t":"7-8s","action":"silent, still pose, mouth closed"}],"dialogue":{"language":"Spanish (Colombia)","script":[{"t":"0.2-7s","line":"<frase> <acción>"}],"rule":"say the script word by word, add nothing"},"avoid":"cuts, text, logos, subtitles, music"}
```

## Si algo se demora

- Si Flow tarda más de 3 minutos en un clip o falla dos veces, avisa. No reintentes más: en clase, el tiempo importa más que ese clip.
- Con varias personas generando a la vez, Flow puede tardar más. Si la clase se atrasa, usa `pieza_rapida.py` con un clip ya generado.
