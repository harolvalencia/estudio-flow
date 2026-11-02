# Pantalla real

Una interfaz se muestra tal como es. Las imágenes y videos generados inventan botones y textos, y el alumno aprendería algo que no existe.

## Antes de capturar

1. Usa un **ambiente de pruebas** y datos ficticios. Si no existe, pide a la persona que lo prepare.
2. Inicia sesión antes de capturar. **Las contraseñas las escribe la persona, siempre fuera de cámara.**
3. Cierra pestañas, notificaciones, marcadores y correo.
4. Ventana a 1920×1080 y zoom del navegador al 125 % o 150 %, para que el texto se lea en un celular.

Si aparece un dato real, un nombre de cliente, un correo o una llave, detente: tacha o recaptura. Las barras laterales suelen mostrar historiales privados.

## Tres formas de obtener la pantalla

| Forma | Cuándo usarla | Cómo |
|---|---|---|
| **Capturas de Claude** | Sistemas web sin datos sensibles | Claude in Chrome: `computer` con `action: screenshot` y `save_to_disk: true` |
| **Capturas públicas** | Páginas públicas sin iniciar sesión | Chrome sin interfaz a doble densidad; ver abajo |
| **Grabación de la persona** | Animaciones, escritorio, sistemas internos | Herramienta Recortes de Windows o `Cmd+Mayús+5` en Mac; a `01-referencias/pantalla/` |

Para una página pública, a 3840×2160:

```
chrome --headless=new --hide-scrollbars --window-size=1920,1080 --force-device-scale-factor=2 --screenshot=captura.png URL
```

En Flow las capturas de Claude in Chrome pueden colgarse: revisa las reglas de la skill `flow-control`.

## Calidad

- Una captura se amplía hasta 1,7 veces sin verse borrosa. `armar_tutorial.py` avisa si la superas.
- Para un zoom de 2× en 1080p necesitas capturas a doble densidad, unos 3840 px de ancho.
- Antes de cada paso captura el estado inicial. Si el paso cambia la pantalla, usa una escena por estado.
- Comprueba que lo que se ve sea igual a la versión que usará el alumno.

## Dónde poner las marcas

En `tutorial.json`, `x` y `y` son fracciones de la imagen, de 0 a 1, medidas desde la esquina superior izquierda, y apuntan al **centro** del elemento. `ancho` y `alto` son el tamaño del elemento, también en fracciones.

Mide sobre la imagen real. Después de armar, mira un fotograma de cada marca: un recuadro corrido enseña mal.

## Grabaciones

Cada escena toma un trozo con `desde` y `hasta`. El tramo se acelera o se frena para durar lo que dura la voz, entre 0,5× y 3×. Si no alcanza, ajusta el guion o graba de nuevo. Muéstrala siempre más lenta que una persona experta.
