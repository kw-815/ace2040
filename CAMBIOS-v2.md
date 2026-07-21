# Cambios v1 → v2

## Correcciones
- **Pilares gigantes** — el `<div>` usaba una clase que no existía en el CSS. Cambiado a `objectives__grid` (grid de 4 columnas con `aspect-ratio 3/4.1`).
- **Framing del eje** — se veía flush contra el borde con una barra vertical suelta. Ahora es una tarjeta con fondo suave y padding uniforme.

## Mejoras UX
- **Nav sticky del home** — barra de índice que sigue el scroll, con 9 anclas.
- **Scroll suave** entre secciones.
- **Sección "Punto de partida" rediseñada**: 3 stats destacadas con número protagonista (Crecimiento 3,7% · Riesgo país <400 pb · Empleo 37,1%) + 7 stats compactas en formato horizontal tipo tabla-lista.
- **Blurb en tarjetas de pilar**: al pasar el cursor aparece un texto corto describiendo el pilar. En mobile queda visible por defecto.

## Cómo actualizar tu repo
Reemplazá en GitHub estos archivos:
- `index.html`
- `css/styles.css`
- `pages/pilar-1.html` a `pages/pilar-4.html`
