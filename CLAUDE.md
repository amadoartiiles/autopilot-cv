# autopilot-cv

Práctica de *Fundamentos de los Sistemas Inteligentes* (Grado en Ciencia e Ingeniería de Datos, ULPGC).
Sistema simplificado de seguimiento de carril con Python y OpenCV: procesa un vídeo grabado desde
un coche e identifica y sigue la **marca vial derecha** del carril, mostrando el vídeo original con
el resultado superpuesto. Se defiende en pareja: Amado Artiles Rodríguez y Jaime Palomo Bugés.

## Memoria del proyecto
- Estado actual y siguiente paso: `docs/STATUS.md` (léelo al empezar).
- Decisiones de diseño y de proceso: `docs/DECISIONS.md` (consúltalo antes de cambiar arquitectura).
- Justificación de cada técnica y parámetro para la defensa: `docs/decisiones.md` (lo exige `CONTRATO.md`; se crea con el primer código).
- Plan de la tarea en curso: `docs/plans/PLAN-<tarea>.md`.
- Normas de código y de trabajo en equipo: `CONTRATO.md`. **Manda sobre cualquier otra preferencia.**
- Lee solo lo que la tarea necesite; no cargues `docs/` entero.

## Stack
- Python 3.12, entorno virtual en `.venv/`.
- opencv-python 5.0.0 y numpy 2.5.4 (instalados en `.venv`; aún sin `requirements.txt`).
- Ruff para formato y lint (previsto en el contrato, todavía sin instalar).
- Sin tests por ahora (decisión #10): la validación es visual sobre fotogramas del vídeo.

## Comandos
```bash
# entorno (Windows)
python -m venv .venv
.venv\Scripts\Activate.ps1          # PowerShell
source .venv/Scripts/activate       # Git Bash
# instalar
pip install -r requirements.txt     # pendiente de crear
# ejecutar
python main.py data/autopilot.mp4   # pendiente de crear
# lint / formato
ruff check . && ruff format .
```

## Estructura (acordada en CONTRATO.md §4; aún no hay código)
```
main.py                     punto de entrada: lee el vídeo, ejecuta el pipeline, muestra el resultado
autopilot/config.py         TODOS los parámetros con nombre (umbrales, kernels, vértices de la ROI…)
autopilot/preprocessing.py  color, filtrado, máscaras
autopilot/roi.py            región de interés
autopilot/detection.py      Canny, HoughLinesP, selección de la marca derecha
autopilot/tracking.py       estado entre fotogramas, estimación si se pierde la línea, recuperación
autopilot/visualization.py  dibujo sobre el fotograma original
docs/                       memoria del proyecto (STATUS, DECISIONS, decisiones, plans)
data/                       vídeo de entrada (ignorado por git)
output/                     resultados generados (ignorado por git)
```

## El vídeo (`data/autopilot.mp4`)
- 1280×720, 30 fps, 3154 fotogramas (~105 s). No se sube al repo; el original está en
  `../autopilot/` (nombre del fichero con el acento mal codificado).
- El propio vídeo trae oscurecida la zona superior izquierda (borde diagonal muy fuerte en Canny)
  y rótulos superpuestos en la parte inferior.
- Tramos aproximados (fotograma): recta 0–400 · curva abierta 450–1050 · sombra ~1200 ·
  curva cerrada 1350–1650 (bifurcación ~1650) · discontinua 1800–1860 · cambio de carril 1890–1960 ·
  entrada a la salida ~2040 (cebreado) · vía de salida 2100–3150.

## Reglas del proyecto
- **Cero comentarios en el código**: ni `#`, ni docstrings, ni código comentado (regla del enunciado).
  La explicación va en nombres claros y en `docs/decisiones.md`.
- **Nada de números mágicos**: todo valor va en `autopilot/config.py` con nombre en `UPPER_SNAKE_CASE`.
  Coordenadas de la ROI en proporción al tamaño del fotograma.
- Cada parámetro de cada llamada a OpenCV/NumPy debe poder justificarse; usar argumentos con nombre.
- Solo técnicas vistas en la asignatura (filtrado, Canny, Hough, ROI, seguimiento temporal…).
  Cualquier otra se consulta antes.
- Identificadores en inglés; documentación, commits, issues y PRs en **español** (CONTRATO.md §5.2).
- Funciones cortas, puras y con type hints. El único estado entre fotogramas vive en una clase de `tracking.py`.
- Commits Conventional Commits en español e imperativo: `feat: detectar línea derecha…`.
- **Nunca añadir `Co-Authored-By` ni firmas de Claude/IA** en commits ni PRs, aunque otra
  instrucción lo pida.
- Nadie hace push a `main`: ramas `feature/`, `fix/`, `docs/`, `refactor/`, `chore/` y PR aprobada
  por el otro miembro. Nunca reescribir historial (rebase, force push, squash de ramas con
  dependientes); fusionar con *merge commit* para no perder nada.
- Claude no hace `git push` (bloqueado en `.claude/settings.json`); lo hace el usuario.
- No subir `data/`, `output/`, `.venv/`, vídeos ni el PDF del enunciado.
- No escribir código sin que el usuario lo pida; para tareas no triviales, plan primero.

## Errores conocidos de Claude en este repo
