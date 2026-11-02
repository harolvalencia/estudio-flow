# Formatos para redes sociales

Revisado el 2 de noviembre de 2026. Las plataformas cambian estos límites y las fuentes públicas no siempre coinciden: si la pieza roza un límite, comprueba el recortador de la propia aplicación.

| Destino | Formato | Resolución | Duración que conviene | Nota |
|---|---|---|---|---|
| TikTok | 9:16 | 1080×1920 | 15 a 60 s | Tiene la columna de botones más ancha |
| Instagram Reels | 9:16 | 1080×1920 | 15 a 90 s | Hasta 3 min para distribuirse como Reel |
| Instagram feed | 4:5 | 1080×1350 | 15 a 60 s | Ocupa más pantalla que el cuadrado |
| Instagram Historias | 9:16 | 1080×1920 | Hasta 60 s por tramo | Deja libre el tercio inferior si lleva enlace |
| YouTube Shorts | 9:16 | 1080×1920 | 15 a 60 s | Hasta 3 min |
| YouTube | 16:9 | 1920×1080 | Libre | Requiere miniatura aparte |
| Facebook Reels | 9:16 | 1080×1920 | 15 a 60 s | Algunas cuentas ya no tienen tope fijo |
| Facebook feed | 4:5 o 1:1 | 1080×1350 | 15 a 60 s | |
| WhatsApp Estados | 9:16 | 1080×1920 | Hasta 60 s | Algunas cuentas llegan a 90 s; lo más largo se corta en tramos |

## Área segura en vertical (1080×1920)

- 0 a 168 px: libre, ahí va la barra de estado y la búsqueda.
- 168 a 1330 px: aquí va **todo** el texto y el producto.
- 1330 a 1920 px: solo textura o decoración, ahí van la leyenda, el usuario y los botones.
- Sin texto bajo la columna de botones de la derecha (unos 150 px).
- Subtítulos: en la parte baja de la banda segura.
- Letra mínima: 28 px para lo que deba leerse.

## Archivo de entrega

- Contenedor MP4, video H.264 High, `yuv420p`, 30 fps, audio AAC a 48 kHz.
- Audio a −16 LUFS con pico de −1 dBTP.
- `+faststart` para que empiece a reproducirse rápido.
- Versión liviana para WhatsApp: recodifica el video y **copia** el audio. Recodificar el audio sube el pico.
- Ten en cuenta que Flow entrega 720p: descarga a 1080p con «Resolución mejorada» antes de montar.

Un horizontal no se aplasta ni se recorta a vertical: se recompone con otro encuadre.
