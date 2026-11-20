import cv2
import numpy as np

from autopilot.config import PREPROCESSING_BLUR_KERNEL_SIZE, PREPROCESSING_BLUR_SIGMA


def convert_to_grayscale(frame: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)


def smooth_image(gray: np.ndarray) -> np.ndarray:
    return cv2.GaussianBlur(
        src=gray, ksize=PREPROCESSING_BLUR_KERNEL_SIZE, sigmaX=PREPROCESSING_BLUR_SIGMA
    )
