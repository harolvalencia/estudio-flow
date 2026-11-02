# Plantilla de tutorial.json

`armar_tutorial.py` convierte este archivo y `tiempos.json` en una composición de HyperFrames. Todas las rutas son relativas a `04-montaje/`.

```json
{
  "titulo": "Crea tu primer reporte",
  "formato": "16:9",
  "subtitulos": "pista",
  "volumen_banda": 0.36,
  "marca": {
    "nombre": "Innovaitors",
    "primario": "#1893F8",
    "acento": "#19E3E6",
    "fondo": "#02040A",
    "logo": "assets/img/logo-blanco.png",
    "fuente_titulo": "Clash Display",
    "fuente_texto": "Manrope",
    "fuentes": [
      {"familia": "Clash Display", "src": "assets/fonts/clash-700.woff2", "peso": 700},
      {"familia": "Manrope", "src": "assets/fonts/manrope-var.woff2", "peso": "200 800"}
    ]
  },
  "guion": ["Tramo 1, palabra por palabra.", "Tramo 2."],
  "escenas": []
}
```

`guion` tiene un texto por clip de voz, en el mismo orden que `03-flow/voz/`. `formato` acepta `16:9`, `9:16` y `1:1`. `subtitulos` acepta `pista` o `quemados`; usa `quemados` solo en piezas verticales.

## Escenas

Toda escena lleva `tipo` y `tramos`, el número del clip o una lista como `[3, 4]`. Si lleva `capitulo`, ahí empieza un capítulo. En el texto, `*palabra*` resalta y `|` cambia de línea en los títulos.

### apertura

```json
{"tipo": "apertura", "tramos": 1, "video": "assets/video/apertura.mp4", "sincronizar": true,
 "capitulo": "Qué vas a lograr", "etiqueta": "Tutorial · 3 minutos",
 "titulo": "Crea tu primer|*reporte*", "objetivos": ["Filtrar los datos", "Exportar a Excel"]}
```

Usa `video` con un clip de Flow 16:9, o `imagen` solo para ensayar. `sincronizar` hace que el video arranque donde arranca su voz: úsalo si alguien habla a cámara.

### pantalla

```json
{"tipo": "pantalla", "tramos": 2, "imagen": "assets/pantalla/reportes.png",
 "capitulo": "Abre Reportes", "paso": 1, "titulo": "Entra a Reportes",
 "marcas": [
   {"palabra": "Reportes", "x": 0.12, "y": 0.2, "ancho": 0.08, "alto": 0.04, "zoom": 2, "nota": "Menú *Reportes*"}
 ]}
```

Para una grabación usa `"video": "assets/pantalla/toma.mp4", "desde": 12.5, "hasta": 19`.

| Campo de marca | Qué hace |
|---|---|
| `palabra` | La marca ocurre cuando la voz dice esa palabra. Debe aparecer en el tramo |
| `en` | Segundo dentro de la escena, si no se usa `palabra` |
| `x`, `y` | Centro del elemento, en fracciones de la imagen |
| `ancho`, `alto` | Tamaño del recuadro, en fracciones |
| `zoom` | Acercamiento de la cámara |
| `clic` | `false` si solo se señala, sin clic |
| `nota` | Etiqueta junto al elemento |

Elige como `palabra` una que se pronuncie igual en español. Si `armar_tutorial.py` avisa que la voz no la dijo, cambia por otra palabra de la frase.

### idea

```json
{"tipo": "idea", "tramos": 5, "video": "assets/video/contexto.mp4", "etiqueta": "Error común",
 "titulo": "No exportes|*sin filtrar*", "texto": "El archivo saldría con todos los registros."}
```

`video` o `imagen` son opcionales. Úsalos con clips de Flow para dar riqueza a los cambios.

### pregunta

```json
{"tipo": "pregunta", "tramos": 7, "capitulo": "Comprueba", "pregunta": "¿Qué haces primero?",
 "opciones": ["Exportar", "Filtrar", "Imprimir"], "correcta": 1, "revelar": {"palabra": "correcta"}}
```

`correcta` empieza en 0. Di en el guion la frase que revela la respuesta y deja una pausa antes.

### cierre

Siempre es la última escena.

```json
{"tipo": "cierre", "tramos": 8, "video": "assets/video/cierre.mp4", "capitulo": "Tu turno", "palabra": "Crea",
 "frase": "Ya sabes|*hacerlo*", "boton": "Crea tu primer reporte", "texto": "empresa.com"}
```

En `palabra` entran el botón, el logo y el golpe musical.

## Prompt de un tramo de narración

La imagen de estos clips no se ve: solo se usa el audio. Agrega la voz guardada y cualquier imagen sencilla como ingrediente.

```json
{"shot":"fixed camera, no people","location":"plain dark background","subject":"the supplied image stays still","audio":"off-screen narrator voice, clean studio recording, no music, no ambience, no sound effects","duration":"10s","dialogue":{"language":"Spanish (Colombia)","script":[{"t":"0.2-9.4s","line":"Tu frase exacta."}],"rule":"say the script word by word, add nothing"},"avoid":"music, ambience, sound effects, people talking"}
```
