# REN3D realista · Kennedy

Copia de [REN3D](https://anasoficasca-code.github.io/REN3D/) cuyo modo principal es una **malla fotorrealista real** del territorio de Kennedy (Google Photorealistic 3D Tiles sobre CesiumJS), con los puntos del territorio como marcadores clicables.

Web: https://anasoficasca-code.github.io/REN3D-realista/

## Modos

- **Realista** (por defecto): malla 3D de Google, arrastrar para orbitar, rueda o pellizco para zoom, W A S D para volar. Tocar un marcador lleva la cámara a ese punto.
- **Maqueta 3D**: el modelo propio de Kennedy (edificios, árboles, agua, carros, aves) heredado de REN3D.
- **Noche** y **JUGAR** (modo pájaro y VR) siguen igual que en REN3D.

## Requisitos de la API de Google

- Usa la **Map Tiles API** con la llave `GKEY` de `index.html`.
- Debe mostrarse la atribución de Google (Cesium la dibuja abajo a la izquierda); no se debe ocultar.
- Recomendado: en Google Cloud, restringir la llave por referente HTTP a `anasoficasca-code.github.io/*` y a esa sola API.

## Calidad

- PC: resolución nativa, MSAA x4, error de pantalla 6 px.
- Celular: resolución limitada a 1,5x, sin MSAA, error de pantalla 20 px.

## Publicar

GitHub → repo `REN3D-realista` → Settings → Pages → Deploy from branch → `main` / `(root)`.
