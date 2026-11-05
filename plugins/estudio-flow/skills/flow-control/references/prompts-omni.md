# Cómo escribir prompts para Flow

Estas reglas salen de producir videos reales con Gemini Omni Flash, de 20 y 37 clips. Cada una corresponde a un fallo que ocurrió. Con el clip piloto, el cálculo de tiempos y la reparación, en el video de 37 clips se regeneraron 3 y se repararon 4 sin gastar. Con estas reglas, 4 clips de prueba en 4 estilos salieron bien al primer intento.

## Elegir el modo

- **Ingredientes** para fijar un personaje, producto o voz en una toma nueva. Es el modo de todo clip con voz fijada. Cada clip es una toma aparte: usa la misma imagen de escena y los mismos campos fijos, y corta con intención.
- **Fotogramas** para continuidad sin voz fijada. Cada clip arranca en el último fotograma del anterior: conserva lugar, personaje y luz.
- La voz fijada solo funciona en Ingredientes con Omni y siempre junto a una imagen o personaje. Detalles y catálogo en [voces-flow.md](voces-flow.md).
- Extender solo existe en Veo 3.1 Lite y solo para videos de Veo de 8 s.

## Prompt de imagen

```
<tipo de plano>, <sujeto y acción>, <lugar>, <luz y color>, <lente y profundidad de campo>, <estilo>, no text, no logos
```

Ejemplo real:

```
Macro shot of a glass light bulb in pitch black darkness, inside it a droplet of liquid cyan light swirling like ink in water, electric blue reflections on the glass, cinematic premium commercial, no text, no logos
```

Escribe los prompts en inglés y termina con `no text, no logos`. Los textos y marcas se agregan después con HyperFrames. Si la persona ya tiene imágenes, se usan en lugar de generarlas: el fotograma aprobado es lo que más intentos ahorra.

## Prompt de video: JSON de campos fijos

Mantén iguales los campos que dan consistencia y cambia solo `duration`, `timeline` y `dialogue`. Escríbelo en una línea. No lo armes a mano: lo escribe `clips_flow.py`, a partir de `clips.json`.

```json
{"shot":"medium shot, fixed camera, eye level","location":"<igual en todos los clips>","character":"@nombre, <vestuario fijo>","hands":"right side of the image holds <objeto>; left hand stays down","style":"<igual en todos los clips>","audio":"<ambiente>","duration":"8s","timeline":[{"t":"0-2.5s","action":"..."},{"t":"2.5-7s","action":"..."},{"t":"7-8s","action":"silent, still pose, mouth closed"}],"dialogue":{"language":"Spanish (Colombia)","script":[{"t":"0.2-2.5s","line":"Frase exacta."}],"rule":"say the script word by word, add nothing"},"avoid":"cuts, new locations, extra people, text, logos, subtitles, music"}
```

## clips.json

Los campos de arriba valen para todos los clips. Cada clip puede cambiar `camara`, `lugar`, `estilo` o `audio`.

```json
{
  "idioma": "Spanish (Colombia)",
  "camara": "locked-off static camera at eye level, medium shot; no pan, no zoom, no change of angle",
  "lugar": "<el mismo lugar, con detalle>. The background never changes.",
  "personaje": "<quién es y qué lleva, con lo que nunca cambia>",
  "estilo": "<receta de estilos-visuales.md + colores de la marca>",
  "audio": "only the voice and soft ambience, no music",
  "evitar": "<lo propio de esta pieza>",
  "clips": [
    {"id": "01", "linea": "Frase exacta.", "accion": "<qué hace mientras habla>", "manos": "holds nothing in the hands", "piloto": true},
    {"id": "02", "clase": "off", "camara": "slow push-in", "sujeto": "<qué se ve>", "linea": "Frase exacta.", "accion": "<qué pasa>"},
    {"id": "03", "clase": "muda", "duracion": 6, "camara": "slow push-in", "sujeto": "<qué se ve>", "accion": "<qué pasa>"},
    {"id": "n1", "clase": "narracion", "linea": "Frase exacta."}
  ]
}
```

| `clase` | Qué es |
|---|---|
| `camara` (por defecto) | Alguien habla mirando al público |
| `off` | La voz narra sobre un producto, un lugar o una idea |
| `muda` | Sin voz: lleva `duracion` de 4, 6, 8 o 10 s |
| `narracion` | Solo se usa el audio, siempre a 360p |

Marca con `"piloto": true` el clip más difícil. Si no marcas ninguno, el script elige el de un objeto en la mano o el de más palabras.

```
python _estudio/clips_flow.py preparar 03-flow/clips.json
python _estudio/clips_flow.py preparar 03-flow/clips.json --ritmo 2.3 --clip 02
```

El primero deja `03-flow/prompts.json` con todos los prompts y dice los puntos de cada ruta. El segundo imprime un solo prompt. Si encuentra un error conocido, no deja nada: corrígelo y vuelve a correrlo.

## Reglas

**Cámara y encuadre**

- Cámara fija y nada que no se vea en el fotograma inicial. Pedir girar o alejar hizo que Omni cortara a otra toma en un lugar inventado.
- Si un objeto debe aparecer, que entre al cuadro desde abajo.

**Manos y objetos**

