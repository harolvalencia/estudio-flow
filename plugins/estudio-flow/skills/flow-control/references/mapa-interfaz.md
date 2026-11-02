# Mapa de la interfaz de Flow

Verificado en vivo el 2 de noviembre de 2026 con una cuenta Pro en español. Los nombres entre comillas son los `aria-label` estables de los botones.

## Inicio (`flow.google.com`)

Galería de proyectos, botones `Flow Music` y `Flow TV`, botón `Nuevo proyecto`. Cada proyecto tiene iconos para editar el nombre y eliminar.

## Dentro de un proyecto

**Barra lateral:** `Todo el contenido multimedia`, `Imágenes`, `Vídeos`, `Caracteres`, `Escenas`, `Subidas`, `Biblioteca`, `Herramientas`, `Crear herramienta`, `Papelera`, `Ocultar`. Imágenes, Vídeos y Subidas solo aparecen cuando existe ese tipo de contenido.

**Barra superior:**

- Título editable (`Texto editable`) y su menú (`Más opciones del proyecto`).
- `Buscar` y `Opciones de filtrado y ordenación`.
- `+` (`Menú para añadir contenido multimedia`): `Subir`, `Nueva colección`, `Crear personaje`, `Nueva escena`.
- `Ayuda del producto`.
- `Ajustes`: modo de vista `Cuadrícula` o `Lote`, tamaño S/M/L, sonido al pasar el cursor, `Mostrar detalles del recuadro`, `Borrar petición al enviar`.
- `Más opciones`: `Descargar proyecto`, ayuda y registro de cambios.
- `Información de la cuenta`: saldo de puntos, `Crear avatar`, `Marca de agua visible`.

**Cuadro de petición:**

- `Inicio` y `Fin` en modo Fotogramas de video.
- Cuadro `¿Qué quieres crear?`.
- `+` (`Añadir ingredientes a ventana para peticiones`): pestañas `Todo`, `Imágenes`, `Vídeos`, `Voces`, `Caracteres`, `Avatares`, `Subidas`, buscador y selector de proyecto.
- `Agente`, que activa el agente propio de Flow. No lo uses: Claude ya dirige la producción y el agente gasta cuota diaria.
- `Activador de ajustes`.
- `Iniciar generación` y `Borrar petición`.

## Modelos en el selector

- Video: `Omni 1.1 Flash`, `Veo 3.1 - Lite`, `Veo 3.1 - Fast`, `Veo 3.1 - Quality`.
- Imagen: `Nano Banana Pro`, `Nano Banana 2 Lite`, `Nano Banana 2.1`.

## Qué modelo usar

| Necesidad | Modelo | Por qué |
|---|---|---|
| Fotogramas y storyboard | Nano Banana 2.1 | 0 puntos en el plan probado |
| Clip con diálogo o de 10 s | Omni 1.1 Flash en Ingredientes | Único con 10 s y voces; 4 s a 720p = 7 puntos |
| Prueba rápida | Omni a 360p | Mitad de precio; Pro y Ultra lo escalan a 720p sin costo |
| Clip mudo barato | Veo 3.1 Lite | Bajo costo, permite Extender |
| Toma heroica | Veo 3.1 Quality | Máxima calidad, 100 puntos |

## Compatibilidad por modelo (ayuda oficial de Flow)

| Modelo | Duración | Fotogramas | Ingredientes | Extender | Video a video |
|---|---|---|---|---|---|
| Veo 3.1 Lite | 4, 6, 8 s | Sí | Sí, solo 8 s | Sí, solo 8 s | No |
| Veo 3.1 Fast | 4, 6, 8 s | Sí | Sí, solo 8 s | No | No |
| Veo 3.1 Quality | 4, 6, 8 s | Sí | No | No | No |
| Omni Flash 1.1 | 4, 6, 8, 10 s | Sí | Sí | Próximamente | Hasta 10 s |

Todos admiten 16:9 y 9:16.

## Atajos útiles

`Ctrl+U` subir, `Ctrl+D` descargar en vista de edición, `Ctrl+G` agrupar en colección, `Mayús+I` solo imágenes, `Mayús+V` solo videos, `Mayús+U` solo subidas, `@` menú de recursos en el cuadro de petición, `Esc` volver a la cuadrícula.

## Escenas (Scenebuilder)

`⋮` en un clip, `Añadir a la escena`. Permite ordenar, recortar y previsualizar. Aquí no se usa para el montaje final: el montaje va en HyperFrames, donde hay control exacto de texto, marca y sonido.

## Equivalentes en inglés

| Español | Inglés |
|---|---|
| Nuevo proyecto | New project |
| Fotogramas | Frames |
| Ingredientes | Ingredients |
| Vídeo | Video |
| Imagen | Image |
| Iniciar generación | Start generation |
| Descargar | Download |
| Cambiar nombre | Rename |
| Añadir a petición | Add to prompt |
| Resolución mejorada | Upscaled |
