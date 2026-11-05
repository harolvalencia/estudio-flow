# Secuencia lógica

Una lección se entiende cuando cada paso parte de lo que dejó el anterior. Si el video usa un cliente que todavía no se ha creado, la persona se pierde aunque cada paso esté bien explicado.

Esto se hace en la etapa 2, **antes de escribir el guion**. Después de grabar la voz, cambiar el orden cuesta puntos.

## 1. Recorre antes de escribir

- **Con acceso al sistema:** recórrelo de principio a fin en el ambiente de pruebas, como lo haría alguien nuevo. Anota en cada paso la pantalla, la acción y lo que queda después. Toma las capturas en esa misma pasada: así cada pantalla muestra lo que dejó el paso anterior.
- **Sin acceso:** saca el recorrido del manual, del procedimiento o de una grabación. Avísale a la persona que no lo recorriste y pide a quien valida que lo confirme con especial cuidado.

Las contraseñas las escribe la persona. Sigue [pantalla real](pantalla-real.md).

## 2. Elige un caso hilo

Es un solo registro de prueba que atraviesa toda la lección, por ejemplo: «La clienta de prueba Ana compra dos unidades». Lo que crea un paso es lo que usa el siguiente, y el resultado final es el de ese caso. Usa siempre datos ficticios.

## 3. Ordena por lo que cada paso necesita

1. Primero lo que otros pasos necesitan: entrar, luego los datos base, luego los movimientos y al final los reportes.
2. Si intervienen varios roles, sigue el orden en que el trabajo pasa de uno a otro y di cuándo cambia el rol.
3. Una palabra nueva se explica antes de usarla.
4. Las excepciones y las opciones avanzadas van después del camino normal, o en otra lección.

Si la lección explica **cómo funciona el sistema completo**, usa el formato «Recorrido del sistema» de [formatos didácticos](formatos-didacticos.md).

## 4. Escribe secuencia.json

Guárdalo en `00-brief/secuencia.json`:

```json
{
  "leccion": "Registrar una venta",
  "caso_hilo": "La clienta de prueba Ana compra dos unidades",
  "punto_de_partida": ["usuario con acceso"],
  "pasos": [
    {"n": 1, "titulo": "Entra al sistema", "pantalla": "Inicio de sesión", "accion": "Escribe usuario y contraseña", "resultado": "Menú principal", "necesita": ["usuario con acceso"], "deja": ["sesión"]},
    {"n": 2, "titulo": "Crea la clienta", "pantalla": "Clientes", "accion": "Pulsa Nuevo y completa los datos de Ana", "resultado": "Ana aparece en la lista", "necesita": ["sesión"], "deja": ["clienta"], "rol": "Vendedor"},
    {"n": 3, "titulo": "Registra la venta", "pantalla": "Ventas", "accion": "Elige a Ana y agrega dos unidades", "resultado": "Venta con número", "necesita": ["sesión", "clienta"], "deja": ["venta"]},
    {"n": 4, "titulo": "Consulta el reporte", "pantalla": "Reportes", "accion": "Filtra por hoy", "resultado": "La venta de Ana en el reporte", "necesita": ["venta"], "deja": []}
  ]
}
```

En `necesita` y `deja` escribe el mismo nombre para la misma cosa. `punto_de_partida` es lo que la persona ya tiene antes de empezar.

```
python _estudio/validar_secuencia.py 00-brief/secuencia.json
```

Si un paso necesita algo que se crea más adelante, el script lo rechaza y propone un orden válido.

## 5. Haz aprobar el orden

Muéstrale a quien valida la lista numerada y pregunta: **«¿Así lo haría alguien nuevo? ¿Falta o sobra un paso?»**. Guarda su respuesta en `proceso.json`, en `brief.secuencia_aprobada`. No sigas al storyboard sin esa aprobación.

Todas las propuestas enseñan estos mismos pasos en este mismo orden. Cambian el formato, el estilo y el tono, nunca la secuencia. Pon los títulos en `plan.json`, en `secuencia`, para que el storyboard muestre la lista completa.

## 6. Llévalo al guion

- **Conecta los pasos.** Cada uno dice de dónde viene: «Ya con la clienta creada, vamos a registrar su venta».
- **Muestra el resultado solo como avance.** Si la apertura lo enseña, dilo: «Esto es lo que vas a lograr». Después arranca desde cero.
- **Pon el error común donde ocurre.** Si depende de un paso, va justo después de ese paso.
- **Numera con `paso`.** Una escena por paso o varias, siempre en orden.

Cuando `tutorial.json` esté escrito, y antes de generar la voz:

```
python _estudio/validar_secuencia.py 00-brief/secuencia.json --tutorial 04-montaje/tutorial.json
```

Comprueba que el video enseñe los mismos pasos, en el mismo orden y sin saltos. El script mira el orden, no el sentido: mira también los fotogramas para confirmar que cada pantalla muestra lo que dejó el paso anterior.