- Un solo objeto a la vez y siempre en la misma mano.
- Nombra la mano por el lado de la imagen, en el campo `hands`.
- Para cambiar de objeto, uno sale por abajo y el otro entra por abajo con la misma mano.
- Dos objetos más una acción hicieron que aparecieran cosas de la nada y se cambiaran de mano.

**Diálogo**

- Omni habla entre **1,9 y 2,9 palabras por segundo**, y varía de un clip a otro aun con la misma voz. Se acomoda a la ventana que le das: Sulafat, medida antes a 2,9, habló a unas 2 palabras por segundo con la ventana calculada.
- Si le das más tiempo de habla del necesario, **repite palabras** para llenarlo. Pasó tres veces en un mismo video hasta ajustar la ventana.
- Por eso se calculan dos tiempos, y `clips_flow.py` los hace: la **duración del clip** sale del ritmo real, más 0,9 s de margen, y la **ventana de habla** sale de un ritmo 16 % más rápido.
- Sin medir la voz se usa 1,9 palabras por segundo, que da el presupuesto más alto. El clip piloto da el ritmo real.
- Pon el diálogo en `dialogue.script`, frase por frase con su tiempo, y deja el último tramo en `silent`.
- Los términos raros se escriben como suenan, por ejemplo una sigla deletreada.

**Final del clip**

- Termina en una pose quieta con la boca cerrada. Facilita el corte y sirve de fotograma inicial para el siguiente.

**Personajes**

- El personaje va como ficha en el cuadro, y en el prompt se nombra **sin `@`**, siempre igual: en el cuadro, la `@` abre el buscador de recursos.
- Di en `personaje` lo que nunca cambia. Un personaje se quitó el casco hasta que el prompt lo prohibió y `evitar` lo repitió.

**Texto y marca**

- Nunca pidas letreros, subtítulos ni logos. Pide un espacio limpio donde irán.
- Con productos o personas como ingrediente, usa referencias sobre fondo liso o recortado.

## Revisar cada toma

```
python _estudio/clips_flow.py revisar 03-flow/01.mp4 --clips 03-flow/clips.json --id 01
```

Compara la voz con el guion, busca palabras repetidas y cortes, mide el ritmo y deja una hoja de fotogramas cada 0,5 s en `03-flow/revision/`. Probado contra 42 tomas de un video real: acertó en las 11 con fallo o reparación conocidos y no dio ninguna falsa alarma clara en las 31 finales.

| Veredicto | Qué haces |
|---|---|
| `aprobar` | Mira la hoja. El script no ve manos, objetos, cara ni lugar |
| `reparar` | Corta lo que indica. No gastes otra toma |
| `regenerar` | Cambia el prompt según la tabla de abajo |
| `dudoso` | Compara `cambian` y `faltan`: puede ser el transcriptor. Pide escucharla antes de gastar |
| `sin comprobar` | Falta el transcriptor. Mira la hoja y pide escucharla |

Un tartamudeo muy corto puede pasar sin detectarse. Sin el transcriptor no se comprueba la voz.

## Qué hacer con cada fallo

**Regenera solo si no se puede arreglar sin gastar.** Máximo 2 veces por clip, y cada vez con el prompt cambiado: repetir el mismo gasta puntos para obtener el mismo error. Si sigue fallando, parte la frase o cubre el tramo en el montaje.

| Fallo | Causa probable | Arreglo sin gastar | Si hay que regenerar |
|---|---|---|---|
| Repite una palabra | Sobra tiempo de habla | Corta en un silencio o dentro del mismo sonido, con un cruce de 4 cuadros | Corre `preparar` con el ritmo medido |
| Balbucea al final | Sobra tiempo tras la frase | Recorta el clip donde termina la frase | Acorta la ventana |
| Silencio al empezar | Normal: hasta 0,7 s | Recórtalo. `narracion_desde_clips.py` lo hace solo | No regeneres |
| Dedos que no cuadran con lo que dice | Pedir que cuente con los dedos: para tres cosas levantó cuatro | Pide un gesto abierto y pon el conteo en el montaje | Regenera solo si se nota junto al texto |
| Pronuncia mal una palabra | Término raro | Ninguno | Escríbela como suena y pruébala antes en la vista previa, que es gratis |
| Corta a otra toma | Se pidió mover la cámara o algo fuera del encuadre | Usa el tramo antes del corte si alcanza | Cámara fija y nada que no esté en la imagen inicial |
| Aparece un objeto o cambia de mano | Dos objetos más una acción | Cubre ese tramo con otro plano | Un objeto, en la misma mano, y que entre desde abajo |
| Cambian la cara o el vestuario | Sin imagen de referencia, o sin decir qué es fijo | Ninguno | Agrega la imagen del personaje y di en `personaje` lo que no cambia |
| Gestos a destiempo | Muchas acciones en un solo tramo | Ninguno | Reparte la acción en `timeline` por frases |
| Texto o logo deformado | Se pidió o se mencionó | Cúbrelo en el montaje | Quítalo de la descripción y déjale el espacio libre |
| Trae música | Falta `no music` | Ninguno: la música se corta entre clips | Agrega `no music` en `audio` |
| El plano no podría ser la portada | `estilo` o `lugar` pobres | Reencuadre, luz y destellos en el montaje | Sube luz, profundidad y escala en los campos fijos |

No gastes puntos en dudas de gusto si cumple el storyboard. No aceptes un plano pobre para ahorrar.
