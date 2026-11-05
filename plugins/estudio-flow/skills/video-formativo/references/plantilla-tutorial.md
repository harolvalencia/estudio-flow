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

Una pieza promocional agrega `"banda": {"perfil": "epico", "continua": true}`: música épica de principio a fin. Sin ese campo, suena suave en la apertura y el cierre.

## Escenas

Toda escena lleva `tipo` y `tramos`, el número del clip o una lista como `[3, 4]`. Con `"pausa_despues": 1.5` queda ese silencio tras la voz: úsalo donde la persona deba leer, copiar un comando o ver un resultado. Si lleva `capitulo`, ahí empieza un capítulo. En el texto, `*palabra*` resalta y `|` cambia de línea en los títulos.

### apertura

```json
{"tipo": "apertura", "tramos": 1, "video": "assets/video/apertura.mp4", "sincronizar": true,
 "capitulo": "Qué vas a lograr", "etiqueta": "Tutorial · 3 minutos",
 "titulo": "Crea tu primer|*reporte*", "objetivos": ["Filtrar los datos", "Exportar a Excel"]}
```

Usa `video` con un clip de Flow 16:9, o `imagen` solo para ensayar. Sin ninguno, el fondo es un degradado de la marca: úsalo solo en pizarra o infografía si el presupuesto no alcanza para un clip. `sincronizar` hace que el video arranque donde arranca su voz: úsalo si alguien habla a cámara.

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

### comandos

Para lo que la persona debe escribir tal cual. Es una tarjeta con los comandos exactos, sin imitar la ventana de ningún programa.

```json
{"tipo": "comandos", "tramos": 8, "paso": 5, "titulo": "Instala las herramientas", "encabezado": "Abre *PowerShell* y ejecuta",
 "etiqueta": "Windows", "comandos": ["winget install OpenJS.NodeJS", "winget install Gyan.FFmpeg"],
 "al_decir": ["Node", "FFmpeg"], "nota": "Texto de apoyo bajo los comandos."}
```

Cada comando aparece cuando la voz dice su palabra de `al_decir`. Comprueba antes que los comandos funcionen de verdad: quien vea el video los va a copiar.

### pregunta

```json
{"tipo": "pregunta", "tramos": 7, "capitulo": "Comprueba", "pregunta": "¿Qué haces primero?",
 "opciones": ["Exportar", "Filtrar", "Imprimir"], "correcta": 1, "revelar": {"palabra": "correcta"}}
```

`correcta` empieza en 0. Di en el guion la frase que revela la respuesta y deja una pausa antes. Para un caso, usa `"etiqueta": "¿Qué harías?"`.

### practica y resumen

```json
{"tipo": "practica", "tramos": 7, "capitulo": "Tu turno", "titulo": "Crea tu *primer reporte*", "pausa_despues": 3,
 "puntos": ["Abre Reportes", "Filtra por mes", "Exporta a Excel"], "al_decir": ["Reportes", "mes", "Excel"]}
```

`practica` numera los puntos y muestra «Pausa el video y hazlo tú», que se cambia con `aviso`. `resumen` lleva los mismos campos y marca cada punto con un chequeo. Cada punto entra cuando la voz dice su palabra de `al_decir`. Aceptan `etiqueta`, y `video` o `imagen` de fondo.

### construccion

Pizarra o infografía: un lienzo grande que se construye al ritmo de la voz. Al final la cámara se aleja, se ve todo y la luz sube. Agrega `pausa_despues` de unos 2 s para esa revelación.

```json
{"tipo": "construccion", "tramos": [3, 4], "capitulo": "Cómo funciona", "estilo": "pizarra", "tema": "oscuro", "pausa_despues": 2,
 "lienzo": {"ancho": 1.6, "alto": 1.6}, "paso": 2, "titulo": "El proceso",
 "elementos": [
   {"tipo": "dibujo", "imagen": "assets/dibujos/idea.png", "x": 0.25, "y": 0.3, "ancho": 0.25, "palabra": "idea"},
   {"tipo": "texto", "texto": "Parte de una *idea*", "x": 0.25, "y": 0.55, "palabra": "parte"},
   {"tipo": "flecha", "de": [0.42, 0.3], "a": [0.62, 0.3], "palabra": "luego"},
   {"tipo": "dato", "valor": "01", "etiqueta": "Mapeo", "detalle": "Dónde atacar primero", "x": 0.76, "y": 0.3, "ancho": 0.3, "palabra": "mapeo"},
   {"tipo": "barra", "etiqueta": "Avance", "texto": "70 %", "valor": 0.7, "x": 0.5, "y": 0.75, "ancho": 0.5, "palabra": "avance"}
 ]}
```

| Campo | Qué hace |
|---|---|
| `estilo` | `pizarra` (cuadrícula) o `infografia` (puntos) |
| `tema` | `oscuro`, recomendado para lo épico, o `claro`. En claro se oculta el logo pequeño de esa escena |
| `lienzo` | Tamaño en veces la pantalla. Usa el mismo valor en ancho y alto, o se verán bordes al alejar |
| `textura` | Imagen de fondo del tablero, en lugar de la cuadrícula. Con una pizarra de verdad se ve más épico |
| `mezcla` | Cómo se funde un dibujo: `screen` para fondo negro (por defecto en oscuro), `multiply` para fondo blanco (en claro), `normal` para PNG transparente |
| `x`, `y` | Centro del elemento, en fracciones del lienzo |
| `ancho` | Ancho del elemento, en fracciones del lienzo |
| `palabra` o `en` | Cuándo aparece, igual que una marca |
| `zoom`, `mover` | Acercamiento de la cámara, y `false` para que no vaya hasta ese elemento |
| `foco` | `[x, y]`: adónde apunta la cámara si no es al centro del elemento. Sirve para encuadrar un dibujo junto con sus textos |
| `tam`, `alineado` | En un texto: tamaño en píxeles, y `centro` o `izquierda`. `\|` cambia de línea |

En vertical deja los elementos en la mitad superior del lienzo: abajo van los subtítulos. Para escribir los textos con otra letra, agrega `fuente_mano` en `marca` y su archivo en `fuentes`.

### cierre

Siempre es la última escena.

```json
{"tipo": "cierre", "tramos": 8, "video": "assets/video/cierre.mp4", "capitulo": "Tu turno", "palabra": "Crea",
 "frase": "Ya sabes|*hacerlo*", "boton": "Crea tu primer reporte", "texto": "empresa.com"}
```

En `palabra` entran el botón, el logo y el golpe musical. `boton`, `texto` y `video` son opcionales. Para invitar a usar la aplicación usa `imagen` con una captura real, `boton` y la dirección en `texto`; la captura queda oscurecida y manda la marca. `"qr": "assets/img/qr.png"` agrega un código QR, solo si la persona lo entrega.

## Prompt de un tramo de narración

La imagen de estos clips no se ve: solo se usa el audio. Agrega la voz guardada y cualquier imagen sencilla como ingrediente. El prompt lo escribe `clips_flow.py preparar`, con `"clase": "narracion"`: calcula la duración y el tiempo de habla de cada frase. No lo escribas a mano.
