from __future__ import annotations

from math import hypot
from typing import Tuple

Point = Tuple[float, float]


def distance(a: Point, b: Point) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])


def is_extended(tip: Point, pip: Point, margin: float = 0.015) -> bool:
    return tip[1] < pip[1] - margin


def is_pinching(a: Point, b: Point, palm_size: float, ratio: float = 0.28) -> bool:
    if palm_size <= 0:
        return False
    return distance(a, b) <= palm_size * ratio


def classify_gesture(
    *,
    thumb: Point,
    index_tip: Point,
    index_pip: Point,
    middle_tip: Point,
    middle_pip: Point,
    wrist: Point,
    middle_mcp: Point,
) -> str:
    """Return one of: left_click, right_click, move, scroll_up, scroll_down, none."""

    palm_size = max(distance(wrist, middle_mcp), 1e-6)
    index_extended = is_extended(index_tip, index_pip)
    middle_extended = is_extended(middle_tip, middle_pip)

    index_pinch = is_pinching(thumb, index_tip, palm_size)
    middle_pinch = is_pinching(thumb, middle_tip, palm_size)

    if index_pinch:
        return "left_click"

    if middle_pinch:
        return "right_click"

    if index_extended and not middle_extended:
        return "move"

    if index_extended and middle_extended:
        vertical_gap = (middle_tip[1] - index_tip[1]) / palm_size
        if vertical_gap > 0.45:
            return "scroll_up"
        if vertical_gap < -0.45:
            return "scroll_down"

    return "none"
