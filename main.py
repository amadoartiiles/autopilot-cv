import argparse
from pathlib import Path

import cv2
import numpy as np

from autopilot.config import WINDOW_EXIT_KEY, WINDOW_FRAME_DELAY_MS, WINDOW_NAME
from autopilot.detection import Segment, detect_edges, find_right_line_candidates
from autopilot.preprocessing import convert_to_grayscale, smooth_image
from autopilot.roi import apply_region_of_interest, build_roi_mask
from autopilot.tracking import RightLineTracker
from autopilot.visualization import draw_tracking_overlay


def parse_video_path() -> Path:
    parser = argparse.ArgumentParser(description="Seguimiento de la marca vial derecha.")
    parser.add_argument("video_path", type=Path, help="Ruta al vídeo de entrada.")
    return parser.parse_args().video_path


def open_video(video_path: Path) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise SystemExit(f"No se puede abrir el vídeo: {video_path}")
    return capture


def read_frame_size(capture: cv2.VideoCapture) -> tuple[int, int]:
    frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return frame_width, frame_height


def find_candidates_in_frame(
    frame: np.ndarray, roi_mask: np.ndarray, frame_width: int
) -> list[Segment]:
    gray = convert_to_grayscale(frame)
    smoothed_gray = smooth_image(gray)
    edges = detect_edges(smoothed_gray)
    edges_in_roi = apply_region_of_interest(edges, roi_mask)
    return find_right_line_candidates(edges_in_roi, frame_width)


def is_exit_requested() -> bool:
    return cv2.waitKey(delay=WINDOW_FRAME_DELAY_MS) == ord(WINDOW_EXIT_KEY)


def run_pipeline(capture: cv2.VideoCapture) -> None:
    frame_width, frame_height = read_frame_size(capture)
    roi_mask = build_roi_mask(frame_width, frame_height)
    tracker = RightLineTracker(frame_width, frame_height)
    while True:
        is_frame_read, frame = capture.read()
        if not is_frame_read:
            break
        candidates = find_candidates_in_frame(frame, roi_mask, frame_width)
        tracked_line = tracker.update(candidates)
        cv2.imshow(winname=WINDOW_NAME, mat=draw_tracking_overlay(frame, tracked_line))
        if is_exit_requested():
            break


def main() -> None:
    capture = open_video(parse_video_path())
    try:
        run_pipeline(capture)
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
