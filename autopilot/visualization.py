import cv2
import numpy as np

from autopilot.config import DRAW_LINE_COLOR_BGR, DRAW_LINE_THICKNESS, DRAW_LINE_TYPE
from autopilot.tracking import TrackedLine


def draw_tracking_overlay(frame: np.ndarray, tracked_line: TrackedLine | None) -> np.ndarray:
    overlay = frame.copy()
    if tracked_line is None:
        return overlay
    return cv2.line(
        img=overlay,
        pt1=(round(tracked_line.bottom_x), tracked_line.bottom_y),
        pt2=(round(tracked_line.top_x), tracked_line.top_y),
        color=DRAW_LINE_COLOR_BGR,
        thickness=DRAW_LINE_THICKNESS,
        lineType=DRAW_LINE_TYPE,
    )
