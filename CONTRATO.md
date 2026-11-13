# Contrato de trabajo — autopilot-cv

Acuerdo entre los dos miembros de la pareja sobre cómo escribimos, organizamos y revisamos el código de la práctica *Sistema de conducción autónoma mediante visión artificial con OpenCV* (FSI, ULPGC).

Todo lo que entre en `main` cumple este contrato. Si algo no está cubierto aquí, se decide entre los dos y se añade a este documento.

---

## 1. Reglas que vienen del enunciado (no negociables)

1. **El código no lleva ningún comentario explicativo.** Ni `#`, ni docstrings, ni bloques de texto comentado, ni código comentado "por si acaso". La explicación vive en los nombres y en `docs/decisiones.md` (ver §6).
2. **Ambos conocemos todo el código.** Cualquiera de los dos debe poder explicar cualquier función en la defensa. Por eso ningún cambio entra sin que el otro lo haya revisado y entendido (ver §8).
3. **Cada parámetro de cada función de OpenCV/NumPy que usemos debe estar justificado**: qué hace y por qué ese valor.
4. **Cada solución adoptada debe poder justificarse.** Si no sabemos explicar por qué algo funciona, no se queda.
5. Solo usamos técnicas de procesamiento de imagen vistas en la asignatura (preprocesado, filtrado, Canny, Hough, regiones de interés, seguimiento temporal…). Cualquier técnica fuera de eso se consulta antes entre los dos.
6. La salida muestra el **vídeo original con los resultados superpuestos**, dejando claro qué marca vial se está siguiendo.

## 2. Entorno

- **Python 3.12.**
- Entorno virtual en `.venv/` en la raíz del repositorio (no se sube).
- Dependencias en `requirements.txt` **con versión fijada** (`opencv-python==X.Y.Z`, `numpy==X.Y.Z`). Quien añada una dependencia actualiza el fichero en el mismo commit y lo avisa.
- Antes de añadir una librería nueva, se acuerda entre los dos: tiene que poder justificarse en la defensa.

## 3. Datos

- El vídeo **no se sube al repositorio** (pesa ~32 MB y es material de la asignatura). Cada uno lo coloca en `data/` con el nombre `autopilot.mp4`.
- La ruta al vídeo se pasa por argumento de línea de comandos o se toma de la configuración; nunca se escribe una ruta absoluta de nuestro ordenador en el código.
- Las salidas generadas (vídeos procesados, capturas) van a `output/`, que tampoco se sube.

## 4. Estructura del proyecto

Estructura acordada (se crea cuando empecemos a programar):

```
autopilot-cv/
├── CONTRATO.md
├── README.md
├── requirements.txt
├── main.py                 punto de entrada: lee el vídeo, ejecuta el pipeline, muestra el resultado
├── autopilot/
│   ├── __init__.py
│   ├── config.py           todos los parámetros con nombre (umbrales, tamaños de kernel, ROI…)
│   ├── preprocessing.py    conversión de color, filtrado, máscaras
│   ├── roi.py              definición y aplicación de regiones de interés
│   ├── detection.py        bordes (Canny) y líneas (Hough), selección de la marca derecha
│   ├── tracking.py         seguimiento temporal, estimación cuando se pierde la marca, recuperación
│   └── visualization.py    dibujo de resultados sobre el fotograma original
├── docs/
│   └── decisiones.md       registro de decisiones y justificación de parámetros
├── data/                   (ignorado) vídeo de entrada
└── output/                 (ignorado) resultados generados
```

Cada módulo tiene **una responsabilidad**. Si un fichero empieza a hacer dos cosas, se divide.

## 5. Estilo de código

### 5.1 General
- **PEP 8**, formateado con **Ruff** (`ruff format`) y comprobado con `ruff check`. Longitud máxima de línea: **100**.
- Indentación con 4 espacios, codificación UTF-8, final de línea LF.
- Nada de código muerto, `print` de depuración ni imports sin usar en `main`.

### 5.2 Idioma
- **Identificadores en inglés** (variables, funciones, clases, módulos), por coherencia con OpenCV y NumPy.
- **Documentación, commits, issues y PRs en español.**

### 5.3 Nombres (sustituyen a los comentarios)
- `snake_case` para variables, funciones y módulos; `PascalCase` para clases; `UPPER_SNAKE_CASE` para constantes.
- Los nombres deben decir **qué es** o **qué hace**, sin abreviaturas crípticas: `right_lane_line`, `apply_region_of_interest`, `CANNY_LOW_THRESHOLD`; no `l`, `img2`, `th1`.
- Funciones con verbo: `detect_edges`, `select_right_line`, `estimate_from_history`.
- Booleanos como pregunta: `is_line_detected`, `has_lost_track`.
- Abreviaturas permitidas por ser estándar en visión: `roi`, `bgr`, `hsv`, `gray`, `frame`.

