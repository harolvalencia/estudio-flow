---
name: acabado-hyperframes
description: "Une los clips de Flow y les da el acabado profesional con HyperFrames: igualar color y volumen, títulos, subtítulos, marca, llamado a la acción, render y exportes para cada red. Úsala después de descargar las tomas de Flow o cuando haya que montar, subtitular, poner logo o renderizar un video en Estudio Flow."
---

# Acabado con HyperFrames

HyperFrames convierte HTML en video. Da control exacto sobre lo que Flow no hace bien: texto, logos, cifras, subtítulos y ritmo. Si las skills `hyperframes`, `hyperframes-cli`, `hyperframes-registry` y `media-use` están disponibles, léelas antes de componer: mandan sobre este resumen. Si no están, instala el plugin desde el marketplace `heygen-com/hyperframes` o sigue este archivo.

## Dónde ejecutar

Usa la ruta guardada en `proceso.json` en `entorno.ruta`:

- **windows:** Desktop Commander, con PowerShell, sobre la ruta real de la carpeta.
- **cowork:** la terminal de la sesión.

Ejecuta primero `python _estudio/verificar_entorno.py <carpeta>`. Si responde `"listo": false`, sigue lo indicado en `siguiente`.

## 1. Igualar los clips

Con las tomas en `03-flow/` como `01.mp4`, `02.mp4`:

```
python _estudio/igualar_y_unir.py 03-flow --salida unido.mp4
```

Iguala color, nitidez y volumen a −16 LUFS, y deja `03-flow/corregidos/` y `03-flow/final/unido.mp4`. Si el clip continúa al anterior reporta «modo par», con corrección exacta. Si reporta «plano nuevo» en un clip que debía ser continuo, ese clip no arrancó en el fotograma: regénéralo. Para sacar solo el fotograma inicial del clip siguiente usa `--solo-inicio`.

Si los clips son planos distintos a propósito, no hace falta unirlos aquí: usa los `corregidos/` por separado en el montaje.

## 2. Crear el montaje

```
npx hyperframes init 04-montaje --example blank --resolution portrait --non-interactive --skip-skills
```

`--resolution` acepta `portrait` (1080×1920), `landscape` (1920×1080) y `square` (1080×1080). Crea `04-montaje/assets/` con subcarpetas para fuentes, imágenes y audio, y copia ahí clips, logo y música. `index.html` es la composición raíz con una escena por archivo en `compositions/`.

### Reglas del contrato

1. Todo elemento con tiempo lleva `class="clip"`, `data-start` y `data-duration` en segundos.
2. La duración del video es la `data-duration` de la raíz.
3. Cada composición crea una línea de tiempo pausada y la registra: `window.__timelines["<data-composition-id>"] = tl`.
4. Sin `Date.now()`, `Math.random()` sin semilla, llamadas de red, temporizadores ni `repeat: -1`.
5. Nunca animes `display`, `visibility` ni `autoAlpha` en un `.clip`: anima un hijo.
6. Anima transformaciones, no `left`, `top`, `width` ni `height`.
7. Nunca uses `play()`, `pause()` ni busques posiciones en los medios. Un `<video>` conserva el sonido con `data-has-audio="true"`; si no, va `muted`.
8. Todo `<audio>` lleva `id`. Música y voz van en `<audio>` aparte.
9. Las fuentes fuera de las incluidas necesitan `@font-face` hacia `assets/fonts/`.
10. Rutas `assets/...` sin barra inicial.
11. Los filtros de color o grano van con `npx hyperframes media-treatment`, no con filtros CSS.
12. El archivo de una escena pone estilos, marcado y scripts dentro de `<template>` y da estilo a su raíz con `#root`.

### Qué agregar

- **Gancho:** frase fuerte visible desde el fotograma 0.
- **Subtítulos:** en la parte baja de la banda segura, con palabras clave en color de marca, sincronizados con la transcripción. Todo lo hablado va subtitulado.
- **Riqueza visual:** destellos, luz, partículas y transiciones con energía sobre clips con movimiento. Una escena con imagen fija y texto no se entrega.
- **Marca:** logo pequeño durante el video y protagonista en el cierre. Nunca abre el video.
- **Cierre:** 4 a 6 s con frase inspiradora, acción dicha y escrita, botón llamativo, logo con energía y clímax de música. Sostén 1,5 s el último cuadro.
- **Sonido:** voz delante, música de principio a fin entre 12 y 15 dB por debajo, sonidos en los cambios y un solo riser con golpe en el cierre.

Lee [el estándar de calidad](../estudio-flow/references/mejores-practicas-video.md). Antes de escribir a mano un efecto con nombre, búscalo: `npx hyperframes catalog <palabras>` y `npx hyperframes add <bloque>`. Para el cierre revisa `cta-close`, `cta-lockup` y `logo-outro`.

### Áreas seguras en 1080×1920

Nada entre 0 y 168 px. Todo el texto y el producto entre 168 y 1330 px. Debajo de 1330 px solo decoración. Sin texto en los últimos 150 px de la derecha. Letra mínima de 28 px.

## 3. Comprobar

Desde `04-montaje`:

```
npx hyperframes check --json
npx hyperframes snapshot --at 0,1.2,6.5,11.5 -o .hyperframes/snaps
```

Corrige todos los errores y mira la hoja `contact-sheet.jpg`. El verificador no lo ve todo: en la primera prueba dio 0 errores con las palabras pegadas, un texto cian sobre un fondo cian y el gancho sin leerse en el fotograma 0. Revisa siempre:

- El fotograma 0: la frase del gancho ya debe leerse.
- Espacio entre palabras en títulos grandes. Clash Display necesita `word-spacing: .16em`.
- Contraste de cada texto contra la imagen que tiene detrás, no contra el velo.
- Texto cortado o encima de una cara.
- Fotogramas negros. Un `id` de una escena nunca debe repetir el de un anfitrión de `index.html`: en la prueba, ocultar un subtítulo llamado `s1` ocultó toda la escena `s1` y el verificador no lo detectó. Usa prefijos claros como `sub1`.
- La ortografía de cada palabra en pantalla.

## 4. Renderizar

Desde `04-montaje`:

```
npx hyperframes render . -o ../05-final/maestro.mp4 -q delivery --quiet
```

En la prueba, 15 s de video en 1080×1920 tardaron menos de 2 minutos en Windows. Sin GPU suele tomar de 2 a 5 veces la duración del video. Si el video pasa de 240 s, guarda fotogramas en disco: comprueba que haya espacio.

## 5. Control final

Pasa el archivo por el control antes de exportar. Necesita `pip install faster-whisper`.

```
python _estudio/control_final.py ../05-final/maestro.mp4 --cierre 4
```

Si responde `"aprobado": false`, corrige lo que indica. Un tramo sin voz se arregla generando en Flow la locución de esa escena, no con más texto.

## 6. Exportar para cada red

```
python _estudio/exportar_redes.py 05-final/maestro.mp4 --nombre <pieza> --destino 05-final --sufijo 9x16 --liviana --portada 1
```

Entrega el archivo principal, una versión liviana para WhatsApp y una portada, y mide lo entregado. Copia esa salida a `proceso.json` en `entregables`.

Si el brief pide otro formato, no recortes: duplica la composición raíz con la nueva proporción y recompón las escenas.
