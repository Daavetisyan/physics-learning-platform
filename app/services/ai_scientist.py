from __future__ import annotations

import re


def _extract_numbers(text: str) -> list[float]:
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", text)]


def _position_response(message: str, mode: str) -> str:
    lower = message.lower()

    if mode == "guide":
        if any(word in lower for word in ["relative", "between", "from b", "from a"]):
            return (
                "Let us define the order before calculating. Which object are you locating, and which object is the reference? "
                "Write their coordinates as x_object and x_reference, then evaluate x_object - x_reference. What sign do you get, and what direction does that sign represent?"
            )
        if any(word in lower for word in ["negative", "positive", "sign"]):
            return (
                "First state the chosen positive direction. The negative direction is simply the opposite. "
                "Now ask: on which side of the origin is the object? The sign comes from that choice, not from the object's distance."
            )
        return (
            "Start by naming four things: the object, the reference point, the positive direction, and the unit. "
            "Then tell me the object's signed coordinate. Which of those four pieces is still missing?"
        )

    if mode == "check":
        nums = _extract_numbers(message)
        if "relative" in lower and len(nums) >= 2:
            object_position, reference_position = nums[0], nums[1]
            result = object_position - reference_position
            return (
                f"Using the first value as the object's coordinate and the second as the reference coordinate: "
                f"{object_position:g} - ({reference_position:g}) = {result:g}. "
                "Check that your subtraction order matches the words 'object relative to reference,' then interpret the sign using the stated positive direction."
            )
        return (
            "Show your chosen origin, positive direction, coordinates with units, and subtraction order. "
            "I will check whether the signs describe the intended directions and whether your interpretation matches the calculation."
        )

    if "reference point" in lower or "origin" in lower:
        return (
            "A reference point is the place or object used for comparison. When we assign that point coordinate zero, it becomes the origin of the coordinate system. "
            "Changing the origin changes the coordinate labels, but it does not physically move the objects."
        )
    if "frame" in lower or "train" in lower or "car" in lower or "moving" in lower:
        return (
            "A frame of reference is the full viewpoint used for measurement. A passenger may be at rest relative to a train because the passenger's position inside it is constant, "
            "while the same passenger moves relative to the ground. Always finish a motion statement with 'relative to what?'"
        )
    if "negative" in lower or "minus" in lower:
        return (
            "A negative coordinate does not mean a negative distance. It means the object lies opposite to the chosen positive direction. "
            "If right is positive, left-side coordinates are negative; if the axis is reversed, the signs reverse too."
        )
    if "relative" in lower:
        return (
            "To find A relative to B, subtract in that order: x_A - x_B. The magnitude gives their separation along the line, and the sign tells which direction A lies from B. "
            "Reversing the order gives the opposite sign."
        )
    if "position" in lower:
        return (
            "A complete position description needs a reference point, a direction, a numerical value, and a unit. "
            "For example, '4 m east of the door' is complete, while '4 m away' is not."
        )
    return (
        "Let us describe the situation like an experiment. Identify the reference point, assign an origin, choose the positive direction, and write every coordinate with a unit. "
        "Then we can decide whether the question asks for a coordinate, a separation, or a relative position."
    )


def _speed_response(message: str, mode: str) -> str:
    lower = message.lower()
    if mode == "guide":
        return (
            "Did the question use total path length or change in position? That tells you whether to use distance or displacement. "
            "Then divide by total time and include direction if the quantity is velocity."
        )
    if mode == "check":
        nums = _extract_numbers(message)
        if len(nums) >= 2:
            distance, time = nums[0], nums[1]
            if time == 0:
                return "Time cannot be zero. Check the values copied from the problem."
            return f"Using the first two values, {distance:g} ÷ {time:g} = {distance/time:g}. Now verify the units and whether direction is required."
        return "Show the relationship, substituted values, units, and direction if the problem asks for velocity."
    if "difference" in lower or ("speed" in lower and "velocity" in lower):
        return "Speed describes how fast using distance. Velocity describes rate of change of position and includes direction."
    return "Average speed is total distance divided by total time. Average velocity is displacement divided by total time and needs direction."


def answer_as_scientist(message: str, mode: str = "explain", lesson_slug: str = "position-reference-points") -> str:
    text = message.strip()
    if not text:
        return "Ask about the exact idea, diagram, sign, unit, or calculation that is confusing."
    if lesson_slug == "position-reference-points":
        return _position_response(text, mode)
    return _speed_response(text, mode)
