# Estudio Flow

Una productora de video con IA dentro de Claude para escritorio, para redes sociales, tutoriales y capacitaciones. Le cuentas qué necesitas y Claude revisa tu marca, te entrevista, propone ideas con storyboard interactivo, produce en Google Flow con Omni Flash y sus voces, termina el video con HyperFrames y te entrega el archivo final.

## Qué incluye

| Plugin | Qué hace |
|---|---|
| `estudio-flow` | 7 skills: dirección, control de Flow, storyboard, acabado, video formativo, informe y manual de marca |
| `hyperframes-skills` | Skills oficiales de [HyperFrames](https://github.com/heygen-com/hyperframes), de HeyGen, bajo Apache-2.0 |

## Novedades de la versión 1.6.0

- **Tutoriales en orden lógico:** recorre el sistema antes de escribir el guion, con un mismo caso de principio a fin, y valida que ningún paso use algo que aún no existe.
- **Video de referencia:** le das una dirección o un archivo, lo analiza y aplica lo que funcionó, sin copiar la pieza.
- **Estilos:** real, animación 3D, caricatura, plastilina, pizarra e infografía que se construyen al ritmo de la voz.
- **Cierre a tu medida:** pregunta, «pausa y hazlo tú», caso para decidir, resumen, invitación a usar la aplicación o siguiente lección.
- **Menos puntos de Flow:** prompts calculados con el ritmo real de la voz, clip piloto y revisión automática de cada toma antes de gastar otra.
- **Tu marca y tus imágenes:** usa los archivos que ya tengas en el Proyecto y las imágenes que le entregues.

Si vienes de una versión anterior, vuelve a pegar las instrucciones del Proyecto.

## Instalación en Claude

Necesitas Claude para escritorio con un plan de pago.

1. Abre **Customize** y entra a **Plugins**.
2. Pulsa **Add**, luego **Add marketplace** y **Add from a repository**.
3. Pega esta dirección y pulsa **Sync**:

   ```text
   https://github.com/harolvalencia/estudio-flow
   ```

4. Instala **estudio-flow** y **hyperframes-skills**.

Para recibir una versión nueva pulsa **Add → Manage marketplaces → ⋯ → Check for updates**. Revisa el commit que muestra: la sincronización automática puede tardar. Si vienes de una versión anterior a la 1.5.0, vuelve a pegar `instrucciones-del-proyecto.md` en tu Proyecto.

Si el marketplace no sincroniza, descarga los archivos `.plugin` de la [última versión](https://github.com/harolvalencia/estudio-flow/releases/latest) y súbelos con **Add → Upload plugin**.

En Claude Code:

```text
claude plugin marketplace add harolvalencia/estudio-flow
claude plugin install estudio-flow@estudio-flow
claude plugin install hyperframes-skills@estudio-flow
```

## Crear el Proyecto

1. En Claude, crea un Proyecto nuevo.
2. Pega en **Instructions** el contenido de [instrucciones-del-proyecto.md](instrucciones-del-proyecto.md).
3. Instala la extensión **Claude in Chrome** e inicia sesión en [Google Flow](https://flow.google.com).
4. En Claude para escritorio ve a **Configuración → General → Tareas → Navegador preferido** y elige Chrome.
5. Abre una sesión en el Proyecto y cuéntale qué video necesitas.

## Prueba en minutos

Para una clase o una demostración, escribe `Modo rápido` en el Proyecto y da la empresa, el color, la escena, la frase y la acción. Claude genera un solo clip de 8 s con voz y le agrega logo, frase y botón. Cuesta unos 12 puntos de Flow y no usa HyperFrames.

## Para producir el video final

Necesitas Node 22 o superior, ffmpeg y Python 3.13 con `numpy`, `pillow` y `faster-whisper`. Para que Claude trabaje en tu computador, instala también el plugin **Desktop Commander**: busca ese nombre y elige la fila que dice **Plugin** y `wonderwhy-er/desktopcommandermcp`. Claude avisará que podrá ejecutar código en tu computador sin preguntar: acepta solo en tu propio equipo.

En Windows, usa PowerShell:

```text
winget install OpenJS.NodeJS
winget install Gyan.FFmpeg
winget install Python.Python.3.13
python -m pip install numpy pillow faster-whisper
```

En Mac, usa la Terminal y [Homebrew](https://brew.sh):

```text
brew install node ffmpeg python@3.13
python3.13 -m venv ~/.estudio-flow
source ~/.estudio-flow/bin/activate
pip install numpy pillow faster-whisper
```

En Mac no existe el comando `python`, y Homebrew no deja instalar librerías en su Python. Por eso se crea `~/.estudio-flow`, y Claude lo usa solo.

## Licencia

Apache-2.0. Las skills de `hyperframes-skills` son trabajo de HeyGen; ver [plugins/hyperframes-skills/NOTICE.md](plugins/hyperframes-skills/NOTICE.md). Google Flow y Claude son productos de sus respectivas compañías, y este proyecto no está afiliado a ellas. Cada persona responde por lo que genera y por respetar los términos de esas plataformas.