### 5.4 Funciones
- Una función hace **una sola cosa** y es corta (orientativo: < 30 líneas). Si necesitaría un comentario para entenderse, se divide o se renombra.
- Preferimos funciones **puras**: reciben un fotograma/datos y devuelven un resultado, sin modificar la entrada ni depender de estado global.
- El único estado que persiste entre fotogramas (historial de líneas, última posición conocida…) vive en una clase en `tracking.py`, nunca en variables globales.
- **Type hints obligatorios** en parámetros y retorno (`np.ndarray`, `tuple[int, int]`, `Line | None`…). Ayudan a entender el código sin comentarios.
- Al llamar a funciones de OpenCV con varios parámetros, usar **argumentos con nombre** cuando la API lo permita, para que se lea qué es cada valor.

### 5.5 Parámetros y números mágicos
- **Prohibidos los números mágicos.** Todo umbral, tamaño de kernel, coordenada de ROI, número de fotogramas de historial, etc. se define en `autopilot/config.py` como constante con nombre.
- Coordenadas de la ROI expresadas **en proporción al tamaño del fotograma** (p. ej. `0.6 * height`), no en píxeles absolutos, salvo que se justifique.
- Cada constante de `config.py` tiene su entrada en `docs/decisiones.md`.

## 6. Documentación de decisiones (`docs/decisiones.md`)

Como el código no puede llevar comentarios, toda justificación va aquí. Es nuestra chuleta para la defensa.

Para cada técnica o parámetro relevante:

| Campo | Contenido |
|---|---|
| **Qué** | Técnica o parámetro (`CANNY_LOW_THRESHOLD = 50`) |
| **Dónde** | Módulo y función que lo usa |
| **Por qué** | Justificación y alternativas descartadas |
| **Situación del vídeo** | Qué tramo resuelve (recta, curva, sombra, discontinua, salida…) |

Regla: **un cambio de parámetro o de técnica sin su entrada en `decisiones.md` no se acepta en revisión.**

## 7. Git y GitHub

### 7.1 Ramas
- `main` siempre funciona: el programa se ejecuta de principio a fin sobre el vídeo sin errores.
- Nadie hace push directo a `main`. Se trabaja en ramas:
  - `feature/<descripcion-corta>` — funcionalidad nueva (`feature/hough-right-line`)
  - `fix/<descripcion-corta>` — corrección (`fix/shadow-false-positives`)
  - `docs/<descripcion-corta>` — documentación
  - `refactor/<descripcion-corta>` — reorganización sin cambiar comportamiento

### 7.2 Commits
- Formato **Conventional Commits en español**, en imperativo:
  - `feat: detectar línea derecha con Hough probabilístico`
  - `fix: evitar confundir la sombra con la marca vial`
  - `refactor: separar la ROI en su propio módulo`
  - `docs: justificar umbrales de Canny`
  - `chore: fijar versión de opencv-python`
- Commits pequeños y con un único propósito.
- **Sin líneas `Co-Authored-By` ni firmas de herramientas o asistentes.** Los únicos autores del repositorio somos nosotros dos.

### 7.3 Pull requests
- Todo cambio entra en `main` mediante PR, aprobada por **el otro miembro de la pareja**.
- La descripción de la PR indica: qué cambia, qué situación del vídeo mejora y qué entradas de `decisiones.md` se han añadido.
- Se hace *squash and merge* o *merge* normal, pero siempre manteniendo mensajes en el formato de §7.2.
- La rama se borra tras fusionarla.

## 8. Revisión (checklist antes de aprobar una PR)

El revisor comprueba, y solo aprueba si todo se cumple:

- [ ] El programa se ejecuta sobre el vídeo completo sin errores.
- [ ] No hay ningún comentario ni docstring en el código.
- [ ] No hay números mágicos: todo está en `config.py`.
- [ ] `ruff format` y `ruff check` pasan sin avisos.
- [ ] Nombres claros, funciones cortas, type hints presentes.
- [ ] Los parámetros nuevos o modificados están justificados en `docs/decisiones.md`.
- [ ] **El revisor sabe explicar el código nuevo**, incluidos todos los parámetros de las funciones de OpenCV usadas. Si no, se pregunta en la PR antes de aprobar.
- [ ] No se suben vídeos, salidas, `.venv/` ni ficheros del sistema.

## 9. Herramientas de apoyo (incluida IA)

- Se puede usar cualquier herramienta de apoyo, pero **quien sube el código responde de él**: debe entenderlo y poder defenderlo igual que si lo hubiera escrito a mano.
- El código generado con ayuda pasa por la misma revisión que el resto, sin excepciones.
- Ninguna herramienta figura como autora o coautora en commits ni PRs.

## 10. Comunicación y reparto

- Las tareas se reparten mediante *issues* de GitHub, asignadas a una persona.
- Antes de empezar algo grande, se comenta en el issue para no duplicar trabajo.
- Aunque cada uno lleve unas partes, **ambos revisamos y entendemos todas** (requisito de la defensa).

## 11. Cambios en este contrato

Este documento solo se modifica mediante PR aprobada por los dos.

---

**Aceptado por:**

- [ ] Miembro 1: ____________ — fecha: ________
- [ ] Miembro 2: ____________ — fecha: ________
