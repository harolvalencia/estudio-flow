---
name: storyboard-interactivo
description: "Convierte una o varias propuestas de video en un artefacto interactivo donde la persona ve cada idea como un animatic dentro de un teléfono, compara escenas, tiempos y puntos, y decide. Úsala en la etapa de propuestas de una producción de Estudio Flow o cuando alguien pida ver un storyboard."
---

# Storyboard interactivo

Cada propuesta se ve como un animatic real: fotogramas generados en Flow, ritmo, texto en pantalla, área segura y costo.

## Pasos

1. Deja los fotogramas en `02-storyboard/` con nombres `a1.jpg`, `a2.jpg`, `b1.jpg`. Usa 3 a 6 escenas por propuesta. Genéralos con Nano Banana 2.1 (0 puntos).
2. Escribe `02-storyboard/plan.json` con el formato de abajo. El texto en pantalla es el definitivo, no un relleno.
3. Ejecuta:

```
python _estudio/armar_storyboard.py 02-storyboard/plan.json
```

   En Mac y Linux, cambia `python` por el valor de `comando_python` que da `verificar_entorno.py`.

4. Publica `02-storyboard/storyboard.html` como artefacto. Si la sesión no permite artefactos, ábrelo en Chrome.
5. Dile a la persona que elija abajo, copie su decisión y la pegue en el chat. La página no puede escribir en la conversación.

## plan.json

```json
{
  "pieza": "Reel Bootcamp Promptotyping",
  "formato": "9:16",
  "duracion_s": 15,
  "objetivo": "Agendar diagnósticos",
  "ritmo": 2.2,
  "marca": {"nombre": "Innovaitors", "primario": "#1893F8", "acento": "#00C2D1", "logo": "logo-blanco.png"},
  "propuestas": [
    {
      "id": "A",
      "nombre": "De la servilleta al prototipo",
      "resumen": "Una idea cobra vida en 15 segundos",
      "concepto": "Qué pasa en el video, en dos frases.",
      "porque": "Por qué sirve para este objetivo y este público.",
      "estilo": "Animación 3D de película",
      "referente": "Del video de referencia toma el gancho con una pregunta en el primer segundo.",
      "tono": "Épico",
      "voz": "Sulafat, cálida y segura",
      "tecnica": "Clips Omni + títulos",
      "escenas": [
        {
          "inicio": 0, "fin": 3,
          "imagen": "a1.jpg",
          "descripcion": "Qué se ve",
          "texto": "Texto en pantalla",
          "locucion": "Lo que dice la voz en esta escena",
          "audio": "Música y efectos",
          "flow": "Omni 6 s, Ingredientes + voz",
          "puntos": 10
        }
      ]
    }
  ]
}
```

Cada escena lleva `locucion`, y la última también `"cta": true`. El script rechaza el plan si falta alguna, si una frase no cabe en su tiempo o si no hay cierre. Solo usa `"sin_voz": true` en el plan si la persona lo pidió.

`ritmo` son las palabras por segundo para comprobar que la locución quepa. Usa 2,2 mientras no hayas medido la voz. `estilo` y `referente` son opcionales: el segundo solo si hay un video de referencia.

Para un tutorial o capacitación agrega `"tipo": "formativo"`, `"objetivos"` con la lista de lo que podrá hacer la persona, `"fuente"`, `"valida"`, `"secuencia"` con los títulos de los pasos aprobados y `"cierre_formativo"`: `pregunta`, `practica`, `caso`, `resumen`, `invitacion` o `siguiente`. Cada escena lleva `"origen"` (`pantalla`, `flow` o `grafico`) y puede llevar `"paso"`. Si el final es `pregunta`, `practica` o `caso`, al menos una escena lleva `"practica": true`. El script rechaza el plan si falta algo, si los pasos van en desorden o si la lección pasa de 6 minutos, salvo que lleve `"largo_aprobado": true`.

`formato` acepta `9:16`, `16:9`, `1:1` y `4:5`. Las escenas no deben dejar huecos: cada `inicio` es el `fin` de la anterior. El logo es opcional y debe servir sobre fondo oscuro.

## Calidad

- Si hay varias propuestas, deben ser videos distintos, no versiones del mismo.
- El primer cuadro de cada propuesta debe funcionar como gancho.
- Revisa la ortografía del texto en pantalla antes de publicar.
- Si la persona pide otras, conserva el archivo anterior como `storyboard-ronda1.html` y arma una ronda nueva.
