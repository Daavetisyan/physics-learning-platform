from __future__ import annotations

from dataclasses import dataclass


def direction_multiplier(positive_direction: str) -> int:
    if positive_direction not in {"right", "left"}:
        raise ValueError("positive_direction must be 'right' or 'left'")
    return 1 if positive_direction == "right" else -1


def displayed_coordinate(world_x: float, origin_world_x: float, positive_direction: str = "right") -> float:
    return direction_multiplier(positive_direction) * (world_x - origin_world_x)


def relative_position(player_world_x: float, reference_world_x: float, positive_direction: str = "right") -> float:
    return direction_multiplier(positive_direction) * (player_world_x - reference_world_x)


def physical_distance(first_world_x: float, second_world_x: float) -> float:
    return abs(first_world_x - second_world_x)


def within_tolerance(actual: float, target: float, tolerance: float = 0.15) -> bool:
    return abs(actual - target) <= tolerance


def describe_relative_position(
    player_world_x: float,
    reference_world_x: float,
    reference_label: str,
    positive_direction: str = "right",
) -> str:
    difference = player_world_x - reference_world_x
    if abs(difference) < 0.05:
        return f"You and the {reference_label.lower()} are at the same position."
    physical_direction = "right" if difference > 0 else "left"
    signed_position = relative_position(player_world_x, reference_world_x, positive_direction)
    sign = "+" if signed_position >= 0 else "-"
    return (
        f"You are {abs(difference):.1f} m to the {physical_direction} of the {reference_label.lower()} "
        f"({sign}{abs(signed_position):.1f} m with {positive_direction} positive)."
    )


@dataclass(frozen=True)
class ConstantVelocityObject:
    world_x: float
    velocity: float

    def after(self, elapsed_seconds: float) -> "ConstantVelocityObject":
        return ConstantVelocityObject(self.world_x + self.velocity * elapsed_seconds, self.velocity)
