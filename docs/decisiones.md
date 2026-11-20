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

---

## Preprocesado

Valores **provisionales** del esqueleto (fase 0): se ajustan en la tarea A1 de la guía.

### Técnica: escala de grises y suavizado gaussiano antes de Canny

| Campo | Contenido |
|---|---|
| **Qué** | Pasar el fotograma BGR a un canal de intensidad y suavizarlo con un filtro gaussiano. |
| **Dónde** | `autopilot/preprocessing.py` · `convert_to_grayscale`, `smooth_image` |
| **Por qué** | Canny trabaja sobre un solo canal, y la marca vial (blanca) se distingue del asfalto (gris oscuro) por su intensidad. El suavizado quita el ruido de alta frecuencia (textura del asfalto, compresión del vídeo) que Canny convertiría en bordes cortos y falsos. Pendiente de valorar en A1: máscara de color blanco en HLS/HSV (decisión #8). |
| **Situación del vídeo** | Todos; la sombra (~f1200) es el tramo que más puede exigir cambiarlo. |

### `PREPROCESSING_BLUR_KERNEL_SIZE = (5, 5)`

| Campo | Contenido |
|---|---|
| **Qué** | Tamaño (ancho, alto) en píxeles del núcleo gaussiano. |
| **Dónde** | `autopilot/config.py` → `autopilot/preprocessing.py` · `smooth_image` |
| **Por qué** | Tiene que ser impar para que el núcleo tenga un píxel central. 5×5 es el valor habitual antes de Canny: quita la textura del asfalto sin emborronar la marca, que mide decenas de píxeles de ancho cerca del coche. 3×3 deja más ruido; 7×7 o más empieza a fundir los trazos lejanos de la discontinua. Provisional. |
| **Situación del vídeo** | Todos. |

### `PREPROCESSING_BLUR_SIGMA = 0`

| Campo | Contenido |
|---|---|
| **Qué** | Desviación típica del gaussiano en x (`sigmaX`). |
| **Dónde** | `autopilot/config.py` → `autopilot/preprocessing.py` · `smooth_image` |
| **Por qué** | Con 0, OpenCV la calcula a partir del tamaño del núcleo: σ = 0.3·((k − 1)·0.5 − 1) + 0.8 = 1.1 para k = 5. Así el núcleo y σ siempre son coherentes y solo hay un parámetro que ajustar. |
| **Situación del vídeo** | Todos. |

### Llamadas a OpenCV en `preprocessing.py`

**`convert_to_grayscale(frame)`**
- `cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)`: OpenCV lee los fotogramas en orden BGR, por
  eso el código es `BGR2GRAY` y no `RGB2GRAY` (cambiaría el peso de rojo y azul). Calcula
  0.299·R + 0.587·G + 0.114·B, la luminancia percibida.

**`smooth_image(gray)`**
- `cv2.GaussianBlur(src=gray, ksize=..., sigmaX=...)`. `sigmaY` se deja por defecto (0 → igual a
  `sigmaX`, filtro isótropo). `borderType` por defecto (`BORDER_REFLECT_101`): refleja la imagen en
  los bordes para no crear un salto artificial que luego Canny detectaría.

---

## Canny

Valores **provisionales** del esqueleto: se ajustan en la tarea A2.

### `CANNY_LOW_THRESHOLD = 50` y `CANNY_HIGH_THRESHOLD = 150`

| Campo | Contenido |
|---|---|
| **Qué** | Umbrales de histéresis sobre la magnitud del gradiente. |
| **Dónde** | `autopilot/config.py` → `autopilot/detection.py` · `detect_edges` |
| **Por qué** | Un píxel con gradiente por encima de 150 es borde seguro; entre 50 y 150 solo es borde si está conectado a uno seguro; por debajo de 50 se descarta. La proporción 1:3 es la que recomienda Canny (entre 1:2 y 1:3). El contraste marca blanca–asfalto supera con margen el umbral alto, y la histéresis mantiene unido el borde de la marca aunque se debilite a lo lejos. |
| **Situación del vídeo** | Todos. En la sombra (~f1200) el contraste baja; es el primer tramo que mirar al ajustarlos. |

### Llamadas a OpenCV en `detection.py` (Canny)

**`detect_edges(smoothed_gray)`**
- `cv2.Canny(image=..., threshold1=CANNY_LOW_THRESHOLD, threshold2=CANNY_HIGH_THRESHOLD)`. OpenCV
  usa el menor de los dos como umbral bajo, pero se pasan en orden para que se lea bien.
  `apertureSize` por defecto (3): Sobel 3×3 para el gradiente, suficiente tras el suavizado.
  `L2gradient` por defecto (`False`): magnitud aproximada |Gx| + |Gy|, más rápida y suficiente para
  bordes tan marcados.

---

## Hough y candidatos

Valores **provisionales** del esqueleto: se ajustan en A3; el filtrado de candidatos llega en A4.

### Técnica: transformada de Hough probabilística (`HoughLinesP`)

| Campo | Contenido |
|---|---|
| **Qué** | Convierte los píxeles de borde de dentro de la ROI en segmentos rectos con sus dos extremos. |
| **Dónde** | `autopilot/detection.py` · `find_right_line_candidates` |
| **Por qué** | La marca vial es, a trozos, una recta. A diferencia de `HoughLines`, la versión probabilística devuelve segmentos con extremos (no rectas infinitas) y permite unir trozos separados con `maxLineGap`, útil en la discontinua (decisión #8). |
| **Situación del vídeo** | Todos. |

### `HOUGH_RHO_PIXELS = 1`

| Campo | Contenido |
|---|---|
| **Qué** | Resolución en distancia del acumulador, en píxeles. |
| **Dónde** | `autopilot/config.py` → `autopilot/detection.py` · `find_right_line_candidates` |
| **Por qué** | 1 píxel es la resolución de la imagen: no tiene sentido una más fina, y una más gruesa juntaría la marca con bordes cercanos paralelos (las dos líneas de la doble marca blanca). |
| **Situación del vídeo** | Todos. |

### `HOUGH_THETA_DEGREES = 1` → `HOUGH_THETA_RADIANS`

| Campo | Contenido |
|---|---|
| **Qué** | Resolución angular del acumulador. Se define en grados para que se lea y se convierte con `math.radians`, porque OpenCV la espera en radianes. |
| **Dónde** | `autopilot/config.py` → `autopilot/detection.py` · `find_right_line_candidates` |
| **Por qué** | 1° distingue sin problema la inclinación de la marca de la de otros bordes y mantiene el acumulador pequeño (180 ángulos). |
| **Situación del vídeo** | Todos. |

### `HOUGH_VOTE_THRESHOLD = 20`

| Campo | Contenido |
|---|---|
| **Qué** | Votos mínimos en el acumulador para aceptar una recta (`threshold`). |
| **Dónde** | `autopilot/config.py` → `autopilot/detection.py` · `find_right_line_candidates` |
| **Por qué** | Equivale aproximadamente a pedir 20 píxeles de borde alineados. Bajo a propósito para el esqueleto: preferimos que sobren candidatos (los descartan A4 y el seguimiento) a que falte la marca en los trazos cortos de la discontinua. Provisional. |
| **Situación del vídeo** | Discontinua (f1800–1860). |

### `HOUGH_MIN_LINE_LENGTH = 20`

| Campo | Contenido |
|---|---|
| **Qué** | Longitud mínima en píxeles de un segmento devuelto (`minLineLength`). |
| **Dónde** | `autopilot/config.py` → `autopilot/detection.py` · `find_right_line_candidates` |
| **Por qué** | Descarta trocitos de borde de la textura del asfalto sin perder los trazos de la discontinua lejos del coche, que miden pocas decenas de píxeles. Provisional. |
| **Situación del vídeo** | Discontinua y cebreado (~f2040). |

### `HOUGH_MAX_LINE_GAP = 10`

| Campo | Contenido |
|---|---|
| **Qué** | Hueco máximo en píxeles entre dos tramos de borde para unirlos en un solo segmento (`maxLineGap`). |
| **Dónde** | `autopilot/config.py` → `autopilot/detection.py` · `find_right_line_candidates` |
| **Por qué** | Une los cortes pequeños que deja Canny dentro de una misma marca. Es pequeño frente al hueco entre trazos de la discontinua: unirlos se valorará en A3 junto con el seguimiento. Provisional. |
| **Situación del vídeo** | Discontinua. |

### Llamadas a OpenCV en `detection.py` (Hough)

**`find_right_line_candidates(edges_in_roi, frame_width)`**
- `cv2.HoughLinesP(image=..., rho=..., theta=..., threshold=..., minLineLength=..., maxLineGap=...)`.
  `image` son los bordes **ya recortados** por la ROI.
- En OpenCV 5.1 devuelve un array `int32` de forma `(N, 4)` con `x1, y1, x2, y2`, y un array vacío
  `(0, 4)` si no encuentra nada (en OpenCV 4 era `(N, 1, 4)` o `None`). Por eso no hace falta tratar
  el caso `None` (comprobado el 2026-11-20).
- Cada fila se convierte en una tupla de `int` de Python: el tipo `Segment` es la interfaz con el
  seguimiento, y así no depende de tipos de NumPy.
- `frame_width` aún no se usa: forma parte de la interfaz congelada porque el filtrado de A4 lo
  necesita (posición de la marca derecha respecto al ancho).

---

## Programa principal

### `WINDOW_NAME = "autopilot-cv"`

| Campo | Contenido |
|---|---|
| **Qué** | Título de la ventana donde se muestra el resultado. |
| **Dónde** | `autopilot/config.py` → `main.py` · `run_pipeline` |
| **Por qué** | `cv2.imshow` identifica la ventana por su nombre; usar siempre la misma constante hace que cada fotograma se pinte en la misma ventana en vez de abrir una nueva. |
| **Situación del vídeo** | Todos. |

### `WINDOW_FRAME_DELAY_MS = 1`

| Campo | Contenido |
|---|---|
| **Qué** | Milisegundos que `cv2.waitKey` espera una tecla tras mostrar cada fotograma. |
| **Dónde** | `autopilot/config.py` → `main.py` · `is_exit_requested` |
| **Por qué** | `imshow` solo refresca la ventana cuando se llama a `waitKey`. 1 ms es la espera mínima (0 esperaría indefinidamente): el vídeo avanza tan rápido como se procesa. Para verlo a velocidad real habría que esperar ≈ 1000 / 30 fps = 33 ms menos el tiempo de proceso; se decide en A5. |
| **Situación del vídeo** | Todos. |

### `WINDOW_EXIT_KEY = "q"`

| Campo | Contenido |
|---|---|
| **Qué** | Tecla que detiene la reproducción antes del final. |
| **Dónde** | `autopilot/config.py` → `main.py` · `is_exit_requested` |
| **Por qué** | Convención habitual en los ejemplos de OpenCV. `ord(...)` la convierte en el código que devuelve `waitKey`. |
| **Situación del vídeo** | — |

### Llamadas en `main.py`

- `argparse`: la ruta del vídeo es un argumento obligatorio, nunca una ruta escrita en el código
  (`CONTRATO.md` §3). Se convierte a `pathlib.Path`.
- `cv2.VideoCapture(str(video_path))`: se pasa como `str` porque es lo que espera la API. Si
  `isOpened()` es falso, se termina con `SystemExit` y un mensaje claro, en vez de fallar más
  adelante con un fotograma vacío.
- `capture.get(cv2.CAP_PROP_FRAME_WIDTH)` y `capture.get(cv2.CAP_PROP_FRAME_HEIGHT)`: tamaño del
  fotograma, leído una sola vez para construir la máscara de la ROI y el tracker. Devuelven `float`;
  se pasan a `int`.
- `capture.read()` devuelve `(is_frame_read, frame)`; cuando es falso, se ha llegado al final.
- `cv2.imshow(winname=WINDOW_NAME, mat=...)`: muestra el fotograma con el resultado dibujado.
- `try/finally` con `capture.release()` y `cv2.destroyAllWindows()`: libera el vídeo y cierra la
  ventana aunque se salga con la tecla o haya un error.

---

## Seguimiento

Versión **ingenua** del esqueleto (sin memoria entre fotogramas). Se sustituye en J1–J4.

### Interfaz: `TrackedLine` y `RightLineTracker.update`

| Campo | Contenido |
|---|---|
| **Qué** | `RightLineTracker.update(candidates)` recibe los segmentos de Hough de un fotograma y devuelve un `TrackedLine` (`bottom_x`, `bottom_y`, `top_x`, `top_y`, `status`) o `None` si no hay línea. |
| **Dónde** | `autopilot/tracking.py` |
| **Por qué** | La línea se describe por dónde corta dos horizontales de referencia: dos puntos definen la recta (y también su ángulo) y, a diferencia del ángulo solo, distinguen dos líneas casi paralelas como las de la doble marca blanca. Las `y` van dentro de `TrackedLine` para que las filas en píxeles se calculen en un único sitio (el tracker) y el dibujo no repita ese cálculo. Es una `dataclass(frozen=True)`: el resultado de un fotograma no se puede modificar después. `TrackingStatus` distingue línea detectada de estimada (J4). |
| **Situación del vídeo** | Todos. |

### `TRACKING_REFERENCE_TOP_ROW = 0.42` y `TRACKING_REFERENCE_BOTTOM_ROW = 0.74`

| Campo | Contenido |
|---|---|
| **Qué** | Alturas, en proporción al fotograma, de las dos horizontales de referencia (filas 302 y 532 en 720 p). |
| **Dónde** | `autopilot/config.py` → `autopilot/tracking.py` · `RightLineTracker.__init__` |
| **Por qué** | Coinciden con los lados superior e inferior de la ROI: es la franja donde hay bordes, así que la línea dibujada cubre justo la zona analizada. Son constantes propias y no las de la ROI para poder moverlas sin tocar la máscara. Se convierten a píxeles con `round(proporción · (alto − 1))`, igual que la ROI. |
| **Situación del vídeo** | Todos. |

### Funciones de `tracking.py`

- **Selección ingenua:** el segmento más largo (`math.hypot`). En la ROI, la marca derecha suele ser
  la estructura recta más larga. Falla cuando hay otra más larga (bifurcación, cambio de carril,
  cebreado): lo resuelve el seguimiento de J1–J4.
- **`compute_x_at_row`:** prolonga el segmento hasta una fila con la ecuación de la recta que pasa
  por sus dos extremos: x = x1 + (fila − y1)·(x2 − x1)/(y2 − y1).
- **`is_horizontal`:** con y1 = y2 la recta no corta las horizontales de referencia (división por
  cero), así que esos segmentos se descartan.
- `frame_width` se guarda pero aún no se usa: es parte de la interfaz para J1–J4.

---

## Visualización

Versión mínima del esqueleto: el color por estado y las horizontales de referencia llegan en J5.

### `DRAW_LINE_COLOR_BGR = (0, 255, 0)`

| Campo | Contenido |
|---|---|
| **Qué** | Color de la línea seguida, en orden BGR (verde). |
| **Dónde** | `autopilot/config.py` → `autopilot/visualization.py` · `draw_tracking_overlay` |
| **Por qué** | El verde contrasta con el asfalto gris y la marca blanca, y no se confunde con nada del vídeo. El orden es BGR porque es el de los fotogramas de OpenCV. |
| **Situación del vídeo** | Todos. |

### `DRAW_LINE_THICKNESS = 6`

| Campo | Contenido |
|---|---|
| **Qué** | Grosor en píxeles de la línea dibujada. |
| **Dónde** | `autopilot/config.py` → `autopilot/visualization.py` · `draw_tracking_overlay` |
| **Por qué** | A 1280×720 se ve claramente sin tapar del todo la marca que hay debajo, así que se puede comprobar a simple vista si coincide. |
| **Situación del vídeo** | Todos. |

### `DRAW_LINE_TYPE = cv2.LINE_AA`

| Campo | Contenido |
|---|---|
| **Qué** | Dibujo con antialiasing. |
| **Dónde** | `autopilot/config.py` → `autopilot/visualization.py` · `draw_tracking_overlay` |
| **Por qué** | Suaviza los bordes de una línea inclinada. Aquí sí conviene (al contrario que en la máscara de la ROI) porque es solo para mostrar: los valores intermedios no se usan para calcular nada. |
| **Situación del vídeo** | Todos. |

### Llamadas a OpenCV en `visualization.py`

**`draw_tracking_overlay(frame, tracked_line)`**
- `frame.copy()`: `cv2.line` dibuja sobre la imagen que recibe; al copiarla, la función es pura y
  el fotograma original no cambia.
- `cv2.line(img=..., pt1=..., pt2=..., color=..., thickness=..., lineType=...)`: une el corte con la
  horizontal inferior y el corte con la superior. Las `x` son `float` y se redondean con `round`
  porque OpenCV exige puntos enteros. Si un punto cae fuera del fotograma, OpenCV recorta la línea
  al borde.
- Si `tracked_line` es `None`, se devuelve la copia sin dibujar nada.
