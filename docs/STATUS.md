# Estado del proyecto

_Última actualización: 2026-11-13_

## Objetivo actual
Fijar la región de interés (ROI) para quedarnos solo con la marca derecha antes de aplicar Canny y Hough.

## Hecho
- Contrato de trabajo (`CONTRATO.md`) y `.gitignore` en `main`.
- README y nombres/fecha de firmantes del contrato en `main` (PR #1, fusionada con merge commit).
- `.venv` con opencv-python 5.0.0 y numpy 2.5.4; vídeo copiado a `data/autopilot.mp4`.
- Análisis de fotogramas de todo el vídeo y propuesta de ROI trapezoidal → `docs/plans/PLAN-roi.md`.
- Estructura de memoria (CLAUDE.md, docs/, `.claude/`) en la rama `chore/claude-setup`, subida.

## En curso
- ROI → `docs/plans/PLAN-roi.md` · propuesta hecha, pendiente de confirmación para pasarla a código.

## Siguiente paso
- Confirmar los vértices de la ROI y crear la rama `feature/roi` con `requirements.txt`,
  `autopilot/config.py`, `autopilot/roi.py` y `docs/decisiones.md`.

## Bloqueos / dudas abiertas
- Abrir la PR de `chore/claude-setup` contra `main`, que Jaime la apruebe y fusionarla con merge commit.
- Borrar la rama `docs/readme` (en GitHub y en local con `git branch -d`); ya está toda en `main`.
- Jaime y Amado marcan su casilla en el contrato.
- Configurar protección de `main` en GitHub (PR + 1 aprobación).
- Añadir `.gitattributes` con `* text=auto eol=lf` (Git avisa de conversión LF→CRLF).
- La carpeta está en OneDrive: vigilar problemas de sincronización con `.git`.
