from __future__ import annotations

from collections.abc import Sequence


def total_distance(positions: Sequence[float]) -> float:
    """Return the sum of the absolute lengths of every journey segment."""
    return sum(abs(end - start) for start, end in zip(positions, positions[1:]))


def displacement(positions: Sequence[float], positive_direction: str = "right") -> float:
    """Return signed final-minus-initial displacement in the selected orientation."""
    if len(positions) < 2:
        return 0.0
    value = positions[-1] - positions[0]
    if positive_direction == "left":
        return -value
    if positive_direction != "right":
        raise ValueError("positive_direction must be 'right' or 'left'")
    return value


def displacement_magnitude(positions: Sequence[float]) -> float:
    return abs(displacement(positions))
