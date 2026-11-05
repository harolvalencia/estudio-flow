---
name: informe-pdf
description: "Genera el documento PDF del proceso de una producción de Estudio Flow: encargo, propuestas, decisión, puntos usados, prompts, montaje y archivos finales. Úsala solo cuando la persona pida el informe del proceso: no hace parte de la entrega normal."
---

# Informe del proceso

El informe sale de los datos reales de `00-brief/proceso.json`. Si un dato falta, complétalo mirando los archivos, nunca inventándolo.

## Antes de generar

Comprueba que `proceso.json` tenga:

- `marca` con nombre, origen, colores y logo. El logo se ve sobre fondo oscuro: usa una versión clara.
- `voz` si la pieza lleva voz de Flow.
- `propuestas` con la elegida marcada en `elegida: true`.
- `clips` con prompt, modelo, intentos y puntos reales de cada toma.
- `montaje.elementos`: lo que se agregó, por ejemplo títulos, subtítulos, logo, música.
- `entregables`: copia la salida de `exportar_redes.py`.
- `lecciones`: qué funcionó y qué se haría distinto.

No incluyas correos, contraseñas ni saldos de la cuenta que no sean necesarios.

## Generar

```
python _estudio/generar_informe.py <carpeta>
```

En Mac y Linux, cambia `python` por el valor de `comando_python` que da `verificar_entorno.py`.

Deja el PDF en `06-informe/`.

## Revisar

Abre el PDF y revisa cada página: imágenes visibles, texto cortado, tablas y ortografía. Si algo falla, corrige `proceso.json` y vuelve a generar. Entrégalo solo cuando lo hayas revisado.
