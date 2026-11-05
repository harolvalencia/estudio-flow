# Estilos visuales

No todo video necesita una persona. El estilo se pregunta en la entrevista. Todos deben llegar al [estándar de calidad](mejores-practicas-video.md): cambia la forma, no la ambición.

| Estilo | Cómo se produce | Puntos | Sirve para | Estado |
|---|---|---|---|---|
| **Real cinematográfico** | Clips de Omni | Los del clip | Marcas de servicio, testimonios, cercanía | Probado |
| **Animación 3D de película** | Clips de Omni con un personaje fijo | Los del clip | Explicar con calidez, personajes de marca, público amplio | Probado con voz, más de 40 clips |
| **Caricatura 2D** | Clips de Omni con un personaje fijo | Los del clip | Humor, público joven, ideas simples | Probado con voz, 1 clip |
| **Plastilina** | Clips de Omni con un personaje fijo | Los del clip | Piezas memorables, artesanía, alimentos | Probado con voz, 1 clip |
| **Pizarra** | HyperFrames, dibujos de Nano Banana y voz por tramos | Solo la voz, más apertura y cierre | Explicar un proceso o una idea que se construye | Probado con voz: 80 s, 10 clips, 69 puntos |
| **Infografía animada** | HyperFrames, iconos de Nano Banana y voz por tramos | Solo la voz, más apertura y cierre | Datos, pasos, comparaciones | Probado con voz: 62 s, 8 clips |

Los clips de prueba de caricatura y plastilina (6 s a 360p, escalados a 720p, 5 puntos cada uno) salieron bien al primer intento: voz exacta, sin repeticiones, labios sincronizados y sin cambio de estilo. Es un solo clip por estilo: el clip piloto de cada pieza sigue siendo la prueba real.

## Cómo preguntar

**«¿Qué estilo imaginas para este video?»** Ofrece: real, animación 3D, caricatura, plastilina, pizarra e infografía. Si la persona no sabe, recomienda según el objetivo y, cuando haya varias propuestas, varía el estilo: **al menos una no es realista**.

Guarda la respuesta en `proceso.json`, en `brief.estilo`, y en `plan.json`, en el campo `estilo` de cada propuesta.

Muéstralo antes de gastar: los fotogramas del storyboard se generan en ese estilo con Nano Banana 2.1, a 0 puntos.

## Nombres de estudios

Si la persona dice «tipo Pixar» o «como Disney», entiende qué busca y descríbelo. **Nunca escribas en un prompt el nombre de un estudio, una película o un personaje de terceros.** `clips_flow.py` lo rechaza. Tampoco copies un personaje conocido: crea uno propio.

## Recetas

Copia el texto en inglés al campo `estilo` de `clips.json` y agrega los colores de la marca. Con una imagen de referencia, empieza por `same <estilo> as the reference image`: así no cambia de estilo entre clips.

**Real cinematográfico.** Épico por la luz y la escala.
`cinematic live-action commercial, natural skin texture, volumetric light, backlit rim light, shallow depth of field, deep layered background`

**Animación 3D de película.** Épico por la luz cálida, la profundidad y el gesto.
`stylized 3D animated feature film look, friendly rounded proportions, expressive eyes, soft skin shading, warm global illumination, volumetric light, deep layered background, rich saturated colors, crisp sharp focus`

**Caricatura 2D.** Épico por la composición, el color y los fondos pintados.
`hand-drawn 2D cartoon animation, clean ink outlines, cel shading, bold saturated colors, painted background with deep parallax layers, dramatic rim light, expressive poses`

**Plastilina.** Épico por la luz de estudio sobre un set en miniatura. Pide el personaje sin nada delante: en la prueba, una mesa ocupó el tercio inferior del cuadro.
`stop-motion clay animation, handmade plasticine with subtle fingerprints, miniature set with deep layered background, warm dramatic studio light, shallow depth of field`

## Personajes

Con personaje animado, la coherencia se gana antes de gastar:

1. Genera el personaje una vez con Nano Banana, de frente y sobre un fondo limpio, y haz que la persona lo apruebe.
2. Úsalo como ingrediente en todos los clips, siempre con la misma descripción en `personaje`.
3. Di en esa descripción lo que nunca cambia, y en `evitar`, lo que no debe pasar. En un video real, un personaje se quitó el casco hasta que el prompt lo prohibió.

No recrees a una persona real sin que la persona confirme que tiene su autorización. Eso incluye su versión en caricatura.

## Pizarra e infografía

Se construyen con la escena `construccion` de `armar_tutorial.py`, también en piezas promocionales. Sigue [la plantilla](../../video-formativo/references/plantilla-tutorial.md#construccion). Cada elemento aparece cuando la voz dice su palabra, y al final la cámara se aleja y se ve todo.

**Cómo llegan a lo épico**, porque un fondo blanco con dibujos no basta:

- Usa un lienzo grande para que la cámara viaje de una idea a otra.
- Prefiere el tablero oscuro con líneas de luz. El claro sirve si la marca lo pide.
- Abre y cierra con un clip de Flow en el mismo estilo, si el presupuesto lo permite. El dibujo que cobra vida es la mejor apertura.
- Reserva la revelación para el final: la cámara se aleja, la luz sube y entra el golpe musical.
- Usa `"banda": {"perfil": "epico", "continua": true}` en piezas promocionales.

**Dibujos con Nano Banana 2.1 (0 puntos).** Sobre negro puro, para que el fondo desaparezca sobre el tablero oscuro:

`hand-drawn white chalk line illustration of <qué>, thick expressive strokes, pure black background, no shading, no text, no logos`

Sobre blanco puro para el tablero claro:

`hand-drawn dark marker line illustration of <qué>, thick expressive strokes, pure white background, no shading, no text, no logos`

Iconos de infografía:

`glowing flat icon of <qué> in <colores de la marca>, clean shapes, pure black background, no text, no logos`

Fondo del tablero, para `textura`:

`an empty dark slate blackboard filling the whole frame, seen straight on, even soft lighting, subtle chalk dust smudges and faint erased marks, very dark charcoal, no frame, no text, no letters, no numbers, no drawings, no logos`

Si un dibujo sale sobre un gris en vez de negro puro, sube el punto negro antes de usarlo: con la mezcla `screen`, ese gris se ve como un cuadrado sobre el tablero. Con Pillow bastó poner en 0 todo lo que estaba por debajo de 70.

Los textos y las cifras los escribe HyperFrames, nunca la imagen.

**El título de la apertura.** Va a la izquierda, sobre un velo oscuro. Pide en el clip el motivo a la derecha, con la izquierda vacía: `the subject in the right two thirds of the frame, the left third dark and empty`. Si el clip ya salió centrado, muévelo a la derecha con ffmpeg y rellena la izquierda con su espejo, sin gastar puntos.

**La voz.** Va por tramos a 360p, como en un tutorial. La imagen de esos clips no se ve. Sigue [narración por tramos](../../flow-control/references/voces-flow.md#narración-larga-por-tramos).

**El control.** Estas piezas tienen pausas entre dibujos:

```
python _estudio/control_final.py 05-final/<video>.mp4 --cierre 4 --congelado 8 --pausa 3.5
```

## Pantalla real

El estilo nunca cambia una interfaz: se muestra real, con datos de prueba. Un tutorial en caricatura lleva caricatura en el presentador, la apertura y el cierre, y pantalla real en cada paso.
