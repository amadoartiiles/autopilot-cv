import cv2
import numpy as np

from autopilot.config import (
    CANNY_HIGH_THRESHOLD,
    CANNY_LOW_THRESHOLD,
    HOUGH_MAX_LINE_GAP,
    HOUGH_MIN_LINE_LENGTH,
    HOUGH_RHO_PIXELS,
    HOUGH_THETA_RADIANS,
    HOUGH_VOTE_THRESHOLD,
)

Segment = tuple[int, int, int, int]


def detect_edges(smoothed_gray: np.ndarray) -> np.ndarray:
    return cv2.Canny(
        image=smoothed_gray, threshold1=CANNY_LOW_THRESHOLD, threshold2=CANNY_HIGH_THRESHOLD
    )


def find_right_line_candidates(edges_in_roi: np.ndarray, frame_width: int) -> list[Segment]:
    detected_segments = cv2.HoughLinesP(
        image=edges_in_roi,
        rho=HOUGH_RHO_PIXELS,
        theta=HOUGH_THETA_RADIANS,
        threshold=HOUGH_VOTE_THRESHOLD,
        minLineLength=HOUGH_MIN_LINE_LENGTH,
        maxLineGap=HOUGH_MAX_LINE_GAP,
    )
    return [(int(x1), int(y1), int(x2), int(y2)) for x1, y1, x2, y2 in detected_segments]
