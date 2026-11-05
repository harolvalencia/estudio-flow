# Estándar de calidad de cada video

Este estándar es obligatorio. Una pieza que no lo cumpla no se entrega. Solo se omite una regla si la persona lo pide de forma expresa.

En tutoriales y capacitaciones aplica además [el estándar formativo](../../video-formativo/references/diseno-instruccional.md), que cambia el ritmo, los subtítulos y dónde va lo épico.

Las reglas salen de la ayuda oficial de Flow, de la producción real de videos con Omni Flash y de las guías de HyperFrames. Las plataformas cambian: no cites porcentajes ni datos de rendimiento que no puedas comprobar.

## 1. Voz de principio a fin

Un video con voz solo al comienzo se siente incompleto.

- La locución acompaña **todo** el video. Máximo 1,5 s seguidos sin voz, salvo el remate final.
- Cada escena tiene su línea de locución en `plan.json`, antes de generar nada.
- **Prohibido dejar una escena solo con texto y música.**
- Toda voz sale de Google Flow. Hay dos formas de hacerlo, y ambas usan la misma voz guardada:
  - **A cámara:** una persona habla mirando al público.
  - **Voz en off:** la imagen es un producto, un lugar o una idea, y la voz narra sin que nadie aparezca hablando.
- El guion total se calcula antes: `palabras = duración en segundos × 2,3`. Para 15 s, unas 34 palabras.
- Todo lo hablado va subtitulado y sincronizado con la transcripción.

## 2. Épico y visualmente rico

Cada plano debe poder ser la portada de la pieza.

- **Movimiento real.** Toda escena final es un clip de Omni o Veo. Una imagen fija con zoom solo sirve para ensayar en el storyboard.
- **Tres capas por plano.** Sujeto con profundidad, fondo con vida y una capa de luz como partículas, destellos, humo o reflejos.
- **Dirige la luz.** Pide contraluz, haces volumétricos, destellos anamórficos y alto contraste con los colores de la marca.
- **Escala.** Alterna un detalle macro con un plano amplio. Lo pequeño que se vuelve enorme es lo más épico.
- **Una transformación.** El video cuenta un cambio visible: de la idea al resultado, de la oscuridad a la luz.
- **Ritmo.** Una idea nueva cada 2 a 4 s. Ningún plano queda quieto más de 2 s, salvo el cierre.
- **Transiciones con intención.** Destellos, barridos de luz o un objeto que cruza el cuadro. Evita el fundido a negro entre escenas.
- **Tipografía viva.** Títulos cinéticos en la tipografía de la marca, palabra clave en color de acento.
- En HyperFrames busca primero en el catálogo: `lens-flare`, `vfx-anamorphic-flare`, `light-leak`, `light-sweep-pass`, `organic-light-leak-overlay`, `particle-image-reveal`, `caption-gradient-fill`.

## 3. Sonido en capas

1. **Voz:** siempre delante.
2. **Música:** de principio a fin, entre 12 y 15 dB por debajo de la voz. Crece hacia el cierre.
3. **Sonido de acción:** un golpe, barrido o destello en cada cambio importante. No repitas el mismo.
4. **Riser y golpe:** una sola vez, justo al llegar el llamado a la acción.

El archivo final queda a −16 LUFS con pico de −1 dBTP. Si Flow trae música propia en un clip, pide `no music` en el prompt y agrégala en el montaje: así la música no se corta entre clips.

## 4. Cierre que mueve a actuar

El video termina en su punto más alto. El cierre dura de 4 a 6 s y tiene estas partes:

1. **Inspiración:** una frase que devuelve el beneficio a la persona.
2. **Acción:** un verbo y qué hacer exactamente, **dicho por la voz y escrito en pantalla**.
3. **Marca:** el logo aparece con energía, no como un pie de página.
4. **Clímax:** la música sube, entra el golpe y la imagen llega a su mayor brillo.
5. **Sostén:** el mensaje final queda quieto 1,5 s para poder leerse.

Fórmula: `Beneficio inspirador + verbo + acción concreta`.

| Débil | Fuerte |
|---|---|
| «Agenda tu diagnóstico gratuito» | «Tu próxima gran idea empieza hoy. Agenda tu diagnóstico gratuito.» |
| «Compra ya» | «Tu mesa merece este sabor. Pídelo hoy por WhatsApp.» |
| «Más información» | «El cambio empieza contigo. Escríbenos ahora.» |

Usa frases y ofertas reales de la marca. Nunca inventes descuentos, cupos ni urgencias.

## 5. Gancho

- La voz y la imagen fuerte arrancan desde el primer segundo.
- El fotograma 0 ya muestra la frase del gancho.
- Empieza con un problema, una pregunta o una promesa, nunca con el logo.

## 6. Prompts que funcionan en Flow

Recomendaciones de la ayuda oficial:

- Sé específico con sujeto, acción, entorno, iluminación y estilo.
- Explica cómo debe usarse cada ingrediente dentro del clip.
- El texto debe complementar las imágenes, no contradecirlas.
- Para mantener la voz entre clips, agrega una sola referencia de voz.

Reglas propias:

- Pon el diálogo exacto en `dialogue.script` y agrega `say the script word by word, add nothing`.
- Describe el sonido ambiente y los efectos en `audio`.
- Con personas hablando, usa cámara fija. En planos sin personas puedes pedir un avance lento de cámara.
- Termina cada clip en una pose quieta o en un momento de luz, para cortar limpio.

## 7. Control final

Antes de entregar:

```
python _estudio/control_final.py 05-final/<video>.mp4 --cierre 4
```

En Mac y Linux, cambia `python` por el valor de `comando_python` que da `verificar_entorno.py`.

El video no se entrega hasta que apruebe. Además, míralo completo con sonido o revisa la hoja de fotogramas y la transcripción.
