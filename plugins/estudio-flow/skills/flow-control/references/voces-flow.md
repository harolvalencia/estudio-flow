# Voces de Google Flow

Verificado en vivo el 2 de noviembre de 2026 con una cuenta Pro en español, generando y transcribiendo un clip real. Las voces solo funcionan con **Omni Flash** en modo **Ingredientes**.

## Lo que se comprobó

Prompt con diálogo en español, imagen como ingrediente y voz personalizada, 4 s a 720p, 7 puntos.

- Dijo la frase exacta, sin agregar ni repetir palabras.
- Mantuvo la cara de la imagen y terminó en pose quieta con la boca cerrada.
- Archivo entregado: 720×1280, 24 fps, 4,03 s, H.264 con audio AAC a 48 kHz.
- Velocidad medida: 10 palabras en 3,4 s, unas 2,9 palabras por segundo. Sin voz fijada se había medido 2,2. Calcula con 2,2 para dejar margen y comprueba siempre en la transcripción.
- Las vistas previas de voz no gastaron puntos.

## Reglas de Flow

- **Una voz nunca va sola.** Si solo hay voz, `Iniciar generación` queda desactivado y Flow explica «Un ingrediente de audio necesita otros ingredientes para funcionar». Agrega una imagen, un personaje o un video como ingrediente.
- El botón desactivado no da error: comprueba su atributo `disabled`.
- `Fotogramas` no acepta voz. Para un clip hablado usa `Ingredientes`.

## Crear la voz de la marca

Hazlo una vez por proyecto, antes del primer clip con diálogo:

1. En `Vídeo` e `Ingredientes` con `Omni 1.1 Flash`, pulsa `+` (`Añadir ingredientes a ventana para peticiones`) y espera unos 6 s.
2. Abre la pestaña `Voces`. Lee las posiciones por DOM: el panel cambia de lugar según la altura del cuadro de petición.
3. Escribe el nombre en `Buscar recursos`. **No hagas clic en la fila:** eso agrega la voz y cierra el panel. El panel derecho ya muestra la primera coincidencia.
4. Escribe en `Ejemplo de diálogo`, máximo 120 caracteres, una frase real de la pieza.
5. Escribe en `Personalizar interpretación` cómo debe sonar. Ejemplo probado: «Mujer colombiana, español neutro de Bogotá, voz cálida y segura, ritmo pausado, tono de locución publicitaria».
6. El panel se reacomoda: vuelve a leer las posiciones. Pulsa `Vista previa` y espera unos 8 s.
7. Pulsa `Guardar voz nueva`.
8. La voz queda de primera en la lista del proyecto. Se guarda como `Sulafat (personalizado)`: el nombre escrito en `Nombre de la voz` no se conservó en la prueba, así que búscala por ese nombre.
9. Con la voz en la lista, pulsa `Añadir a petición`. Aparece como una ficha en el cuadro.

El selector de la esquina superior del panel cambia de proyecto. Así se trae una imagen de otro proyecto sin descargarla ni subirla.

## Voz en off

Para una escena sin nadie hablando a cámara, usa la misma voz guardada con una imagen de producto o lugar como ingrediente. Explica en el prompt que la voz es una narración y que nadie aparece hablando: `audio: "off-screen narrator voice, no person speaking on screen"`.

La ayuda oficial indica que una voz se puede citar en el texto como `@Voice: nombre`. La prueba se hizo agregándola como ficha desde el panel.

## Generar un clip con voz

1. Agrega la voz y la imagen con el panel `+`. Deben verse dos fichas en el cuadro.
2. Escribe el prompt en una sola línea, con el diálogo en `dialogue.script`.
3. Comprueba que `Iniciar generación` esté activo y lee el costo en el panel de ajustes.
4. Genera. Un clip de 4 s tardó cerca de 1 minuto.
5. Descarga y transcribe. Compara palabra por palabra contra el guion.

## Narración larga por tramos

Un clip dura máximo 10 s. Para un tutorial, cada frase del guion es un tramo y un clip:

