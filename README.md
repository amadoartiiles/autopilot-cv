# autopilot-cv

Sistema simplificado de seguimiento de carril mediante visión artificial con **Python** y **OpenCV**.

Práctica de la asignatura *Fundamentos de los Sistemas Inteligentes* — Grado en Ciencia e Ingeniería de Datos, Universidad de Las Palmas de Gran Canaria (ULPGC).

> **Estado:** en desarrollo. Todavía no hay código; la estructura y los comandos de abajo son los acordados en [`CONTRATO.md`](CONTRATO.md).

## Objetivo

Procesar una grabación tomada desde la parte delantera de un vehículo y **identificar y seguir la marca vial que delimita la parte derecha del carril**, mostrando el vídeo original con el resultado superpuesto.

El sistema debe mantener el seguimiento durante todo el recorrido, que incluye:

- Tramo aproximadamente recto.
- Curvas suaves y curvas pronunciadas.
- Paso bajo una zona de sombra.
- Transición entre marcas continuas y discontinuas.
- Líneas discontinuas de mayor grosor.
- Cambio de carril a la derecha y circulación por una salida.

Cuando la marca no se detecta con fiabilidad, se estima su posición a partir de los fotogramas anteriores.

## Técnicas

Preprocesado y filtrado de imagen, regiones de interés, detección de bordes (Canny), detección de líneas (transformada de Hough) y seguimiento temporal. La justificación de cada técnica y parámetro se recoge en [`docs/decisiones.md`](docs/decisiones.md).

## Requisitos

- Python 3.12
- Dependencias en `requirements.txt` (OpenCV y NumPy, con versión fijada)

## Instalación

```bash
git clone https://github.com/amadoartiiles/autopilot-cv.git
cd autopilot-cv
python -m venv .venv
```

Activar el entorno virtual:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Datos

El vídeo de la práctica **no se incluye en el repositorio**. Descárgalo del campus virtual y colócalo en:

```
data/autopilot.mp4
```

## Uso

```bash
python main.py data/autopilot.mp4
```

## Estructura

```
autopilot-cv/
├── main.py                 punto de entrada
├── autopilot/
│   ├── config.py           parámetros con nombre
│   ├── preprocessing.py    conversión de color, filtrado, máscaras
│   ├── roi.py              regiones de interés
│   ├── detection.py        Canny, Hough y selección de la marca derecha
│   ├── tracking.py         seguimiento temporal y recuperación
│   └── visualization.py    dibujo de resultados sobre el fotograma
├── docs/decisiones.md      justificación de técnicas y parámetros
├── data/                   vídeo de entrada (no se sube)
└── output/                 resultados generados (no se sube)
```

## Forma de trabajo

Normas de código, ramas, commits y revisión: [`CONTRATO.md`](CONTRATO.md).

## Autores

- Amado Artiles Rodríguez
- Jaime Palomo Bugés
