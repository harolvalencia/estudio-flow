# Cómo escribir prompts para Flow

Estas reglas salen de producir un video real de 20 clips con Gemini Omni Flash. Cada una corresponde a un fallo que ocurrió.

## Elegir el modo

- **Fotogramas** para continuidad. Cada clip arranca en el último fotograma del anterior: conserva lugar, personaje y luz. Es el modo por defecto para una secuencia.
- **Ingredientes** para fijar un personaje, producto o voz en una toma nueva. Cada clip es una toma aparte, así que rompe la continuidad entre clips.
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

Escribe los prompts en inglés y termina con `no text, no logos`. Los textos y marcas se agregan después con HyperFrames.

## Prompt de video: JSON de campos fijos

Mantén iguales los campos que dan consistencia y cambia solo `duration`, `timeline` y `dialogue`. Escríbelo en una línea.

```json
{"shot":"medium shot, fixed camera, eye level","location":"<igual en todos los clips>","character":"@nombre, <vestuario fijo>","hands":"right side of the image holds <objeto>; left hand stays down","style":"<igual en todos los clips>","audio":"<ambiente>","duration":"8s","timeline":[{"t":"0-2.5s","action":"..."},{"t":"2.5-7s","action":"..."},{"t":"7-8s","action":"silent, still pose, mouth closed"}],"dialogue":{"language":"Spanish (Colombia)","script":[{"t":"0.2-2.5s","line":"Frase exacta."}],"rule":"say the script word by word, add nothing"},"avoid":"cuts, new locations, extra people, text, logos, subtitles, music"}
```

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

- Omni habla entre **2,2 y 2,9 palabras por segundo**. Calcula: tiempo de la frase = palabras / 2,2, y comprueba en la transcripción.
- Si le das más tiempo de habla del necesario, **repite palabras** para llenarlo.
- Pon el diálogo en `dialogue.script`, frase por frase con su tiempo, y deja el último tramo en `silent`.
- Deja un segundo de margen y escribe «word by word, add nothing».
- Los términos raros se escriben como suenan, por ejemplo una sigla deletreada.

**Final del clip**

- Termina en una pose quieta con la boca cerrada. Facilita el corte y sirve de fotograma inicial para el siguiente.

**Personajes**

- Se citan con `@`, siempre igual. Sin `@` el modelo puede confundirlos con otra cosa. `@me` es el avatar de la persona.

**Texto y marca**

- Nunca pidas letreros, subtítulos ni logos. Pide un espacio limpio donde irán.
- Con productos o personas como ingrediente, usa referencias sobre fondo liso o recortado.

## Revisar cada toma

1. Hoja de fotogramas cada 0,5 s.
2. Transcripción palabra por palabra: detecta repeticiones y tartamudeo.
3. ¿Hubo un corte dentro del clip? ¿Cambió el lugar?
4. ¿Las manos, los objetos y la cara son los mismos?

Si falla, cambia el prompt: repetir el mismo gasta puntos para obtener el mismo error. Cuando el fallo es solo una palabra repetida, se puede reparar con un corte en un silencio sin regenerar.
