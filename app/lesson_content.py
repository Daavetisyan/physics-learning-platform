from __future__ import annotations

POSITION_REFERENCE_POINTS = {
    "status": "production",
    "scientist": {
        "name": "Galileo Galilei",
        "initials": "GG",
        "subtitle": "AI educational character inspired by Galileo",
        "opening": "Describe exactly what you observe. Then tell me: observed from where?",
    },
    "grade_band": "Grades 7–9",
    "estimated_time": "70–90 min",
    "essential_question": "How can two people describe the same object's location differently and both be correct?",
    "objectives": [
        "Explain why every position description needs a reference point.",
        "Represent position on a one-dimensional coordinate line using an origin, direction, number, and unit.",
        "Calculate the relative position of one object compared with another.",
        "Explain why position and motion can depend on the chosen frame of reference.",
        "Choose a useful reference frame for a real physical situation and justify the choice.",
    ],
    "prerequisites": [
        "Read positive and negative numbers on a number line.",
        "Measure or estimate length in meters and centimeters.",
        "Use the words left, right, east, west, above, and below precisely.",
    ],
    "diagnostic": {
        "question": "A backpack is 'three meters away.' Is that enough information to locate it?",
        "options": [
            "Yes, because the distance is known.",
            "No, because we also need to know three meters from what and in which direction.",
            "Yes, if the backpack is not moving.",
        ],
        "correct": "No, because we also need to know three meters from what and in which direction.",
        "explanation": "A number and unit alone give a distance, not a complete position. A position must be stated relative to a chosen reference point and direction.",
    },
    "vocabulary": [
        {
            "term": "Position",
            "definition": "The location of an object relative to a chosen reference point or coordinate system.",
            "example": "The cart is 4 m east of the starting line.",
        },
        {
            "term": "Reference point",
            "definition": "An object or location used as the comparison point when describing position or motion.",
            "example": "A classroom door can be the reference point for locating a desk.",
        },
        {
            "term": "Frame of reference",
            "definition": "The complete viewpoint or coordinate system from which positions and motions are measured.",
            "example": "A passenger can describe a ball relative to the train, while an observer outside describes it relative to the ground.",
        },
        {
            "term": "Origin",
            "definition": "The point assigned coordinate zero in a coordinate system.",
            "example": "If the tree is chosen as x = 0 m, the tree is the origin.",
        },
        {
            "term": "Coordinate",
            "definition": "A signed number, together with a unit, that identifies position along an axis.",
            "example": "x = -3 m means three meters in the negative direction from the origin.",
        },
        {
            "term": "Positive direction",
            "definition": "The direction chosen to correspond to increasing coordinate values.",
            "example": "If right is positive, positions to the left of the origin have negative coordinates.",
        },
        {
            "term": "Relative position",
            "definition": "The position of one object measured from another object rather than from the original origin.",
            "example": "If Maya is at 7 m and Leo is at 2 m, Maya is 5 m to the right of Leo.",
        },
    ],
    "theory_chapters": [
        {
            "number": 1,
            "heading": "Location words are incomplete without a comparison",
            "lead": "Physics begins by replacing vague location words with measurable descriptions.",
            "paragraphs": [
                "In everyday conversation, people often say that an object is 'over there,' 'nearby,' or 'five meters away.' Such phrases may work when everyone can see the same scene, but they are not precise enough for science. The phrase 'five meters away' immediately raises a question: five meters away from what? A desk may be five meters from the door, two meters from the wall, and ten meters from the teacher at the same moment.",
                "A physical position is therefore not a property that can be stated in isolation. Position is a relationship between the object being described and something chosen for comparison. That comparison object or location is called the reference point. A complete statement identifies the object, the reference point, the direction, the numerical amount, and the unit.",
                "For example, 'The cart is 4 m east of the starting line' is complete enough for a one-dimensional situation. The cart is the object, the starting line is the reference point, east is the direction, 4 is the numerical value, and meters are the unit. Each part matters. Without the reference point or direction, many different locations could match the description.",
            ],
            "key_idea": "Position answers 'Where is the object relative to the chosen reference point?'",
            "check": {
                "question": "Which statement gives the most complete position description?",
                "options": [
                    "The bicycle is 8 m away.",
                    "The bicycle is near the building.",
                    "The bicycle is 8 m west of the school entrance.",
                ],
                "correct": "The bicycle is 8 m west of the school entrance.",
                "explanation": "It includes a measurable amount, a unit, a direction, and a reference point.",
            },
        },
        {
            "number": 2,
            "heading": "Choosing a useful reference point",
            "lead": "There is usually more than one valid reference point, but some choices make a problem much easier.",
            "paragraphs": [
                "Imagine describing a student's position in a school hallway. You could measure from the classroom door, the end of the hallway, the drinking fountain, or even the front entrance of the school. Any stable, clearly identified point can serve as a reference point. The physical student does not change location just because you choose a different comparison point, but the numerical description of the position does change.",
                "A useful reference point is easy to identify, does not move unexpectedly, and makes the important measurements simple. For a 100 m race, the starting line is a natural choice. For a car approaching an intersection, the intersection may be the useful reference point. For a book on a table, one corner of the table may be chosen as the reference point.",
                "Scientists choose reference points deliberately. A poor choice can make coordinates awkward or obscure the pattern being studied. A good choice can make the same situation simple. This is not changing reality; it is choosing an efficient language for describing reality.",
            ],
            "key_idea": "Different reference points produce different coordinates, but they describe the same physical arrangement.",
            "check": {
                "question": "For measuring runners during a 100 m race, which reference point is usually most useful?",
                "options": ["The starting line", "A moving spectator", "A cloud above the field"],
                "correct": "The starting line",
                "explanation": "It is fixed, clearly marked, and directly connected to the distances in the race.",
            },
        },
        {
            "number": 3,
            "heading": "From a reference point to a coordinate system",
            "lead": "A reference point becomes much more powerful when we assign it zero and choose a positive direction.",
            "paragraphs": [
                "In one-dimensional motion, objects move along a straight path such as a road, hallway, track, or horizontal laboratory bench. We can represent that path with a number line called a coordinate axis. The chosen reference point is assigned the coordinate zero and is called the origin.",
                "Next, we choose which direction is positive. On a drawing, right is often chosen as positive and left as negative, but that convention is not required. We might instead choose east as positive, upward as positive, or the direction of the initial motion as positive. The important requirement is consistency: once a direction is chosen as positive, the opposite direction must be negative throughout the problem.",
                "A coordinate such as x = +6 m means that the object is six meters from the origin in the positive direction. A coordinate such as x = -2 m means that it is two meters from the origin in the negative direction. The sign does not mean that the physical distance is negative. Distance from the origin is a nonnegative magnitude; the sign communicates direction on the axis.",
            ],
            "formula": "position = signed coordinate + unit, for example x = -2 m",
            "key_idea": "The origin defines zero; the chosen positive direction determines the signs of all other coordinates.",
            "check": {
                "question": "Right is positive. An object is 5 m left of the origin. What is its coordinate?",
                "options": ["x = +5 m", "x = -5 m", "x = 0 m"],
                "correct": "x = -5 m",
                "explanation": "Left is the negative direction when right has been chosen as positive.",
            },
        },
        {
            "number": 4,
            "heading": "A coordinate needs a unit",
            "lead": "The number tells how many units; the unit tells what size each step represents.",
            "paragraphs": [
                "Writing x = 5 is incomplete in a physical situation. Five meters, five centimeters, and five kilometers describe very different locations. A physical coordinate must include an appropriate unit. For classroom-scale measurements, centimeters or meters are common. For roads and cities, kilometers or miles may be more practical.",
                "Before comparing positions or performing calculations, coordinates must use compatible units. Suppose one object is at 150 cm and another is at 2 m. We should convert one value so both are expressed in the same unit: 150 cm = 1.5 m. Only then is the difference easy to interpret.",
                "Units also protect us from meaningless answers. If a calculation subtracts one position in meters from another position in meters, the result is in meters. If the units do not match, the calculation must be repaired before the numerical answer is trusted.",
            ],
            "key_idea": "A coordinate without a unit is not a complete physical position.",
            "check": {
                "question": "Which pair can be subtracted immediately without conversion?",
                "options": ["3 m and 40 cm", "2.5 m and -1.0 m", "6 km and 20 m"],
                "correct": "2.5 m and -1.0 m",
                "explanation": "Both coordinates are already written in meters.",
            },
        },
        {
            "number": 5,
            "heading": "Relative position between two objects",
            "lead": "We can use one object as the temporary reference point for another.",
            "paragraphs": [
                "Suppose Maya stands at x = 7 m and Leo stands at x = 2 m on the same axis, with right positive. From the original origin, their coordinates are 7 m and 2 m. But we may ask a different question: where is Maya relative to Leo? To answer, treat Leo's position as the comparison point.",
                "The relative position of object A with respect to object B is found by subtracting B's coordinate from A's coordinate. In symbols, x(A relative to B) = x_A - x_B. For Maya relative to Leo, 7 m - 2 m = +5 m. The positive sign means Maya is five meters in the positive direction, or five meters to the right of Leo.",
                "Order matters. Leo relative to Maya is 2 m - 7 m = -5 m. This says Leo is five meters in the negative direction from Maya. The magnitudes are equal because the separation is five meters, but the signs are opposite because the directions are opposite.",
            ],
            "formula": "x(A relative to B) = x_A - x_B",
            "key_idea": "Switching the order reverses the sign: x(A relative to B) = -x(B relative to A).",
            "check": {
                "question": "A is at -2 m and B is at +4 m. What is A's position relative to B?",
                "options": ["+6 m", "-6 m", "+2 m"],
                "correct": "-6 m",
                "explanation": "x_A - x_B = -2 m - 4 m = -6 m, so A is 6 m in the negative direction from B.",
            },
        },
        {
            "number": 6,
            "heading": "Position depends on the frame of reference",
            "lead": "The same object can have different valid coordinates in different frames.",
            "paragraphs": [
                "Consider a passenger sitting in seat 12 on a moving train. Relative to the train, the passenger's position may remain constant: the passenger stays in the same seat. Relative to the ground, however, the passenger's position changes continuously as the train moves along the track. Both descriptions are correct because they use different frames of reference.",
                "A frame of reference includes more than a single point. It includes the origin, the coordinate axes, the positive directions, the measuring scale, and usually an observer or set of objects treated as fixed. The train frame treats the train as fixed. The ground frame treats the track and Earth as fixed for the situation.",
                "This idea is central to all motion. Before stating that an object is at rest or moving, we must ask: at rest or moving relative to what? A phone resting on a car seat is stationary relative to the car but moving relative to the road. Physics does not remove this dependence; it states the reference frame clearly.",
            ],
            "key_idea": "At rest and moving are relational descriptions, not absolute labels.",
            "check": {
                "question": "A cup sits on the tray table of a flying airplane. Which statement is best?",
                "options": [
                    "The cup is absolutely at rest.",
                    "The cup is at rest relative to the airplane but moving relative to the ground.",
                    "The cup is moving relative to the airplane and at rest relative to the ground.",
                ],
                "correct": "The cup is at rest relative to the airplane but moving relative to the ground.",
                "explanation": "Its position does not change in the airplane frame, but it changes in the ground frame.",
            },
        },
        {
            "number": 7,
            "heading": "Changing the origin changes coordinates, not the physical scene",
            "lead": "Coordinate values are labels assigned by a system; they are not the objects themselves.",
            "paragraphs": [
                "Place two markers on a floor, one at 3 m and one at 8 m from a wall chosen as the origin. Their separation is 5 m. Now choose the first marker as the new origin. In the new system, the first marker is at 0 m and the second is at 5 m. The coordinate labels changed, but neither marker moved and their separation remained 5 m.",
                "This distinction prevents a common misunderstanding. A coordinate may change because the object moves, but it may also change because the observer changes the coordinate system. When analyzing data, always check whether the physical object changed position or whether only the reference frame was redefined.",
                "Quantities describing relationships between objects, such as their separation, often remain the same under a simple shift of origin. Individual coordinates change by the same amount, so their difference is preserved. This is one reason relative position is so useful.",
            ],
            "key_idea": "A new origin relabels locations; it does not physically move objects.",
            "check": {
                "question": "Two cones are 4 m apart. The origin is moved from one wall to another. What must remain unchanged?",
                "options": ["Each cone's coordinate", "The cones' separation", "Which direction is positive"],
                "correct": "The cones' separation",
                "explanation": "Coordinates may be relabeled, but the physical distance between the cones does not change.",
            },
        },
        {
            "number": 8,
            "heading": "Reversing the positive direction reverses coordinate signs",
            "lead": "The sign of a coordinate depends on the axis orientation chosen by the observer.",
            "paragraphs": [
                "Suppose a tree is 6 m east of a bench. If east is positive and the bench is the origin, the tree's coordinate is +6 m. If we keep the same origin but choose west as positive, the same tree receives the coordinate -6 m. The physical tree has not moved; only the axis direction has been reversed.",
                "A negative coordinate therefore does not automatically mean west, left, down, or bad. It means opposite to whichever direction was defined as positive. In one problem, north might be positive; in another, south might be positive. Always read the coordinate definition before interpreting the sign.",
                "When solving a multi-step problem, write the positive-direction convention near the diagram. This small habit prevents sign errors later when displacement, velocity, acceleration, and force are introduced.",
            ],
            "key_idea": "Signs have meaning only after the positive direction is defined.",
            "check": {
                "question": "The origin stays fixed, but the positive direction is reversed. What happens to every coordinate?",
                "options": ["Its sign reverses", "Its magnitude doubles", "It becomes zero"],
                "correct": "Its sign reverses",
                "explanation": "Each object is now on the opposite signed side of the newly oriented axis, while its distance from the origin stays the same.",
            },
        },
        {
            "number": 9,
            "heading": "Extending position into two dimensions",
            "lead": "One coordinate is enough for a straight line; a flat surface usually requires two.",
            "paragraphs": [
                "A hallway can often be modeled in one dimension because movement is mainly forward and backward along one line. A classroom floor, sports field, or city map requires two independent directions. We then use an x-axis and a y-axis that intersect at the origin.",
                "A two-dimensional position is written as an ordered pair such as (3 m, -2 m). The first coordinate gives the horizontal position along x, and the second gives the vertical or north-south position along y, according to the chosen directions. Order matters: (3, -2) is not the same as (-2, 3).",
                "This course will begin with one-dimensional motion because it makes the essential ideas visible without unnecessary complexity. The same principles remain true in two and three dimensions: position depends on an origin, axes, directions, scale, and reference frame.",
            ],
            "key_idea": "The number of coordinates needed matches the number of independent directions in the model.",
            "check": {
                "question": "Which situation most clearly requires two position coordinates?",
                "options": ["A train moving on a straight track", "A student moving around a basketball court", "An elevator moving vertically"],
                "correct": "A student moving around a basketball court",
                "explanation": "The student can move independently in two directions across the court's surface.",
            },
        },
    ],
    "video": {
        "title": "Why 'Where is it?' is a physics question",
        "target_duration": "8–10 minutes",
        "storyboard": [
            "Open with one object described from three different locations: the door, the camera, and another student.",
            "Show why 'five meters away' is incomplete by placing several possible points five meters from the speaker.",
            "Tape a coordinate line on the floor and define the origin and positive direction.",
            "Place objects at positive and negative coordinates and emphasize that negative means direction, not negative distance.",
            "Use two students to calculate relative position in both orders.",
            "Finish inside a moving car or bus: an object can be at rest relative to the vehicle and moving relative to the road.",
        ],
        "filming_notes": [
            "Keep the coordinate line visible whenever signed positions are discussed.",
            "Display the chosen reference frame in a small on-screen label.",
            "Pause before each answer and invite the student to predict the coordinate.",
            "Use meters consistently in the first recording; introduce conversions in a separate inserted example.",
        ],
    },
    "simulation": {
        "type": "position_reference_frame",
        "title": "Reference Frame Laboratory",
        "instruction": "Move two objects, change the reference point, and reverse the positive direction. Watch which values change and which physical relationships stay the same.",
        "prediction": "If Object A and Object B stay fixed but Object A becomes the new origin, what must Object A's new coordinate be?",
        "prediction_options": ["Its old coordinate", "0 m", "The separation between A and B"],
        "prediction_correct": "0 m",
        "prediction_explanation": "The selected origin is defined to have coordinate zero.",
    },
    "worked_examples": [
        {
            "title": "Example 1: Reading a coordinate",
            "question": "Right is positive and the flag is the origin. A ball is 3 m left of the flag. State the ball's coordinate.",
            "steps": [
                "Write the convention: right is positive, so left is negative.",
                "The ball is 3 m from the origin in the negative direction.",
                "Attach the sign and unit: x = -3 m.",
            ],
            "answer": "x = -3 m",
            "reasoning": "The magnitude 3 m gives the distance from the origin; the negative sign communicates the chosen direction.",
        },
        {
            "title": "Example 2: Changing the origin",
            "question": "A cart is at x = 9 m when a wall is the origin. A cone at x = 4 m is chosen as the new origin. What is the cart's new coordinate?",
            "steps": [
                "The new coordinate measures the cart from the cone.",
                "Subtract the new origin's old coordinate: 9 m - 4 m.",
                "The result is +5 m, so the cart is 5 m in the positive direction from the cone.",
            ],
            "answer": "x' = +5 m",
            "reasoning": "Shifting the origin subtracts the same reference coordinate from every old coordinate.",
        },
        {
            "title": "Example 3: Relative position",
            "question": "Ava is at x = -2 m and Ben is at x = +5 m. Find Ava's position relative to Ben.",
            "steps": [
                "Use x(Ava relative to Ben) = x_Ava - x_Ben.",
                "Substitute: -2 m - (+5 m).",
                "Calculate: -7 m.",
                "Interpret: Ava is 7 m in the negative direction from Ben.",
            ],
            "answer": "-7 m",
            "reasoning": "The negative sign tells direction from Ben to Ava; the separation has magnitude 7 m.",
        },
        {
            "title": "Example 4: Same object, two frames",
            "question": "A passenger sits still on a bus traveling east. Describe the passenger's motion relative to the bus and relative to the road.",
            "steps": [
                "In the bus frame, compare the passenger with seats and walls of the bus.",
                "The passenger's position relative to the bus does not change, so the passenger is at rest in that frame.",
                "In the road frame, the passenger moves east with the bus, so the passenger is moving in that frame.",
            ],
            "answer": "At rest relative to the bus; moving east relative to the road.",
            "reasoning": "Motion statements are incomplete until the frame of reference is named.",
        },
        {
            "title": "Example 5: Unit conversion before comparison",
            "question": "A marker is at 160 cm and a cart is at 2.4 m. How far to the right of the marker is the cart?",
            "steps": [
                "Convert 160 cm to meters: 160 cm = 1.60 m.",
                "Calculate the cart relative to the marker: 2.40 m - 1.60 m.",
                "The result is +0.80 m.",
            ],
            "answer": "0.80 m to the right",
            "reasoning": "Coordinates must use the same units before subtraction.",
        },
    ],
    "misconceptions": [
        {
            "myth": "A negative position means a negative distance.",
            "correction": "Distance from the origin is a magnitude and cannot be negative. The coordinate sign indicates direction relative to the chosen positive direction.",
        },
        {
            "myth": "There is only one correct reference point.",
            "correction": "Many reference points can be valid. A good choice is stable, clear, and useful for the question being studied.",
        },
        {
            "myth": "If coordinates change, the objects must have moved.",
            "correction": "Coordinates can also change because the origin or axis direction was changed. Check whether the physical arrangement changed.",
        },
        {
            "myth": "An object is either moving or at rest, absolutely.",
            "correction": "An object can be at rest in one frame and moving in another. The frame must be stated.",
        },
        {
            "myth": "The relative position of A from B is the same as B from A.",
            "correction": "They have equal magnitude but opposite signs because the directions are reversed.",
        },
    ],
    "practice_groups": [
        {
            "level": "Foundation",
            "description": "Build accurate language and read signed coordinates.",
            "questions": [
                "A lamp is 2 m right of a doorway. Write a complete position statement using the doorway as the reference point.",
                "Right is positive. Give the coordinates of objects 4 m right and 4 m left of the origin.",
                "Explain why the statement 'The chair is 3 m away' is incomplete.",
                "A toy is at x = -6 cm. Describe its location in words if right is positive.",
            ],
        },
        {
            "level": "Standard",
            "description": "Calculate relative position and reason about changing origins.",
            "questions": [
                "A is at x = -3 m and B is at x = +2 m. Find A relative to B and B relative to A.",
                "A tree is at x = 12 m and a bench is at x = 5 m. The bench becomes the new origin. Find the tree's new coordinate.",
                "A student is at 250 cm and a backpack is at 1.2 m. Find the student's position relative to the backpack in meters.",
                "Describe a phone on a train seat relative to the train and relative to the ground while the train moves.",
            ],
        },
        {
            "level": "Challenge",
            "description": "Connect coordinate choices to invariants and modeling decisions.",
            "questions": [
                "Three objects have coordinates -4 m, +1 m, and +7 m. Choose the middle object as the new origin and write all three new coordinates.",
                "The positive direction is reversed while the origin stays fixed. Explain what happens to individual coordinates and to the separation between any two objects.",
                "Design two different coordinate systems for the same basketball court. Explain one advantage of each system.",
                "A passenger walks toward the rear of a train while the train moves forward. Explain what additional information is needed to determine whether the passenger moves forward or backward relative to the ground.",
            ],
        },
    ],
    "quiz": [
        {
            "id": "q1",
            "question": "Which information is required for a complete one-dimensional position description?",
            "options": [
                "Only a number",
                "A reference point, direction, numerical value, and unit",
                "Only the object's name and speed",
            ],
            "correct": "A reference point, direction, numerical value, and unit",
        },
        {
            "id": "q2",
            "question": "Right is positive. A cart is 7 m left of the origin. Its coordinate is:",
            "options": ["+7 m", "-7 m", "0 m"],
            "correct": "-7 m",
        },
        {
            "id": "q3",
            "question": "A is at +6 m and B is at +1 m. What is A relative to B?",
            "options": ["+5 m", "-5 m", "+7 m"],
            "correct": "+5 m",
        },
        {
            "id": "q4",
            "question": "If A relative to B is -4 m, then B relative to A is:",
            "options": ["-4 m", "+4 m", "0 m"],
            "correct": "+4 m",
        },
        {
            "id": "q5",
            "question": "A book rests on a desk inside a moving train. Which statement is correct?",
            "options": [
                "It is at rest relative to both train and ground.",
                "It is moving relative to the train but at rest relative to the ground.",
                "It is at rest relative to the train but moving relative to the ground.",
            ],
            "correct": "It is at rest relative to the train but moving relative to the ground.",
        },
        {
            "id": "q6",
            "question": "The origin moves from x = 0 m to the old coordinate x = 3 m. An object was at x = 8 m. Its new coordinate is:",
            "options": ["+11 m", "+5 m", "-5 m"],
            "correct": "+5 m",
        },
        {
            "id": "q7",
            "question": "What definitely remains unchanged when only the origin is shifted?",
            "options": ["Every coordinate", "The separation between fixed objects", "Every coordinate sign"],
            "correct": "The separation between fixed objects",
        },
        {
            "id": "q8",
            "question": "Why can a negative coordinate not be interpreted before the axis is defined?",
            "options": [
                "Because negative numbers have no physical meaning",
                "Because the negative sign means opposite to the chosen positive direction",
                "Because all distances must be positive",
            ],
            "correct": "Because the negative sign means opposite to the chosen positive direction",
        },
    ],
    "homework": {
        "title": "Map a real space with a coordinate system",
        "instructions": "Choose a straight path at home or school, such as a hallway, room edge, or sidewalk. Define a coordinate system and answer all parts. Use a sketch if helpful.",
        "questions": [
            "Identify your origin and explain why it is a useful reference point.",
            "State the positive direction clearly.",
            "Choose three objects and record their signed positions with units.",
            "Calculate the relative position of Object 1 from Object 2, then reverse the order.",
            "Choose a different origin and rewrite all three coordinates.",
            "Explain which physical relationships stayed unchanged after the origin changed.",
            "Give one example of an object that is at rest in one frame but moving in another.",
        ],
        "submission_prompt": "Write your coordinate definitions, measurements, calculations, and explanations here. A strong response includes units and interprets every sign.",
    },
    "summary": [
        "Position is the location of an object relative to a selected reference point or frame.",
        "In one dimension, the reference point is usually assigned coordinate zero and called the origin.",
        "A positive direction must be defined before signed coordinates can be interpreted.",
        "A complete physical coordinate includes a numerical value and a unit.",
        "Relative position is found by subtraction: x(A relative to B) = x_A - x_B.",
        "Changing the origin or axis direction changes coordinate labels but does not move the objects.",
        "An object may be at rest in one frame and moving in another, so every motion statement needs a frame of reference.",
    ],
    "reflection": "Name one description of location you used today outside physics. What was the hidden reference point?",
}

LESSON_CONTENTS = {
    "position-reference-points": POSITION_REFERENCE_POINTS,
}
