from __future__ import annotations


def _nonnegative(value: float, name: str) -> float:
    value = float(value)
    if value < 0:
        raise ValueError(f"{name} cannot be negative")
    return value


def calculate_speed(distance: float, time: float) -> float:
    distance = _nonnegative(distance, "distance")
    time = _nonnegative(time, "time")
    if time == 0:
        raise ValueError("time must be greater than zero")
    return distance / time


def calculate_distance(speed: float, time: float) -> float:
    return _nonnegative(speed, "speed") * _nonnegative(time, "time")


def calculate_time(distance: float, speed: float) -> float:
    distance = _nonnegative(distance, "distance")
    speed = _nonnegative(speed, "speed")
    if speed == 0:
        raise ValueError("speed must be greater than zero")
    return distance / speed


def average_speed(segment_distances: list[float], segment_times: list[float]) -> float:
    if len(segment_distances) != len(segment_times) or not segment_distances:
        raise ValueError("matching, nonempty segments are required")
    total_distance = sum(_nonnegative(value, "distance") for value in segment_distances)
    total_time = sum(_nonnegative(value, "time") for value in segment_times)
    if total_time == 0:
        raise ValueError("total time must be greater than zero")
    return total_distance / total_time


def position_at_time(start: float, speed: float, elapsed: float, direction: int = 1) -> float:
    speed = _nonnegative(speed, "speed")
    elapsed = _nonnegative(elapsed, "elapsed time")
    if direction not in {-1, 1}:
        raise ValueError("direction must be -1 or 1")
    return float(start) + direction * speed * elapsed
