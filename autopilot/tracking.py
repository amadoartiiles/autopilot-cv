import math
from dataclasses import dataclass
from enum import Enum, auto

from autopilot.config import TRACKING_REFERENCE_BOTTOM_ROW, TRACKING_REFERENCE_TOP_ROW
from autopilot.detection import Segment


class TrackingStatus(Enum):
    DETECTED = auto()
    ESTIMATED = auto()


@dataclass(frozen=True)
class TrackedLine:
    bottom_x: float
    bottom_y: int
    top_x: float
    top_y: int
    status: TrackingStatus


def compute_reference_row(row_proportion: float, frame_height: int) -> int:
    return round(row_proportion * (frame_height - 1))


def compute_segment_length(segment: Segment) -> float:
    x1, y1, x2, y2 = segment
    return math.hypot(x2 - x1, y2 - y1)


def is_horizontal(segment: Segment) -> bool:
    _, y1, _, y2 = segment
    return y1 == y2


def compute_x_at_row(segment: Segment, row: int) -> float:
    x1, y1, x2, y2 = segment
    return x1 + (row - y1) * (x2 - x1) / (y2 - y1)


class RightLineTracker:
    def __init__(self, frame_width: int, frame_height: int) -> None:
        self.frame_width = frame_width
        self.top_row = compute_reference_row(TRACKING_REFERENCE_TOP_ROW, frame_height)
        self.bottom_row = compute_reference_row(TRACKING_REFERENCE_BOTTOM_ROW, frame_height)

    def update(self, candidates: list[Segment]) -> TrackedLine | None:
        extendable_candidates = [segment for segment in candidates if not is_horizontal(segment)]
        if not extendable_candidates:
            return None
        longest_segment = max(extendable_candidates, key=compute_segment_length)
        return TrackedLine(
            bottom_x=compute_x_at_row(longest_segment, self.bottom_row),
            bottom_y=self.bottom_row,
            top_x=compute_x_at_row(longest_segment, self.top_row),
            top_y=self.top_row,
            status=TrackingStatus.DETECTED,
        )
