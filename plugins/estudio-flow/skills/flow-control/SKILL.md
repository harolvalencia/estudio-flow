---
name: flow-control
description: "Maneja Google Flow desde Chrome con Claude in Chrome: crear proyectos, configurar modelo y formato, escribir prompts, subir archivos, generar, vigilar el avance, revisar, renombrar y descargar imágenes y clips. Úsala siempre que haya que operar flow.google.com. Recetas verificadas en la interfaz real en español el 2 de noviembre de 2026."
---

# Control de Google Flow

Flow vive en `https://flow.google.com/`. La dirección antigua `labs.google/fx/tools/flow` redirige ahí. Se opera con el Chrome real de la persona, con su sesión.

Antes de empezar lee la skill de Claude in Chrome si está disponible, abre una pestaña nueva y confirma con una captura que la sesión está iniciada: arriba a la derecha aparece el plan, por ejemplo `PRO`. Si no hay sesión, detente y pídele a la persona que entre. Nunca escribas su contraseña.

Mapa completo de la interfaz: [references/mapa-interfaz.md](references/mapa-interfaz.md). Cómo escribir prompts: [references/prompts-omni.md](references/prompts-omni.md). Voces: [references/voces-flow.md](references/voces-flow.md). Costos: [references/creditos.md](references/creditos.md).

## Gasta pocos tokens sin perder control

- Lee Flow con JavaScript corto. Las capturas y `read_page` pesan mucho más.
- Si necesitas mirar, usa `scale: 0.5` en la captura: cuesta cerca de la cuarta parte.
- Agrupa acciones en `browser_batch`, un clip por lote: los lotes muy largos expiran. Antes de cada generación agrega una comprobación con JavaScript que lance un error si falta algo: detiene el lote sin gastar puntos.
- Para hacer varios clips parecidos usa «Reutilizar petición»; no armes voz e imagen cada vez.

## Cuatro reglas que evitan casi todos los fallos

1. **«Iniciar generación» exige un clic real.** Un `.click()` desde JavaScript no genera nada, y no da error. Usa el clic del ratón.
2. **No tomes capturas mientras haya un submenú abierto o el cursor sobre una tarjeta.** La captura se cuelga 30 s. No es un fallo de Flow: retira el cursor o lee por DOM con JavaScript. Si una captura se cuelga, reintenta una vez después de mover el cursor a una zona vacía.
3. **Las coordenadas del DOM no son las de los clics.** Divide por `window.innerWidth / ancho_de_la_captura`. Los menús se animan: lee las coordenadas 2 s después de abrirlos. Mejor aún, ubica los elementos con `find` o `read_page` y haz clic con su `ref`. No memorices coordenadas: cambian con el tamaño de ventana.
4. **La interfaz no siempre está en español.** Si la cuenta aparece en inglés, los equivalentes están en el mapa.

## Recetas

### Saldo

Clic en el avatar (`Información de la cuenta`). El panel muestra «N puntos de Google Flow», su fecha de renovación y «N puntos de IA». Cierra con Escape. Ese panel contiene el correo: no lo copies al informe.

Los **puntos de Google Flow** son del plan. Los **puntos de IA** se usan cuando aquellos se acaban y se pagan aparte: no los gastes sin permiso expreso.

### Crear y nombrar el proyecto

Pulsa el botón `Nuevo proyecto`. La URL pasa a `flow.google.com/project/<id>`: guárdala en `proceso.json`. Para renombrar, clic en el título arriba a la izquierda, `Ctrl+A`, escribe, `Enter`.

### Configurar la generación

Clic en `Activador de ajustes`, el botón con el resumen `Vídeo · 720p · 6 s ▭ x1`. Se abre un panel con:

