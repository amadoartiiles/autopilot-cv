# Decisiones de técnicas y parámetros

Justificación de cada técnica y de cada parámetro del código (`CONTRATO.md` §6). El código no lleva
comentarios: lo que no se deduzca del nombre se explica aquí. Cada constante de
`autopilot/config.py` tiene su entrada.

Coordenadas: `(x, y)` en proporción al fotograma, con `(0, 0)` arriba a la izquierda y `(1, 1)`
abajo a la derecha. Con el vídeo de 1280×720 se traducen a píxeles multiplicando por `(1279, 719)`.

---

## Región de interés (ROI)

### Técnica: máscara trapezoidal fija aplicada sobre los bordes de Canny

| Campo | Contenido |
|---|---|
| **Qué** | Polígono de cuatro vértices que deja pasar solo la zona de la calzada donde aparece la marca vial derecha. |
| **Dónde** | `autopilot/roi.py` · `build_roi_mask`, `apply_region_of_interest` |
| **Por qué** | Canny marca bordes en toda la imagen: cielo, carteles, coches, quitamiedos, el borde diagonal de la zona que el vídeo trae oscurecida y los rótulos inferiores. Recortar antes de Hough evita que esos bordes generen segmentos falsos. Se usa un trapecio porque, por la perspectiva, el carril se estrecha hacia el horizonte. Descartadas: un rectángulo (mete el quitamiedos y la discontinua izquierda) y una ROI más ancha (mete el carril izquierdo). |
| **Situación del vídeo** | Todos los tramos. En la bifurcación (~f1650), el cambio de carril (~f1920) y el cebreado de la salida (~f2040) entran varias candidatas: las descarta el seguimiento, no la ROI. |

La máscara se construye **una sola vez** por vídeo (`build_roi_mask`), porque solo depende del
tamaño del fotograma, y se aplica en cada fotograma (`apply_region_of_interest`).

### `ROI_TOP_LEFT = (0.48, 0.42)` y `ROI_TOP_RIGHT = (0.62, 0.42)`

| Campo | Contenido |
|---|---|
| **Qué** | Lado superior del trapecio, a la altura del 42 % del fotograma (fila 302 en 720 p), entre el 48 % y el 62 % del ancho (columnas 614 y 793). |
| **Dónde** | `autopilot/config.py` → `autopilot/roi.py` · `compute_roi_vertices` |
| **Por qué** | A 0.42 el lado queda justo por debajo del horizonte y del borde de la zona oscurecida, de modo que fuera de la ROI quedan el cielo, los carteles y los coches lejanos. El tramo 0.48–0.62 es estrecho porque, cerca del horizonte, la marca derecha está cerca del centro; más a la izquierda entraría la discontinua del carril izquierdo. |
| **Situación del vídeo** | Recta y curvas: la marca derecha entra por el lado superior incluso en la curva cerrada (f1500). |

### `ROI_BOTTOM_RIGHT = (1.00, 0.74)`

| Campo | Contenido |
|---|---|
| **Qué** | Vértice inferior derecho, en el borde derecho del fotograma y al 74 % de la altura (columna 1279, fila 532). |
| **Dónde** | `autopilot/config.py` → `autopilot/roi.py` · `compute_roi_vertices` |
| **Por qué** | Cerca del coche, la marca derecha se abre hacia el borde derecho de la imagen; con x = 1.00 no se corta en las curvas hacia la derecha. El lado derecho del trapecio sigue la perspectiva de la calzada y deja fuera el quitamiedos. La altura se explica en `ROI_BOTTOM_LEFT`. |
| **Situación del vídeo** | Curva abierta (f750) y vía de salida (f2600). |

### `ROI_BOTTOM_LEFT = (0.40, 0.74)`

| Campo | Contenido |
|---|---|
| **Qué** | Vértice inferior izquierdo, al 40 % del ancho y al 74 % de la altura (columna 512, fila 532). |
| **Dónde** | `autopilot/config.py` → `autopilot/roi.py` · `compute_roi_vertices` |
| **Por qué** | 0.74 deja el lado inferior justo encima del capó: con 0.76 entraba su reflejo, que Canny detecta como borde horizontal. Además queda por encima de los rótulos del vídeo. x = 0.40 deja fuera la discontinua del carril izquierdo y el borde oscurecido de la parte superior izquierda. |
| **Situación del vídeo** | Todos. En el cambio de carril (f1920) entran trazos de la discontinua abajo a la izquierda; los resuelve el seguimiento. |

