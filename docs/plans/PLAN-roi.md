# Plan: región de interés (ROI)

- **Issue / rama:** sin issue · `feature/roi` (por crear)
- **Responsable:** Amado y Jaime
- **Estado:** en curso

## Objetivo
Una máscara que, aplicada tras Canny, deje dentro solo la marca vial derecha en los tramos normales
del vídeo. Se comprueba dibujando la ROI y los bordes de Canny sobre fotogramas de cada tramo.

## Pasos
- [x] 1. Extraer fotogramas de todo el vídeo (cada 5 s) y del cambio de carril (cada 1 s).
- [x] 2. Probar un trapecio candidato con Canny encima y ajustarlo (borde inferior 0.76 → 0.74).
- [ ] 3. Confirmar vértices con el equipo: (0.48, 0.42), (0.62, 0.42), (1.00, 0.74), (0.40, 0.74).
- [ ] 4. Crear rama `feature/roi` y `requirements.txt` con opencv-python==5.0.0 y numpy==2.5.4.
- [ ] 5. `autopilot/config.py` con los vértices como constantes.
- [ ] 6. `autopilot/roi.py`: función que construye la máscara a partir del tamaño del fotograma y la aplica.
- [ ] 7. Entrada en `docs/decisiones.md` con la justificación de cada vértice.
- [ ] 8. `ruff check` y `ruff format` pasan; PR para que la revise Jaime.

## Notas
- Funciona bien en: recta, curvas abierta y cerrada, sombra, discontinua y vía de salida.
- Casos con candidatas extra (los resuelve el seguimiento, no la ROI):
  bifurcación ~f1650 (dos líneas), cambio de carril ~f1920 (línea nueva casi en el borde derecho y
  trazos de la discontinua abajo a la izquierda), cebreado de la salida ~f2040.
- Los scripts de prueba (`extract.py`, `roi.py`, `sheet.py`) están en el scratchpad de la sesión,
  fuera del repo; no forman parte del proyecto.