- Pestañas `Imagen` y `Vídeo`.
- En video: `Fotogramas` o `Ingredientes`, proporción `16:9` o `9:16`, modelo, `360p` o `720p`, `4 s`, `6 s`, `8 s`, `10 s`, y `x1` a `x4`.
- En imagen: `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, modelo, `x1` a `x4`.
- Abajo, **«La generación consumirá N puntos»**. Léelo siempre antes de generar y regístralo.

Al cambiar de `Imagen` a `Vídeo` el modo puede saltar a `Ingredientes`. Comprueba que quede el que necesitas. Cierra con Escape.

La configuración se conserva en el proyecto, así que no hace falta repetirla si no cambia.

### Escribir el prompt

Clic en el cuadro `¿Qué quieres crear?` y escribe con el teclado. Escribe todo en una línea, también el JSON. Comprueba que el botón a la derecha quede activo.

### Agregar fotograma inicial o final

Con `Vídeo` y `Fotogramas`: clic en `Inicio` o `Fin`. Se abre «Selecciona una imagen de encuadre» con el buscador ya enfocado. Escribe el nombre del recurso y haz clic en su fila: queda puesto al instante y la miniatura reemplaza al botón `Inicio`.

### Agregar ingredientes

Con `Vídeo` e `Ingredientes` usa el botón `+` (`Añadir ingredientes a ventana para peticiones`) y espera unos 6 s: el panel tarda y bloquea la página mientras abre. Tiene las pestañas `Todo`, `Imágenes`, `Vídeos`, `Voces`, `Caracteres`, `Avatares` y `Subidas`, un buscador y un selector de proyecto para traer recursos de otro proyecto. Pulsa `Añadir a petición`. Hacer clic en una fila también la agrega y cierra el panel. Si después haces clic donde estaba el panel, abrirás un recurso de la cuadrícula y lo que escribas activará atajos: lee siempre las posiciones antes de cada clic.

También puedes escribir `@` y buscar el recurso o personaje por nombre.

### Hacer varios clips con los mismos ingredientes

`Reutilizar petición` recupera el prompt, la voz, la imagen y también **la calidad y duración** del clip de origen. Funciona con `.click()` desde JavaScript en la vista `Lote`, sin depender de coordenadas. Después enfoca el cuadro con JavaScript, pulsa `Ctrl+A` y escribe el prompt nuevo.

- Reutiliza siempre un clip con la calidad que quieres: reutilizar uno de 720p vuelve a poner 720p, y cuesta el doble.
- Antes de generar confirma que el cuadro tenga las **dos fichas**. Con el clip anterior aún cargando no restaura nada y el fallo no se ve.
- Nunca hagas clic en coordenadas fijas de la galería: se reacomoda y puedes abrir otra toma, donde lo que escribas activa atajos. Lee la posición por DOM justo antes.
- El panel de ajustes cambia de altura según el prompt: lee las posiciones cada vez.
- La vista en lista tiene un `Descargar` por fila que baja el tamaño original de inmediato. Ahí, `Lote de papelera` queda al lado: no hagas clic a ciegas.
- «No se ha podido cargar el vídeo» en una tarjeta puede ser solo la vista. Recarga la página antes de reintentar y gastar puntos otra vez.

### Agregar voz

Una voz solo funciona con `Omni 1.1 Flash` en `Ingredientes` y siempre junto a una imagen, personaje o video. Sigue [references/voces-flow.md](references/voces-flow.md).

### Subir archivos de la carpeta

`Subir` abre un selector nativo del sistema que Claude no puede manejar. Evítalo así, con archivos de máximo 10 MB en total:

1. Instala este puente con JavaScript en la pestaña:

```js
(() => {
  const p = HTMLInputElement.prototype;
  if (!window.__clickOriginal) window.__clickOriginal = p.click;
  p.click = function () {
    if (this.type === 'file') {
      const el = this;
      setTimeout(() => {
        if (!el.isConnected) document.body.appendChild(el);
        el.style.cssText = 'position:fixed;left:8px;top:8px;width:120px;height:30px;z-index:99999';
        el.setAttribute('aria-label', 'archivo-flow');
      }, 50);
      return;
    }
    return window.__clickOriginal.apply(this, arguments);
  };
  return 'listo';
})()
```

2. Clic real en el `+` de arriba a la derecha (`Menú para añadir contenido multimedia`) y luego en `Subir`.
3. Busca con `find` el elemento `archivo-flow` y usa la herramienta `file_upload` con su `ref` y la ruta del archivo.
4. El archivo aparece en `Subidas`.

Formatos aceptados: `.png .jpg .jpeg .webp .gif .heif .heic .mp4 .m4v .mov .3gp .avi`. Si la herramienta rechaza la ruta, el archivo debe estar en una carpeta conectada a la sesión. Si pesa más de 10 MB, redúcelo con ffmpeg primero o pídele a la persona que lo arrastre a Flow.

### Generar y vigilar

Comprueba antes que `Iniciar generación` no tenga `disabled`: si le falta un ingrediente no da error, simplemente no hace nada. Pasa el cursor sobre la ficha del ingrediente para leer el motivo.

Clic real en `Iniciar generación`. Aparece una tarjeta con el avance, por ejemplo `17 %`. Puedes lanzar varias seguidas sin esperar: corren en paralelo y una imagen tarda unos 15 s. Un clip de 4 s tardó cerca de 1 minuto: espera en tramos de 10 s.

Para vigilar sin capturas:

```js
JSON.stringify({
  enCurso: (document.querySelector('main')?.innerText.match(/\b\d{1,3}\s?%/g) || []),
  imagenes: [...document.images].filter(i => i.src.includes('flow-content.google')).length,
  menuVideos: /\bVídeos\b/.test(document.body.innerText)
})
```

Los clips no aparecen como `<video>` hasta pasar el cursor por encima: cuando `enCurso` quede vacío, revisa con una captura y con el cursor en una zona vacía. Si una tarjeta muestra error, lee el motivo, ajusta el prompt y reintenta hasta 2 veces. Si Flow bloquea el contenido dos veces, detente.

### Abrir el menú de un recurso

Pasa el cursor sobre la tarjeta. Arriba a la derecha aparecen el corazón, `Reutilizar petición` y `⋮` (`Más`). El menú trae `Marcar como favorito`, `Reutilizar petición`, `Añadir a la escena` o `Animar`, `Añadir a la petición`, `Descargar`, `Copiar`, `Cambiar nombre`, `Compartir`, `Publicar en YouTube`, `Definir portada del proyecto`, `Denunciar resultado` y `Mover a la papelera`.

### Renombrar la toma elegida

Antes de descargar, usa `Cambiar nombre` y ponle `clip-01`, `clip-02`. Flow nombra el archivo con el nombre del recurso más un código, por ejemplo `clip-01_7c9e63da.mp4`, así que renombrar es lo que permite identificar cada archivo después.

### Descargar

- **Todo el proyecto:** `Más opciones`, `Descargar proyecto`, espera 2 s a que aparezca el cuadro y confirma `Descargar`: un clic antes de tiempo no se registra. Baja un ZIP con el nombre del proyecto. Es la vía más rápida para fotogramas de storyboard. Imágenes a 768×1376 en 9:16.
- **Una pieza:** `⋮`, pasa el cursor por `Descargar`, y elige:
  - Imagen: `1K` tamaño original, `2K` resolución mejorada (1536×2752 en 9:16), `4K` solo con Ultra.
  - Video: `270p` GIF animado, `720p` tamaño original, `1080p` resolución mejorada, `4K` solo con Ultra.

Con la resolución mejorada Flow trabaja unos segundos y avisa «Se ha completado la mejora de resolución». El archivo llega a la carpeta de descargas de Chrome sin ningún cuadro de diálogo.

Un clip a 720p en 9:16 llega como 720×1280, 24 fps, con audio AAC a 48 kHz. Durante la producción baja **720p**, el tamaño original. Baja **1080p** solo cuando la persona pida escalar, de uno en uno: es gratis en Plus, Pro y Ultra, tardó unos 40 s en prepararse y llega como 1080×1920 con el sufijo `_1080p.mp4`. Espera a que el archivo aparezca en Descargas antes de seguir.

Tras cada descarga, copia el archivo más reciente de Descargas a `03-flow/NN.mp4` y comprueba con `ffprobe` que tenga la duración y la resolución esperadas.

### Pasar de un clip al siguiente con continuidad

1. Extrae el último fotograma del clip anterior (lo hace `igualar_y_unir.py --solo-inicio`, skill `acabado-hyperframes`).
2. Súbelo y úsalo como `Inicio` del clip siguiente.
3. Termina cada clip en una pose quieta, con la boca cerrada.

## Lo que no debes hacer

- No uses `Publicar en YouTube`, `Compartir` ni `Mover a la papelera` salvo pedido expreso.
- No cambies `Marca de agua visible` en el panel de la cuenta.
- No generes con `x2` a `x4` en video salvo que esté en el presupuesto: multiplica el costo.
- No toques proyectos anteriores de la persona.
