# Decisiones del proyecto autopilot-cv

Registro de las decisiones que dan forma a la práctica: pipeline de visión, arquitectura, entorno y
forma de trabajar. Una entrada por decisión, la más reciente arriba.

- **Alcance:** aquí va el *qué* y el *porqué* de cada decisión. El detalle de cada parámetro de
  OpenCV/NumPy (valor exacto, función que lo usa) va en `docs/decisiones.md`, como pide `CONTRATO.md` §6.
- **Estado:** `propuesta` (pendiente de que ambos la aprueben) · `aceptada` · `reemplazada por #N`.
  Una decisión revertida no se borra: se marca como reemplazada.
- **Campos:** las decisiones técnicas indican además en qué módulo se aplican y qué tramo del vídeo
  resuelven, para poder defenderlas.

---

## #10 · 2026-11-13 · Sin tests automáticos por ahora
- **Estado:** aceptada
- **Decisión:** no se escriben tests con pytest en esta fase.
- **Por qué:** el enunciado evalúa el comportamiento sobre el vídeo; la validación se hace visualmente
  con fotogramas de cada tramo.
- **Consecuencias:** la checklist de revisión (`CONTRATO.md` §8) exige ejecutar el vídeo completo sin errores.
  Se puede revisar si el código crece.

## #9 · 2026-11-13 · ROI trapezoidal fija
- **Estado:** propuesta
- **Módulo:** `autopilot/roi.py`, constantes en `autopilot/config.py`
- **Tramos:** todos; problemas conocidos en bifurcación (~f1650), cambio de carril (~f1920) y salida (~f2040)
- **Decisión:** trapecio con vértices (x, y) en proporción al fotograma:
  (0.48, 0.42), (0.62, 0.42), (1.00, 0.74), (0.40, 0.74).
- **Por qué:** arriba corta bajo el horizonte (fuera cielo, carteles y coches); abajo en 0.74 porque en
  0.76 entraba el reflejo del capó; el lado izquierdo queda a la derecha del borde oscurecido del vídeo
  y de la discontinua izquierda; el lado derecho sigue la perspectiva y deja fuera el quitamiedos.
  Descartada una ROI más ancha: mete el quitamiedos y el carril izquierdo.
- **Consecuencias:** en los tramos problemáticos entran varias candidatas; las descarta el seguimiento,
  no la ROI. Más adelante se puede valorar una ROI dinámica centrada en la última línea.

## #8 · 2026-11-13 · Pipeline base: Canny y después Hough
- **Estado:** aceptada (la máscara de blanco, propuesta)
- **Módulo:** `preprocessing.py`, `roi.py`, `detection.py`, `tracking.py`
- **Tramos:** todos
- **Decisión:** gris + suavizado gaussiano → Canny → ROI → `HoughLinesP` → filtrado de segmentos →
  seguimiento temporal. Referencia de carril: posición x de la línea en una fila fija y su ángulo.
- **Por qué:** idea del equipo y técnicas vistas en la asignatura. `HoughLinesP` devuelve segmentos con
  extremos y `maxLineGap` ayuda con las discontinuas. La máscara de blanco (HLS/HSV) se propone para
  la sombra.
- **Consecuencias:** se avanza por dificultad: recta → curvas → sombra → discontinuas → salida.

## #7 · 2026-11-13 · Entorno: Python 3.12, `.venv` y versiones fijadas
- **Estado:** aceptada
- **Decisión:** `.venv/` en la raíz; `requirements.txt` con `opencv-python==5.0.0` y `numpy==2.5.4`.
- **Por qué:** mismas versiones para los dos; nada de paquetes globales.
- **Consecuencias:** una dependencia nueva se acuerda entre los dos y entra en el mismo commit.

## #6 · 2026-11-13 · El vídeo no se sube al repositorio
- **Estado:** aceptada
- **Decisión:** cada uno lo coloca en `data/autopilot.mp4`; `data/` y `output/` en `.gitignore`.
- **Por qué:** pesa ~32 MB y es material de la asignatura.
- **Consecuencias:** la ruta se pasa por argumento; nunca rutas absolutas en el código.

## #5 · 2026-11-13 · Módulos de una sola responsabilidad
- **Estado:** aceptada
- **Decisión:** `main.py` + paquete `autopilot/` (config, preprocessing, roi, detection, tracking, visualization).
- **Por qué:** sin comentarios, la separación y los nombres son lo que hace el código legible y defendible.
- **Consecuencias:** parámetros solo en `config.py`; el estado entre fotogramas, solo en una clase de `tracking.py`.

## #4 · 2026-11-13 · Flujo Git: ramas, PR aprobada y commits en español
- **Estado:** aceptada
- **Decisión:** nada se sube directo a `main`; ramas `feature/`, `fix/`, `docs/`, `refactor/`, `chore/`;
  Conventional Commits **en español**, como dice el contrato (por encima de preferencias personales).
  Se integra sin reescribir historial: nada de rebase, force push ni squash de ramas de las que
  dependen otras.
- **Por qué:** ambos deben conocer todo el código para la defensa, y no se quiere perder ningún cambio.
- **Consecuencias:** checklist de revisión en `CONTRATO.md` §8; las PR se fusionan con *merge commit*.

## #3 · 2026-11-13 · Sin coautoría de herramientas ni IA
- **Estado:** aceptada
- **Decisión:** ningún `Co-Authored-By` ni firma de Claude u otras herramientas en commits ni PRs.
- **Por qué:** los autores son los dos miembros de la pareja.
- **Consecuencias:** quien sube código hecho con ayuda responde de él igual que si lo hubiera escrito.

## #2 · 2026-11-13 · Código sin comentarios; la justificación va en documentación
- **Estado:** aceptada
- **Decisión:** cero comentarios y docstrings; nombres descriptivos en inglés.
- **Por qué:** lo exige el enunciado, y en la defensa hay que conocer el porqué de cada parámetro.
- **Consecuencias:** un cambio de parámetro sin su entrada en `docs/decisiones.md` no se acepta en revisión.

## #1 · 2026-11-13 · Contrato de trabajo común
- **Estado:** aceptada
- **Decisión:** `CONTRATO.md` fija estilo, estructura, Git y revisión; solo cambia por PR aprobada por ambos.
- **Por qué:** que Amado y Jaime traten el código de la misma forma.
- **Consecuencias:** el contrato tiene prioridad sobre las preferencias personales de cada uno.
