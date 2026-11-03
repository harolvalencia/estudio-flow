---
name: manual-de-marca
description: "Consigue la marca de una compañía antes de crear cualquier pieza: pide su manual, o investiga su sitio web para extraer colores, tipografías, logo y tono. Si la compañía no tiene manual, pregunta si quiere recibir al final un manual de marca en PDF visualmente épico con lo investigado, usando imágenes de Google Flow. Úsala en toda producción de Estudio Flow y cuando pidan un manual de marca."
---

# Manual de marca

Ninguna producción avanza sin marca. Esto ocurre en la etapa 1, antes de la entrevista creativa.

## Paso 1. Pide siempre el manual

Pregunta: **«¿Tienes el manual de diseño de marca de la compañía?»**

- **Sí lo tiene:** pide que lo deje en `01-referencias/`. Léelo completo y pasa sus reglas a `00-brief/marca.json` con `"origen": "manual"`. Manda sobre cualquier otra fuente. No generes manual al final.
- **No lo tiene:** pide el **nombre de la compañía** y su **página web**. Investiga con el paso 2 y usa `"origen": "web"`.
- **Tampoco tiene web:** pide nombre, sector, a quién le vende, redes sociales y cualquier logo o pieza que exista. Revisa esas fuentes. Propón una dirección de marca y confírmala antes de producir. Usa `"origen": "nueva"`.

## Paso 2. Investiga la marca en la web

Abre el sitio en Chrome y recorre el inicio, «Nosotros» y una página de servicios. Extrae datos, no impresiones:

```js
(() => {
  const n = {}, f = {}, sumar = (o, k) => { if (k) o[k] = (o[k] || 0) + 1 };
  [...document.querySelectorAll('body *')].slice(0, 3000).forEach(e => {
    const s = getComputedStyle(e);
    sumar(n, s.backgroundColor); sumar(n, s.color); sumar(f, s.fontFamily.split(',')[0]);
  });
  const orden = o => Object.entries(o).filter(([k]) => k !== 'rgba(0, 0, 0, 0)').sort((a, b) => b[1] - a[1]).slice(0, 14);
  const logos = [...document.images].filter(i => /logo/i.test(i.src + i.alt)).slice(0, 6).map(i => i.src);
  const titulos = [...document.querySelectorAll('h1,h2')].slice(0, 10).map(x => x.innerText.trim());
  const botones = [...document.querySelectorAll('a,button')].map(b => b.innerText.trim()).filter(t => t && t.length < 40).slice(0, 12);
  return JSON.stringify({colores: orden(n), fuentes: orden(f), logos, titulos, botones});
})()
```

Después:

1. Toma capturas del sitio y guárdalas en `00-brief/marca/`.
2. Pasa los `rgb()` a HEX. Ignora grises de texto y blancos: quédate con los colores que hacen reconocible la marca.
3. Descarga el logo oficial del sitio. Si solo existe en un color, crea la versión para fondos oscuros.
4. Copia frases reales del sitio: lema, promesa y textos de botones. Son el tono real.
5. Registra de dónde salió cada dato en `fuentes`.

No inventes misión, cifras, clientes ni premios. Lo que no aparezca va en `pendientes`.

## Paso 3. Escribe marca.json

Guarda `00-brief/marca.json`:

```json
{
  "empresa": "Nombre",
  "sitio": "https://...",
  "origen": "manual | web | nueva",
  "fecha": "2026-11-02",
  "lema": "Frase real de la marca",
  "esencia": {"proposito": "", "promesa": "", "publico": "", "personalidad": ["Práctica", "Cercana"]},
  "voz": {"tono": "", "decimos": ["Frase real"], "evitamos": ["Lo que no suena a la marca"]},
  "colores": [
    {"nombre": "Noche", "hex": "#02040A", "rol": "Fondo", "uso": 60},
    {"nombre": "Cian", "hex": "#00C2D1", "rol": "Acento", "uso": 25}
  ],
  "degradado": ["#19E3E6", "#1893F8"],
  "tipografias": [
    {"nombre": "Clash Display", "rol": "Títulos", "archivo": "00-brief/marca/fuentes/clash-700.woff2", "peso": 700},
    {"nombre": "Manrope", "rol": "Textos", "google": "Manrope", "peso": 400}
  ],
  "logo": {"oscuro": "00-brief/marca/logo-blanco.png", "claro": "00-brief/marca/logo-azul.png", "simbolo": "00-brief/marca/simbolo.png"},
  "imagenes": {"portada": "00-brief/marca/portada.jpg", "esencia": "...", "color": "...", "imagineria": ["a.jpg", "b.jpg", "c.jpg"], "cierre": "..."},
  "imagineria": {"estilo": "Descripción del estilo visual", "prompt_base": "Fragmento en inglés para Flow", "evitar": "Qué no debe aparecer"},
  "voz_flow": {"nombre": "Sulafat (personalizado)", "base": "Sulafat", "interpretacion": "Cómo debe sonar"},
  "aplicaciones": ["05-final/portada.jpg"],
  "fuentes": [{"dato": "Colores y tipografías", "origen": "Estilos del sitio web"}],
  "pendientes": ["Confirmar con la compañía el Pantone oficial"]
}
```

Usa `marca.json` para todo: storyboard, títulos, montaje y prompts de Flow.

## Paso 4. Genera el manual solo si la persona lo pide

Si `origen` es `web` o `nueva`, pregunta una sola vez, después de confirmar la marca: **«No tienes manual de marca. ¿Quieres que al final te entregue uno en PDF? Toma unos 4 minutos más y no gasta puntos.»** Guarda la respuesta en `proceso.json`, en `alcance.manual_pdf`. Si no responde, no lo generes. Si `origen` es `manual`, tampoco.

Si dice que sí, en la etapa 7:

1. Crea en Flow un proyecto `Marca - <empresa>`. Genera con Nano Banana 2.1, que cuesta 0 puntos, unas 6 imágenes con el `prompt_base` de la marca: portada 3:4 en 2K y las demás en 16:9. Termina cada prompt con `no text, no logos`.
2. Déjalas en `00-brief/marca/` y regístralas en `imagenes`.
3. Ejecuta:

```
python _estudio/generar_manual_marca.py <carpeta>
```

Deja `06-informe/Manual-de-Marca-<empresa>.pdf`.

4. Revisa cada página: logo legible, contraste, textos sin cortes y ortografía. Corrige `marca.json` y vuelve a generar.
5. Avísale a la persona qué datos son deducidos y cuáles debe confirmar. El manual es una propuesta basada en lo público: no reemplaza a uno oficial hasta que la compañía lo apruebe.
