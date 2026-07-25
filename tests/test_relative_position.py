from app.relative_position import (
    ConstantVelocityObject,
    describe_relative_position,
    displayed_coordinate,
    physical_distance,
    relative_position,
    within_tolerance,
)


def test_relative_position_right_positive():
    assert relative_position(4, 1, "right") == 3


def test_relative_position_left_positive():
    assert relative_position(4, 1, "left") == -3


def test_changing_origin_changes_coordinates():
    assert displayed_coordinate(7, 0, "right") == 7
    assert displayed_coordinate(7, 2, "right") == 5


def test_changing_origin_does_not_change_physical_separation():
    before = physical_distance(7, 2)
    shifted_coordinates = (
        displayed_coordinate(7, 4),
        displayed_coordinate(2, 4),
    )
    after = physical_distance(*shifted_coordinates)
    assert before == after == 5


def test_physical_distance_is_always_non_negative():
    assert physical_distance(-6, 3) == 9
    assert physical_distance(3, -6) == 9
    assert physical_distance(2, 2) == 0


def test_moving_reference_updates_relative_position():
    cyclist = ConstantVelocityObject(world_x=2, velocity=1.5)
    later = cyclist.after(2)
    assert later.world_x == 5
    assert relative_position(4, cyclist.world_x) == 2
    assert relative_position(4, later.world_x) == -1


def test_mission_tolerance_validation():
    assert within_tolerance(3.12, 3, 0.15)
    assert not within_tolerance(3.2, 3, 0.15)


def test_plain_language_left_right_descriptions():
    right = describe_relative_position(4, 1, "Dog", "right")
    left = describe_relative_position(-2, 1, "Cyclist", "left")
    same = describe_relative_position(1, 1, "Building", "right")
    assert "3.0 m to the right of the dog" in right
    assert "+3.0 m with left positive" in left
    assert "same position" in same
