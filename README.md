# REN3D realista · Maqueta de Kennedy

Maqueta 3D de Kennedy (Bogotá) sobre la **malla fotorrealista de Google** (Google Photorealistic 3D Tiles), cargada dentro de la misma escena Three.js que el modelo propio.

Web: https://anasoficasca-code.github.io/REN3D-realista/

## Qué es cada cosa

- **Fondo:** la malla de Google (foto real, fotogrametría aérea) se dibuja primero y luego se borra la profundidad. Es solo un fondo fotográfico: tiene errores de altura de varios metros y no puede tapar nada del modelo.
- **Encima, el modelo propio, siempre visible:** vías, aceras, parques, agua animada, edificios (`data3d/buildings.json`, 243 mil huellas con altura, paleta residencial y techos), árboles 3D reales con niveles de detalle (`data3d/real3d.js`), carros con las trayectorias reales de `kennedy_vehiculos.json`, peatones y aves de los humedales.
- **Máscara de huellas:** donde hay un edificio del modelo se recorta en el shader lo que Google levanta (`construirMascara`), para que no asome su versión "derretida".
- **Arranque rápido:** todos los datos se descargan a la vez y la pantalla de carga se cierra en cuanto están los edificios y las capas; la foto de Google entra sola cuando ya trae detalle.
- **Alineación:** el modelo de Rhino se georreferenció contra las calles de OpenStreetMap (solo traslación, sin giro ni inversión, error de pocos metros; ver `GEO` en `index.html`). La malla de Google se coloca en ese mismo sistema y se calibra al suelo midiendo su altura real alrededor de la cámara.
- **Botones:** Maqueta 3D, Noche y JUGAR (modo pájaro y VR).

## Límites conocidos

- Los edificios del modelo tienen color por edificio y techos, pero no fachadas fotográficas.
- Modo de diagnóstico: `?debug=1` muestra el estado de la malla; `?solo=malla` omite árboles, carros y aves (para probar en equipos lentos).
- La malla de Google es fotogrametría aérea: a nivel de calle las fachadas se ven borrosas y más aún en zonas de poca resolución. No se usan fotos de Street View: su licencia no permite descargarlas ni convertirlas en texturas.
- Los carros, árboles y peatones se asientan a una altura de suelo constante; donde el terreno fotográfico se desvía unos metros pueden quedar ligeramente hundidos o flotando.
- La malla de Google no se puede editar.

## Google Map Tiles API

- Llave `GKEY` en `index.html`, con **Map Tiles API** habilitada.
- La atribución de Google se muestra abajo a la izquierda y no debe ocultarse.
- Recomendado: en Google Cloud, restringir la llave por referente HTTP a `anasoficasca-code.github.io/*` y a esa sola API.
- Las teselas no se descargan ni se guardan en el repo: se piden en vivo.

## Técnica

- Three.js 0.160 y [3d-tiles-renderer](https://github.com/NASA-AMMOS/3DTilesRendererJS) 0.3.45 (plugins `GoogleCloudAuthPlugin` y `GLTFExtensionsPlugin`, decodificación Draco).
- Las teselas se muestran sin iluminar (la foto ya trae su luz) y con tono sin comprimir; en modo noche se oscurecen.
- Calidad: PC con error de pantalla 8 px; celular 22 px.

## Publicar

GitHub → repo `REN3D-realista` → Settings → Pages → Deploy from branch → `main` / `(root)`.
