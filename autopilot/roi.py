import cv2
import numpy as np

from autopilot.config import ROI_MASK_INSIDE_VALUE, ROI_VERTEX_PROPORTIONS


def compute_roi_vertices(frame_width: int, frame_height: int) -> np.ndarray:
    last_column = frame_width - 1
    last_row = frame_height - 1
    return np.array(
        [
            (round(x_proportion * last_column), round(y_proportion * last_row))
            for x_proportion, y_proportion in ROI_VERTEX_PROPORTIONS
        ],
        dtype=np.int32,
    )


def build_roi_mask(frame_width: int, frame_height: int) -> np.ndarray:
    mask = np.zeros(shape=(frame_height, frame_width), dtype=np.uint8)
    roi_vertices = compute_roi_vertices(frame_width, frame_height)
    return cv2.fillPoly(img=mask, pts=[roi_vertices], color=ROI_MASK_INSIDE_VALUE)


def apply_region_of_interest(edges: np.ndarray, roi_mask: np.ndarray) -> np.ndarray:
    return cv2.bitwise_and(src1=edges, src2=edges, mask=roi_mask)
