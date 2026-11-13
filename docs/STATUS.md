# Estado del proyecto

_Última actualización: 2026-11-13_

## Objetivo actual
Fijar la región de interés (ROI) para quedarnos solo con la marca derecha antes de aplicar Canny y Hough.

## Hecho
- Contrato de trabajo (`CONTRATO.md`) y `.gitignore` en `main`.
- README y nombres/fecha de firmantes del contrato en la rama `docs/readme` (subida, PR sin abrir).
- `.venv` con opencv-python 5.0.0 y numpy 2.5.4; vídeo copiado a `data/autopilot.mp4`.
- Análisis de fotogramas de todo el vídeo y propuesta de ROI trapezoidal → `docs/plans/PLAN-roi.md`.
- Estructura de memoria (CLAUDE.md, docs/, `.claude/`) en la rama `chore/claude-setup` (sin commit).

## En curso
- ROI → `docs/plans/PLAN-roi.md` · propuesta hecha, pendiente de confirmación para pasarla a código.

## Siguiente paso
- Confirmar los vértices de la ROI y crear la rama `feature/roi` con `requirements.txt`,
  `autopilot/config.py`, `autopilot/roi.py` y `docs/decisiones.md`.

## Bloqueos / dudas abiertas
- Abrir y aprobar la PR de `docs/readme`; Jaime y Amado marcan su casilla en el contrato.
- `chore/claude-setup` sale de `docs/readme` (sin commit aún). Orden: fusionar `docs/readme` con
  *merge commit* y después abrir la PR de `chore/claude-setup`. Sin rebase, force push ni squash.
- Configurar protección de `main` en GitHub (PR + 1 aprobación).
- Añadir `.gitattributes` con `* text=auto eol=lf` (Git avisa de conversión LF→CRLF).
- La carpeta está en OneDrive: vigilar problemas de sincronización con `.git`.
