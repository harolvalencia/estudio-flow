---
name: video-formativo
description: "Produce tutoriales y videos de capacitación que enseñan de verdad: objetivos de aprendizaje, fuente validada, pantalla real, narración con voces de Flow, señalización, comprobación, subtítulos y capítulos. Úsala cuando alguien pida un tutorial, capacitación, inducción, curso, microlección, manual en video, explicación de un procedimiento o enseñar a usar un sistema."
---

# Video formativo

Un reel busca que alguien se detenga. Un video formativo busca que alguien **sepa hacer algo que antes no sabía**. Por eso cambia casi todo menos la marca, la voz de Flow y el nivel de acabado.

Lee antes [el estándar formativo](references/diseno-instruccional.md). Esta skill reemplaza partes de la skill `estudio-flow`; las etapas y sus salidas no cambian de orden.

## Etapa 1. Entrevista formativa

Después de la marca, sigue [la entrevista formativa](references/entrevista-formativa.md). No propongas nada sin estas cuatro cosas:

1. **Objetivo observable:** qué podrá hacer la persona al terminar. Se escribe con un verbo que se pueda comprobar: crear, configurar, reportar. Nunca «entender» ni «conocer».
2. **Público y punto de partida:** qué sabe ya y qué herramienta usa.
3. **Fuente:** el manual, procedimiento, norma, grabación o experto de donde sale el contenido.
4. **Quién valida:** la persona que aprueba que los pasos son correctos.

Si no hay fuente, pide una. **Nunca inventes pasos, valores, normas ni políticas.** Si el tema afecta seguridad, salud, dinero o cumplimiento legal, el guion no se produce sin el visto bueno escrito de quien valida.

Si el contenido no cabe en una lección de hasta 6 minutos, propón una serie: cada lección con su propio objetivo.

**Salida:** `00-brief/brief.md` con objetivos, fuente y validador; en `proceso.json`, `brief.tipo = "formativo"`.

## Etapa 2. Tres propuestas didácticas

Las tres propuestas cambian el **formato didáctico**, no solo la estética. Elige de [formatos didácticos](references/formatos-didacticos.md) los que sirvan para el objetivo.

1. Escribe el guion por tramos: cada tramo es una idea, hasta 10 s, 22 palabras como máximo.
2. Estructura: resultado primero, objetivos, pasos, error común, comprobación, cierre con práctica.
3. Marca en cada escena su `origen`: `pantalla`, `flow` o `grafico`.
4. Haz los fotogramas: capturas reales para `pantalla`, Nano Banana 2.1 para `flow`.
5. Arma el storyboard con `"tipo": "formativo"`, `objetivos`, `fuente` y `valida`. El formato por defecto es 16:9.

## Etapa 3. Validación y presupuesto

Además de elegir la propuesta, quien valida aprueba el guion **palabra por palabra**. Guarda esa aprobación en `proceso.json`, en `brief.validacion`. Después de grabar la voz, cambiar una frase cuesta puntos.

El presupuesto usa [la tabla de narración](../flow-control/references/voces-flow.md#narración-larga-por-tramos). Dile a la persona cuántos puntos cuesta cada minuto antes de que apruebe.

## Etapa 4. Material y voz

**Pantalla real.** Sigue [pantalla real](references/pantalla-real.md). Una interfaz nunca se genera con IA: Flow la deforma y el alumno aprendería botones que no existen.

**Clips de Flow.** Úsalos para la apertura, las escenas de contexto, el presentador y el cierre. Nunca para mostrar cómo se hace un procedimiento técnico: un casco mal puesto en un clip enseña a ponérselo mal. Si un clip muestra un procedimiento, quien valida debe aprobarlo.

**Voz.** Genera un clip por tramo en `03-flow/voz/` y compara cada transcripción contra el guion. Luego únelos:

```
python _estudio/narracion_desde_clips.py 03-flow/voz --salida 04-montaje/assets/audio/voz.wav --tiempos 04-montaje/tiempos.json --guion 04-montaje/tutorial.json
```

La voz manda el tiempo: cada escena dura lo que dura su narración.

## Etapa 5. Montaje

Crea el proyecto con `npx hyperframes init 04-montaje --example blank --resolution landscape --non-interactive --skip-skills`, escribe `04-montaje/tutorial.json` con [la plantilla](references/plantilla-tutorial.md) y arma todo:

```
python _estudio/armar_tutorial.py 04-montaje/tutorial.json --tiempos 04-montaje/tiempos.json
```

Crea la composición, la música suave, los barridos, los clics y el golpe del cierre. Después sigue la skill `acabado-hyperframes` desde «Comprobar». Lee los `avisos`: dicen qué captura se verá borrosa y qué palabra no encontró la voz. Corrige esos puntos; no los ignores.

Revisa que cada marca caiga exactamente sobre su botón. Mira los fotogramas de cada escena: una marca corrida enseña mal.

## Etapa 6. Control y material de apoyo

```
python _estudio/control_final.py 05-final/<video>.mp4 --tipo formativo --cierre 4 --guion 04-montaje/guion.txt
python _estudio/kit_formativo.py 05-final/<video>.mp4 --guion 04-montaje/guion.txt --linea 04-montaje/linea-de-tiempo.json
```

El primero rechaza el video si la voz no sigue el guion. El segundo deja subtítulos `.srt` y `.vtt`, capítulos y transcripción.

Exporta con `exportar_redes.py --sufijo 16x9`. No uses la versión liviana de WhatsApp para una lección con pantalla: la compresión borra el texto pequeño. Si la lección se usará en celular, recompón una versión 9:16 con `"formato": "9:16"` y `"subtitulos": "quemados"`.

## Etapa 7. Entrega

Además del video y el PDF del proceso, entrega en `05-final/`:

- Subtítulos `.srt` y `.vtt`.
- Capítulos para la descripción de YouTube.
- Transcripción, que también sirve como alternativa accesible.
- `guia-rapida.md`: los pasos en una página y las preguntas de comprobación con su respuesta.

Di con claridad lo que no incluye. El paquete SCORM no se genera: la mayoría de plataformas aceptan MP4 con subtítulos VTT, y si la tuya exige SCORM debe empaquetarse con su herramienta.

## Reglas que no se negocian

- Sin fuente no hay guion. Sin validación no hay producción.
- Interfaces siempre reales, nunca generadas.
- Datos de prueba en pantalla. Nunca clientes, contraseñas, llaves ni correos reales. Las credenciales las escribe la persona fuera de cámara.
- Decir lo que se ve: «pulsa Guardar, arriba a la derecha», no «pulsa aquí». Así el video también sirve a quien no ve bien.
- Sin afirmaciones de cumplimiento legal que quien valida no haya confirmado.