1. Corta el guion en tramos de hasta 22 palabras, cada uno una idea completa.
2. Usa la misma voz guardada, la misma interpretación y el mismo prompt de narración. Está en [la plantilla de tutorial](../../video-formativo/references/plantilla-tutorial.md).
3. Agrega cualquier imagen sencilla como ingrediente. No se verá: solo se usa el audio.
4. Descarga a `03-flow/voz/01.mp4`, `02.mp4` y así en orden.
5. Transcribe cada clip y compáralo con su tramo. Repite el que cambie una palabra.
6. Une todo con `narracion_desde_clips.py`, que recorta los silencios e iguala el volumen.

**Los tramos que solo aportan audio van a 360p.** Medido el 2 de noviembre de 2026 con la misma frase en 360p y 720p: AAC a 48 kHz y 128 kbps en ambos, mismo reparto de energía por frecuencias y misma transcripción. Cuesta la mitad. Las escenas que se ven, como apertura y cierre, van a 720p.

Para una pregunta, pide la pausa en el guion: dos líneas en `script` y un tramo callado en `timeline`. Así la persona tiene tiempo de pensar antes de oír la respuesta.

Verifica cómo dijo los términos en inglés. En las pruebas, los clips de Flow dejaron hasta 0,7 s de silencio al empezar: por eso se recortan.

En el tutorial de prueba, Sulafat dijo bien GitHub, Releases, Assets, Hyperframes y Upload plugin con el texto escrito normal.

## Continuidad entre clips hablados

Cada clip en `Ingredientes` es una toma nueva. Para que se sienta como una sola pieza:

- Usa en todos los clips la misma imagen de personaje, la misma voz guardada y los mismos campos `location` y `style`.
- Corta entre clips con cambio de plano o cubre el corte con otra imagen en HyperFrames.
- Para una acción continua sin diálogo usa `Fotogramas`.

## Catálogo: 29 voces

| Voz | Descripción en Flow | Sirve para |
|---|---|---|
| Sulafat | Female, warm, mid pitch | Marca cercana, probada en español |
| Kore | Female, firm, mid pitch | Institucional segura |
| Achernar | Female, soft, high pitch | Íntimo, belleza, cuidado |
| Aoede | Female, breezy, mid pitch | Estilo de vida |
| Autonoe | Female, bright, mid pitch | Promoción alegre |
| Callirrhoe | Female, easy-going, mid pitch | Conversación natural |
| Despina | Female, smooth, mid pitch | Premium, narración |
| Erinome | Female, clear, mid pitch | Tutoriales |
| Gacrux | Female, mature, mid pitch | Testimonios, autoridad |
| Laomedeia | Female, upbeat, mid-high pitch | Lanzamientos, energía |
| Leda | Female, youthful, mid-high pitch | Público joven |
| Vindemiatrix | Female, gentle, mid pitch | Salud, bienestar |
| Zephyr | Female, bright, mid-high pitch | TikTok, tono ligero |
| Charon | Male, informative, lower pitch | Explicación, noticias |
| Rasalgethi | Male, informative, mid pitch | Educación |
| Sadaltager | Male, knowledgeable, mid pitch | Experto, B2B |
| Alnilam | Male, firm, mid-low pitch | Corporativo |
| Orus | Male, firm, mid-low pitch | Institucional |
| Iapetus | Male, clear, mid-low pitch | Tutoriales |
| Schedar | Male, even, mid-low pitch | Narración neutra |
| Algieba | Male, easy-going, mid-low pitch | Conversación |
| Achird | Male, friendly, mid pitch | Atención al cliente |
| Zubenelgenubi | Male, casual, mid-low pitch | Tono informal |
| Puck | Male, upbeat, mid pitch | Promoción |
| Sadachbia | Male, lively, low pitch | Anuncio enérgico |
| Fenrir | Male, excitable, younger pitch | Público joven, humor |
| Umbriel | Male, smooth, lower pitch | Premium, tráiler |
| Enceladus | Male, breathy, lower pitch | Íntimo, cine |
| Algenib | Male, gravelly, low pitch | Épico, personajes rudos |

Las descripciones son de Flow. La columna «Sirve para» es una orientación: escucha siempre la vista previa. Solo Sulafat está probada en español. El catálogo puede cambiar: confírmalo en el panel `Voces`.