### `ROI_VERTEX_PROPORTIONS`

| Campo | Contenido |
|---|---|
| **Qué** | Tupla con los cuatro vértices en el orden superior izquierdo → superior derecho → inferior derecho → inferior izquierdo. |
| **Dónde** | `autopilot/config.py` → `autopilot/roi.py` · `compute_roi_vertices` |
| **Por qué** | `cv2.fillPoly` une los vértices en el orden en que se le pasan. Si se recorren en orden alrededor del contorno, el polígono no se cruza consigo mismo. |
| **Situación del vídeo** | Todos. |

### `ROI_MASK_INSIDE_VALUE = 255`

| Campo | Contenido |
|---|---|
| **Qué** | Valor de los píxeles de la máscara dentro del trapecio; fuera valen 0. |
| **Dónde** | `autopilot/config.py` → `autopilot/roi.py` · `build_roi_mask` |
| **Por qué** | Es el máximo de una imagen `uint8` y el valor que usa Canny para los bordes, así que la máscara es una imagen binaria del mismo tipo que la de bordes. `cv2.bitwise_and` solo exige que la máscara sea distinta de 0 donde se conserva la imagen; 255 es la convención y permite visualizar la máscara directamente. |
| **Situación del vídeo** | Todos. |

### Llamadas a OpenCV y NumPy en `roi.py`

**`compute_roi_vertices(frame_width, frame_height)`**
- Las proporciones se multiplican por `frame_width - 1` y `frame_height - 1` (último índice válido)
  en vez de por el ancho y el alto, para que una proporción de 1.00 caiga dentro de la imagen
  (columna 1279) y no un píxel fuera (1280).
- `round(...)` lleva cada coordenada al píxel más cercano; truncar desplazaría siempre los vértices
  hacia arriba y hacia la izquierda.
- `np.array(..., dtype=np.int32)`: `cv2.fillPoly` exige puntos enteros de 32 bits.

**`build_roi_mask(frame_width, frame_height)`**
- `np.zeros(shape=(frame_height, frame_width), dtype=np.uint8)`: imagen de un canal, todo a 0
  (fuera de la ROI). El orden es (filas, columnas), como en las imágenes de OpenCV. `uint8` es el
  tipo de la salida de Canny y el que acepta `mask` en `bitwise_and`.
- `cv2.fillPoly(img=mask, pts=[roi_vertices], color=ROI_MASK_INSIDE_VALUE)`: rellena el interior
  del polígono.
  - `img`: la máscara a rellenar. `fillPoly` la modifica in situ, pero la máscara se crea dentro
    de la función, así que no se modifica nada que venga de fuera.
  - `pts`: lista de polígonos; aquí solo hay uno, el trapecio.
  - `color`: el valor de relleno (255). Como la imagen tiene un canal, basta con un escalar.
  - `lineType`, `shift` y `offset` se dejan por defecto: borde de 8 vecinos sin antialiasing (el
    antialiasing pondría valores intermedios y la máscara dejaría de ser binaria), coordenadas
    enteras sin decimales y sin desplazamiento.

**`apply_region_of_interest(edges, roi_mask)`**
- `cv2.bitwise_and(src1=edges, src2=edges, mask=roi_mask)`: el AND de una imagen consigo misma la
  deja igual, y con `mask` solo se calcula donde la máscara es distinta de 0; en el resto la salida
  vale 0. El resultado son los bordes de dentro de la ROI. Alternativa equivalente:
  `cv2.bitwise_and(edges, roi_mask)`, que funciona porque la máscara vale 255; se prefiere la forma
  con `mask` porque no depende de ese valor.
- Se aplica **después** de Canny y no antes: si se recortara la imagen antes, el contorno del
  trapecio sería un salto brusco de intensidad y Canny lo detectaría como borde.
