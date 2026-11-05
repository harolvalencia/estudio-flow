# Puntos de Flow

Fuente: ayuda oficial de Flow, consultada el 2 de noviembre de 2026, y el selector real con cuenta Pro. Los costos cambian: **el número que manda es el que muestra el panel de ajustes** en «La generación consumirá N puntos».

## Saldo por plan

| Plan | Puntos mensuales |
|---|---|
| Sin suscripción | 50 diarios, no se acumulan |
| AI Plus | 200 |
| AI Pro | 1.000 |
| AI Ultra de USD 100 | 10.000 |
| AI Ultra de USD 200 | 25.000 |

Los puntos mensuales tampoco se acumulan al siguiente ciclo. Sin suscripción, entre las 14:00 y las 17:00 UTC (9 a. m. a 12 m. en Colombia) puede que no se pueda generar video.

## Costo por generación

| Acción | Puntos |
|---|---|
| Omni Flash 720p | 7 (4 s), 10 (6 s), 12 (8 s), 15 (10 s) |
| Omni Flash 360p | 4 (4 s), 5 (6 s), 6 (8 s), 7 (10 s) |
| Veo 3.1 Lite | 10; 5 con Ultra |
| Veo 3.1 Fast | 20; 10 con Ultra |
| Veo 3.1 Quality | 100 |
| Editar un video | 40 |
| Escalar de 360p a 720p | Gratis en Pro y Ultra; en otro plan, mira lo que muestra Flow |
| Escalar de 720p a 1080p | Gratis en Plus, Pro y Ultra |
| Escalar a 4K | 50, solo Ultra |
| Imágenes | 0, con límite diario por modelo |
| Vista previa de voz y guardar voz | 0 |

El costo se multiplica por `x2`, `x3` o `x4`.

## Cómo presupuestar

`clips_flow.py preparar` lo calcula para las dos rutas:

```
puntos = (suma del costo de cada clip) × 1,3
```

El 30 % adicional cubre repeticiones. Mantenlo aunque un video real haya usado menos: es un solo caso. Para un reel de 25 s con clips de 8, 8, 6 y 6 s:

| Ruta | Base | Con margen | Qué permite |
|---|---|---|---|
| 360p escalado a 720p | 22 | 29 | Clips a 720p. Flow no ofrece 1080p desde 360p |
| 720p directo | 44 | 58 | Clips a 720p, con opción de bajarlos a 1080p |

La ruta de 360p se usó en un video real de 37 clips en 3D y se probó el 5 de noviembre de 2026 en caricatura, plastilina y persona realista, con el escalado gratis a 720p. En la persona realista la cara queda nítida, con un halo leve en el pelo. La persona elige en la etapa 3.

## Cómo gastar menos sin perder calidad

Lo que más ahorra es no fallar. En orden:

1. **Aprueba la imagen antes del clip.** Nano Banana cuesta 0 puntos. Si la persona ya tiene imágenes, mejor.
2. **Prueba la voz en la vista previa.** Cuesta 0 puntos y detecta las palabras mal dichas.
3. **Revisa los prompts.** `clips_flow.py preparar` rechaza gratis los errores que ya costaron puntos.
4. **Genera un piloto.** El clip más difícil, a 360p, antes de todos los demás.
5. **Lanza los clips de uno en uno.** Así un error no se repite en toda la pieza.
6. **Repara antes de regenerar.** Sigue [la tabla de arreglos](prompts-omni.md#qué-hacer-con-cada-fallo).

Dos detalles de costo: un clip de 8 s cuesta menos que dos de 4 s (a 360p, 6 contra 8 puntos), y `x2` a `x4` multiplican el costo sin descuento.

Ahorrar nunca es quitar clips visibles, luz, profundidad ni escala: el video debe seguir siendo épico.

## Costo por minuto de narración

Un video largo se narra con un clip de 10 s por tramo:

| Resolución del clip | Puntos por minuto | Con 30 % de margen |
|---|---|---|
| 720p | 90 | 117 |
| 360p, misma calidad de voz | 42 | 55 |

El tutorial de ejemplo, de 1:43 con 14 tramos, costó 117 puntos: apertura y cierre a 720p, el resto a 360p, una comparación de calidad y dos frases que hubo que rehacer. Escribe el guion completo antes de generar: cambiar una frase después cuesta otro clip.

Antes de producir, compara contra el saldo real.
