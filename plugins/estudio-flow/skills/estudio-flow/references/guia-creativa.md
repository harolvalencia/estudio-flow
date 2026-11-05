# Guía creativa

## El primer segundo decide

- El fotograma 0 es la portada y el gancho: una cara, un resultado o una frase potente ya en pantalla. Nunca negro, nunca un logo.
- El cambio o la pregunta llega en el primer compás.
- Mucha gente ve sin sonido: la imagen debe enganchar sola y todo lo hablado va subtitulado.

## Estructuras según el objetivo

| Objetivo | Estructura | Duración sugerida |
|---|---|---|
| Vender un producto | Problema, producto en acción, prueba, oferta | 15 a 30 s |
| Dar a conocer una marca | Imagen que detiene, historia corta, firma | 6 a 20 s |
| Generar mensajes o agendas | Pregunta directa, promesa, paso concreto | 10 a 20 s |
| Enseñar una idea en redes | Resultado primero, tres pasos, resumen | 30 a 60 s |
| Tutorial o capacitación | Skill `video-formativo` | 1 a 6 min |
| Lanzar algo nuevo | Tensión, revelación, fecha o acción | 15 a 30 s |
| Testimonio | Antes, momento de cambio, después | 20 a 45 s |

## Cómo hacer que las propuestas sean de verdad distintas

Cuando haya más de una, cambia al menos dos ejes entre una propuesta y otra:

- **Estructura:** problema y solución, viaje, lista, antes y después, revelación, conversación.
- **Protagonista:** persona, producto, personaje animado, tipografía, datos.
- **Estilo visual:** real, animación 3D, caricatura, plastilina, pizarra, infografía. Sigue [estilos-visuales.md](estilos-visuales.md).
- **Tono:** épico, cercano, divertido, íntimo, documental.
- **Técnica:** clips de Flow, fotografías animadas, texto cinético, construcción en HyperFrames, mezcla con material real.

Cada propuesta debe poder resumirse en una frase que no sirva para las otras.

## Escena por escena

- Ritmo vertical: tomas de 1 a 2 s y una idea nueva cada 2 a 4 s.
- Una sola idea en pantalla por vez. En vertical, unas cinco palabras por línea.
- Termina con el beneficio antes de que la persona deslice.
- El cierre sigue la sección 4 de [mejores-practicas-video.md](mejores-practicas-video.md): inspiración, acción dicha y escrita, logo y clímax.
- Deja los títulos y efectos para HyperFrames.

## Cuántos clips usar

Decídelo tú, sin preguntárselo a la persona. Esto aplica a piezas promocionales: en tutoriales manda la narración por tramos.

1. Calcula `clips = duración ÷ 7` y redondea hacia arriba. Son 3 clips para 15 o 20 s, 4 para 25 s y 5 para 30 s.
2. Usa clips de 6 y 8 s. Deja los de 4 s para insertos con poca voz y los de 10 s para una frase que no se pueda partir.
3. Agrega un clip si el guion lo necesita. Nunca aprietes la voz para que quepa.
4. Mantén el ritmo en el montaje, sin gastar más clips: reencuadres cada 2 a 3 s, títulos cinéticos y transiciones con intención.

## Video con voz: el camino por defecto

La voz va por defecto. Quién aparece lo decide el estilo. Un personaje que habla a cámara, real o animado, detiene más que un texto sobre una imagen, y una pizarra que se dibuja mientras alguien explica sostiene la atención en un tema difícil. Con Omni Flash y las voces de Flow se puede hacer sin grabar a nadie.

- Empieza con una frase hablada en los primeros 2 s.
- Una idea por clip. Antes de medir la voz, cuenta con 5 palabras en 4 s, 9 en 6 s, 13 en 8 s y 17 en 10 s. `clips_flow.py` lo recalcula con el ritmo real.
- Alterna a quien habla con voz en off sobre clips de producto o lugar, para esconder los cortes entre clips.
- La voz sigue en todas las escenas: ninguna queda solo con texto y música.
- Subtitula todo lo hablado con HyperFrames.
- Usa la misma voz guardada en toda la pieza y en toda la campaña.

## Qué hace cada herramienta

- **Flow:** todo lo que deba verse filmado o animado, o sonar hablado. Personas, personajes, productos en acción, lugares, movimiento de cámara y voces.
- **HyperFrames:** todo lo que deba ser exacto. Texto, logos, cifras, subtítulos, transiciones, gráficos, pizarras, infografías, llamados a la acción.

Nunca pidas a Flow texto legible ni logos: salen deformados. Déjale el espacio libre y agrégalos en HyperFrames.
