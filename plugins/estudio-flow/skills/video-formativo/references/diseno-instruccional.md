# Estándar del video formativo

Este estándar es obligatorio en tutoriales y capacitaciones. Reemplaza las reglas de ritmo y subtítulos del [estándar promocional](../../estudio-flow/references/mejores-practicas-video.md); las de marca, voz de Flow, sonido y cierre siguen vigentes con los ajustes de aquí.

Se apoya en los principios de aprendizaje multimedia de Richard Mayer y en el estudio de Guo, Kim y Rubin (2014) sobre 6,9 millones de sesiones de video en edX. Son orientación, no leyes: el estudio midió interés en cursos en línea, no aprendizaje en empresas. No cites porcentajes de mejora.

## 1. Una lección, un objetivo

- Cada video enseña una sola cosa que se pueda comprobar.
- Hasta 6 minutos. Si es más largo, divide en una serie.
- Antes de los pasos, enseña las palabras nuevas que vaya a necesitar.
- Cada paso parte de lo que dejó el anterior. El orden se fija y se aprueba antes del guion: [secuencia lógica](secuencia-logica.md).

## 2. Estructura

| Parte | Duración | Qué pasa |
|---|---|---|
| Apertura | 5 a 15 s | Muestra el resultado final y dice qué podrá hacer |
| Objetivos | Dentro de la apertura | Dos o tres, escritos y dichos |
| Pasos | 80 % del video | Decir, mostrar, señalar. Uno por vez |
| Error común | 5 a 10 s | Lo que más falla y cómo evitarlo |
| Final elegido | 5 a 15 s | Lo que eligió la persona: pregunta, «pausa y hazlo tú», caso, resumen, invitación o siguiente lección |
| Cierre | 4 a 8 s | Frase inspiradora, acción dicha y escrita, logo y clímax |

## 3. Enseñar con imagen y voz

- **Una cosa a la vez.** Divide en pasos cortos y numéralos.
- **Señala.** Cada instrucción lleva zoom, foco o marca sobre lo que se nombra.
- **Al mismo tiempo.** La marca aparece cuando la voz dice la palabra, no antes ni después.
- **Cerca.** La etiqueta va al lado de lo que explica.
- **Nada que distraiga.** Quita lo que no enseñe: adornos, música bajo la explicación, anécdotas.
- **No leas la pantalla.** En pantalla van palabras clave, no el párrafo que dice la voz.
- **Háblale a una persona.** «Pulsa Guardar», no «el usuario debe pulsar Guardar».
- **Alterna.** Un presentador o personaje breve, gráficos y pantalla sostienen la atención mejor que solo diapositivas.

## 4. Ritmo

- Hasta 2,3 palabras por segundo, más lento que un reel.
- Deja 1 a 3 s tras una acción para que se vea el resultado.
- Cada imagen fija lleva movimiento que enseña. Máximo 8 s sobre un mismo cuadro sin ningún cambio.

## 5. Épico donde corresponde

El video formativo también debe verse espectacular, pero la espectacularidad no compite con el aprendizaje:

- **Apertura, cambios de capítulo y cierre:** clips de Flow en el estilo elegido, o una pizarra o infografía que se construye, con luz, escala y música. Aquí sí es épico.
- **Durante un paso:** limpio y exacto. La riqueza visual sale de la cámara que entra a la interfaz, del foco y de los gráficos que explican.
- La música suena en la apertura y el cierre. Bajo la explicación solo queda la voz.

## 6. Subtítulos y accesibilidad

- En 16:9 los subtítulos van en una pista aparte `.srt` o `.vtt`, que cada persona activa si la necesita. Así no se repite en pantalla lo que dice la voz.
- En 9:16 para celular van quemados en el video.
- Entrega transcripción por capítulos.
- Di con palabras lo que ocurre en pantalla. Quien no ve bien debe poder seguir el video.
- Contraste alto y letra mínima de 28 px en 1080p.

WCAG 2.2 exige subtítulos para video pregrabado desde el nivel A y audiodescripción en el nivel AA. Si la organización debe cumplir AA, una transcripción no basta: avísalo y confirma cómo lo resolverá.

## 7. Cómo termina

Lo decide la persona en la entrevista. Va antes del cierre:

| Final | Escena | Cuándo conviene |
|---|---|---|
| Pregunta de comprobación | `pregunta` | Hay evaluación o el error sale caro |
| «Pausa y hazlo tú» | `practica` | Puede practicar mientras ve el video |
| Caso para decidir | `pregunta` con otra etiqueta | Enseña a tomar decisiones |
| Resumen de los pasos | `resumen` | Lo va a consultar más de una vez |
| Invitación a usar la aplicación | Solo `cierre` | El objetivo es que empiece a usarla |
| Siguiente lección | Solo `cierre` | Hace parte de una serie |

Si hay pregunta, prueba el objetivo, no un detalle, y las opciones incorrectas son errores reales, no bromas.

## 8. Cierre

Siempre es la última escena y siempre termina en alto, sea cual sea el final elegido. Mantiene la fórmula `Beneficio inspirador + verbo + acción concreta`, pero la acción es **practicar, usar la aplicación o seguir aprendiendo**, no comprar.

| Débil | Fuerte |
|---|---|
| «Gracias por ver este video» | «Ya sabes hacerlo. Crea ahora tu primer reporte.» |
| «Eso es todo» | «Listo para tu turno. Abre el sistema y prueba este paso.» |
| «Ya puedes entrar» | «Tu primer reporte está a un clic. Entra hoy a la aplicación.» |

## 9. Control

```
python _estudio/control_final.py 05-final/<video>.mp4 --tipo formativo --cierre 4 --guion 04-montaje/guion.txt
```

En Mac y Linux, cambia `python` por el valor de `comando_python` que da `verificar_entorno.py`.

Permite pausas de hasta 3,5 s para mirar la pantalla y hasta 8 s sobre un cuadro, y exige que la voz siga el guion.

## Fuentes

- [Mayer (2021), principios para videos instructivos](https://www.x-mol.com/paper/1388220828299059200)
- [Guo, Kim y Rubin (2014)](https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf)
- [WCAG 2.2, documentos explicativos](https://www.w3.org/WAI/WCAG22/Understanding/)
