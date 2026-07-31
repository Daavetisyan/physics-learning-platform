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
        if "rest" in lower or "stop" in lower or "average" in lower:
            return "Draw a journey timeline. Add every traveled distance, then decide whether the question asks for complete elapsed time or moving time. For the complete trip, where does the stop appear in your total time?"
        return (
            "List the known distance, time, and speed with units. Name the unknown, then choose v = d/t, d = vt, or t = d/v. "
            "Before calculating, are the distance and time units compatible?"
        )
    if mode == "check":
        nums = _extract_numbers(message)
        if len(nums) >= 2:
            distance, time = nums[0], nums[1]
            if time == 0:
                return "Time cannot be zero. Check the values copied from the problem."
            return f"Using the first value as distance and the second as time, {distance:g} ÷ {time:g} = {distance/time:g}. Check that you used total distance, included required stop time, and attached a distance-per-time unit."
        return "Show the known values, chosen formula, substitution, unit conversion, and final unit. I will check each step without treating speed as directional."
    if "difference" in lower or ("speed" in lower and "velocity" in lower):
        return "Speed describes how fast using distance. Velocity describes rate of change of position and includes direction."
    if "rest" in lower or "stop" in lower:
        return "For average speed over the complete journey, rest time belongs in total elapsed time even though no distance is added during the stop. Exclude it only if the problem explicitly asks for average speed while moving."
    if "divide" in lower or "why" in lower:
        return "Dividing distance by time shares the path across equal time units. For example, 20 m ÷ 4 s means 5 meters belong to each second, so the speed is 5 m/s."
    return "Speed is total distance divided by total time. Tell me which values are known, including units, and whether the journey contains a stop."


def _distance_displacement_response(message: str, mode: str) -> str:
    lower = message.lower()
    nums = _extract_numbers(message)
    if mode == "guide":
        return (
            "First identify the initial and final positions. Next list every turning point in path order. "
            "Does the question ask for total path length or endpoint change? For distance, add the absolute length of each segment. "
            "For displacement, use Δx = x_f − x_i. What does the resulting sign mean under the stated positive direction?"
        )
    if mode == "check":
        if len(nums) >= 2:
            initial, final = nums[0], nums[-1]
            result = final - initial
            return (
                f"Using the first value as x_i and the last as x_f gives Δx = {final:g} − ({initial:g}) = {result:g}. "
                "That checks displacement only. To check distance, send every position or movement segment in order and include the unit."
            )
        return "Show x_i, x_f, every turning point, the positive direction, and your unit. I will check the subtraction order, segment magnitudes, and sign interpretation."
    if "zero" in lower or "round" in lower:
        return "A round trip can have zero displacement because x_f equals x_i, while distance remains positive because the complete outward and return paths are added."
    if "negative" in lower:
        return "Negative displacement means the change points opposite the chosen positive direction. It is not negative distance: distance is the nonnegative total path length."
    if "distance" in lower and "displacement" in lower:
        return "Distance follows and adds the entire path. Displacement compares only the endpoints with Δx = x_f − x_i and includes direction. Tell me the route and endpoints, and we can calculate both."
    return "Name the initial position, final position, every turning point, positive direction, and unit. Then decide whether you need total path length or signed change in position."


def answer_as_scientist(message: str, mode: str = "explain", lesson_slug: str = "position-reference-points") -> str:
    text = message.strip()
    if not text:
        return "Ask about the exact idea, diagram, sign, unit, or calculation that is confusing."
    if lesson_slug == "position-reference-points":
        return _position_response(text, mode)
    if lesson_slug == "distance-displacement":
        return _distance_displacement_response(text, mode)
    if lesson_slug == "speed":
        return _speed_response(text, mode)
    return _speed_response(text, mode)
