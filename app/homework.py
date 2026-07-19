from __future__ import annotations

import json
import math
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .content import COURSE
from .models import (
    HomeworkAnswer,
    HomeworkAssignment,
    HomeworkAttempt,
    HomeworkQuestion,
    Lesson,
    Student,
)

ACTIVE_STATUSES = {"assigned", "in_progress", "needs_revision", "overdue"}
LOCKED_STATUSES = {"submitted", "completed"}


DEMO_HOMEWORK = [
    {
        "slug": "position-reference-points-homework",
        "title": "Position and Reference Points",
        "lesson_slug": "position-reference-points",
        "instructions": "Use coordinates and reference frames to describe positions precisely. Answer every problem and include units where requested.",
        "reference_text": "Position: x. Relative position: x(A relative to B) = x_A − x_B. Physical separation is the absolute difference |x_A − x_B|.",
        "due_days": 3,
        "estimated_minutes": 35,
        "assigned_by": "Platform",
        "status": "assigned",
        "attempt": {"status": "in_progress", "feedback_status": "not_submitted"},
        "questions": [
            {
                "type": "multiple_choice",
                "prompt": "Which statement gives a complete one-dimensional position?",
                "options": ["The cart is nearby.", "The cart is 4 m right of the doorway origin.", "The cart moved 4 m."],
                "correct": "The cart is 4 m right of the doorway origin.",
                "explanation": "A complete position identifies a reference point, direction, numerical value, and unit.",
                "hint": "Look for an origin, direction, value, and unit.",
                "points": 1,
            },
            {
                "type": "multiple_choice",
                "prompt": "An object is at +7 m. The origin shifts to the old +2 m mark without moving the object. What is its new coordinate?",
                "options": ["+9 m", "+5 m", "−5 m"],
                "correct": "+5 m",
                "explanation": "Subtract the new origin position: 7 m − 2 m = +5 m.",
                "hint": "Subtract the new origin coordinate from the old object coordinate.",
                "points": 1,
            },
            {
                "type": "numerical",
                "prompt": "Object A is at +6 m and Object B is at +1 m. Find A relative to B.",
                "correct": "5",
                "unit": "m",
                "tolerance": 0.01,
                "significant_figures": None,
                "explanation": "x_A − x_B = 6 m − 1 m = +5 m.",
                "hint": "Use x_A − x_B and keep the sign.",
                "points": 2,
            },
            {
                "type": "numerical",
                "prompt": "Object A is at −3 m and Object B is at +5 m. Find their physical separation.",
                "correct": "8",
                "unit": "m",
                "tolerance": 0.01,
                "significant_figures": 1,
                "explanation": "The separation is |−3 m − 5 m| = 8 m.",
                "hint": "Separation is the absolute difference between the two coordinates.",
                "points": 2,
            },
            {
                "type": "written",
                "prompt": "Design a coordinate system for a school hallway. State the origin and positive direction, and explain why another student could reproduce it.",
                "correct": "A strong response names a fixed, identifiable origin and an unambiguous positive direction so another observer can use the same system.",
                "explanation": "Responses should make the reference point and direction reproducible, not merely convenient for one observer.",
                "hint": "Choose a permanent landmark and name exactly which way is positive.",
                "points": 3,
            },
            {
                "type": "written",
                "prompt": "Give an example of an object that is at rest in one frame but moving in another. Name both frames and explain the difference.",
                "correct": "For example, a seated passenger is at rest relative to a train but moving relative to the ground as the train travels.",
                "explanation": "Motion depends on the chosen frame of reference; both descriptions can be correct at the same time.",
                "hint": "Think about a person or object inside a moving vehicle.",
                "points": 3,
            },
        ],
    },
    {
        "slug": "distance-displacement-preview",
        "title": "Distance and Displacement",
        "lesson_slug": "distance-displacement",
        "instructions": "Prepare for the next lesson by comparing path length with change in position.",
        "reference_text": "Distance measures total path length. Displacement compares final and initial position and includes direction.",
        "due_days": 12,
        "estimated_minutes": 25,
        "assigned_by": "Platform",
        "status": "assigned",
        "questions": [
            {"type": "multiple_choice", "prompt": "A runner returns to the starting point. Which quantity must be zero?", "options": ["Distance", "Displacement", "Time"], "correct": "Displacement", "explanation": "Final and initial positions match, so displacement is zero.", "hint": "Compare the initial and final positions.", "points": 1},
        ],
    },
    {
        "slug": "speed-velocity-practice",
        "title": "Speed and Velocity Practice",
        "lesson_slug": "speed-velocity",
        "instructions": "Apply speed and velocity relationships and explain the role of direction.",
        "reference_text": "Average speed = total distance ÷ total time. Average velocity = displacement ÷ elapsed time.",
        "due_days": -2,
        "estimated_minutes": 30,
        "assigned_by": "Tutor",
        "status": "assigned",
        "attempt": {"status": "submitted", "score": 80, "max_score": 5, "feedback_status": "awaiting_review"},
        "questions": [
            {"type": "numerical", "prompt": "A cyclist travels 100 m in 20 s. Find the average speed.", "correct": "5", "unit": "m/s", "tolerance": 0.01, "explanation": "100 m ÷ 20 s = 5 m/s.", "hint": "Divide total distance by elapsed time.", "points": 2},
            {"type": "written", "prompt": "Explain why speed and velocity can have different average values on a return trip.", "correct": "Distance accumulates along the route, while displacement depends only on the start and finish and may be zero.", "explanation": "A return trip can have nonzero distance but zero displacement.", "hint": "Compare total path length with final minus initial position.", "points": 3},
        ],
    },
    {
        "slug": "motion-graphs-review",
        "title": "Motion Graphs Review",
        "lesson_slug": "distance-time-graphs",
        "instructions": "Review how graph shape and slope represent motion.",
        "reference_text": "On a distance–time graph, a steeper slope represents a greater speed; a horizontal segment represents rest.",
        "due_days": -10,
        "estimated_minutes": 40,
        "assigned_by": "Tutor",
        "status": "assigned",
        "attempt": {"status": "completed", "score": 92, "max_score": 5, "feedback_status": "feedback_ready", "feedback": "Strong graph interpretation. Recheck units whenever you calculate a slope."},
        "questions": [
            {"type": "multiple_choice", "prompt": "What does a horizontal segment on a distance–time graph show?", "options": ["Constant speed", "The object is at rest", "Increasing speed"], "correct": "The object is at rest", "explanation": "Distance is not changing while time passes.", "hint": "Ask whether the vertical value changes.", "points": 2},
            {"type": "written", "prompt": "Describe how you identify the faster object when comparing two distance–time lines.", "correct": "The faster object has the steeper line because its distance changes more during the same time interval.", "explanation": "Slope represents the rate of change of distance.", "hint": "Compare the slopes of the lines.", "points": 3},
        ],
    },
]


def seed_homework(db: Session, student: Student) -> None:
    now = datetime.now().replace(microsecond=0)
    for data in DEMO_HOMEWORK:
        assignment = db.scalar(select(HomeworkAssignment).where(HomeworkAssignment.slug == data["slug"]))
        if assignment:
            continue
        lesson = db.scalar(select(Lesson).where(Lesson.slug == data["lesson_slug"]))
        if not lesson:
            continue
        assignment = HomeworkAssignment(
            slug=data["slug"],
            title=data["title"],
            lesson_id=lesson.id,
            instructions=data["instructions"],
            reference_text=data["reference_text"],
            due_date=(now + timedelta(days=data["due_days"])).replace(hour=23, minute=59, second=0),
            estimated_minutes=data["estimated_minutes"],
            assigned_by=data["assigned_by"],
            status=data["status"],
        )
        db.add(assignment)
        db.flush()
        for index, item in enumerate(data["questions"], start=1):
            db.add(
                HomeworkQuestion(
                    homework_id=assignment.id,
                    order_index=index,
                    question_type=item["type"],
                    prompt=item["prompt"],
                    options_json=json.dumps(item.get("options")) if item.get("options") else None,
                    correct_answer=item.get("correct"),
                    explanation=item.get("explanation", ""),
                    expected_unit=item.get("unit"),
                    tolerance=item.get("tolerance"),
                    significant_figures=item.get("significant_figures"),
                    hint=item.get("hint", ""),
                    points=float(item.get("points", 1)),
                )
            )
        db.flush()
        attempt_data = data.get("attempt")
        if attempt_data:
            submitted = attempt_data["status"] in {"submitted", "completed", "needs_revision"}
            attempt = HomeworkAttempt(
                homework_id=assignment.id,
                student_id=student.id,
                status=attempt_data["status"],
                started_at=now - timedelta(days=4),
                submitted_at=now - timedelta(days=2) if submitted else None,
                score=attempt_data.get("score"),
                max_score=attempt_data.get("max_score"),
                feedback=attempt_data.get("feedback", ""),
                feedback_status=attempt_data.get("feedback_status", "not_submitted"),
            )
            db.add(attempt)
            db.flush()
            if submitted:
                for question in assignment.questions:
                    is_written = question.question_type == "written"
                    db.add(
                        HomeworkAnswer(
                            attempt=attempt,
                            question=question,
                            answer_text=(
                                "Distance follows the complete route, while displacement compares the final and initial positions."
                                if is_written else str(question.correct_answer or "")
                            ),
                            numerical_value=float(question.correct_answer) if question.question_type == "numerical" else None,
                            unit=question.expected_unit,
                            is_correct=None if is_written else True,
                            points_awarded=None if is_written else question.points,
                            feedback="Awaiting tutor review." if is_written else "Correct.",
                        )
                    )
    db.commit()


def effective_status(assignment: HomeworkAssignment, attempt: HomeworkAttempt | None, now: datetime | None = None) -> str:
    now = now or datetime.now()
    status = attempt.status if attempt else assignment.status
    if status in {"assigned", "in_progress"} and assignment.due_date < now:
        return "overdue"
    return status


def assignment_progress(assignment: HomeworkAssignment, attempt: HomeworkAttempt | None) -> int:
    if attempt and attempt.status in {"submitted", "completed"}:
        return 100
    total = len(assignment.questions)
    if not total or not attempt:
        return 0
    answered = sum(1 for answer in attempt.answers if answer.answer_text.strip() or answer.numerical_value is not None)
    return round(100 * answered / total)


def homework_view(assignment: HomeworkAssignment, attempt: HomeworkAttempt | None, now: datetime | None = None) -> dict:
    status = effective_status(assignment, attempt, now)
    action = {
        "assigned": "Start homework",
        "in_progress": "Continue",
        "overdue": "Continue",
        "submitted": "Review submission",
        "needs_revision": "View feedback",
        "completed": "View completed work",
    }[status]
    if status == "submitted" and attempt and attempt.feedback_status == "feedback_ready":
        action = "View feedback"
    href = f"/homework/{assignment.id}/results" if status in {"submitted", "completed"} else f"/homework/{assignment.id}"
    if status == "needs_revision":
        href = f"/homework/{assignment.id}/results"
    return {
        "assignment": assignment,
        "attempt": attempt,
        "status": status,
        "status_label": status.replace("_", " ").title(),
        "progress": assignment_progress(assignment, attempt),
        "action": action,
        "href": href,
        "feedback_status": (attempt.feedback_status if attempt else "not_submitted").replace("_", " ").title(),
        "course_title": COURSE["title"],
    }


def homework_summary(items: list[dict], now: datetime | None = None) -> dict[str, int | float | None]:
    now = now or datetime.now()
    active = [item for item in items if item["status"] in ACTIVE_STATUSES]
    due_this_week = sum(1 for item in active if now <= item["assignment"].due_date <= now + timedelta(days=7))
    awaiting = sum(1 for item in items if item["attempt"] and item["attempt"].feedback_status == "awaiting_review")
    scores = [item["attempt"].score for item in items if item["attempt"] and item["attempt"].score is not None]
    return {
        "active": len(active),
        "due_this_week": due_this_week,
        "awaiting_feedback": awaiting,
        "average_score": round(sum(scores) / len(scores)) if scores else None,
    }


def parse_options(question: HomeworkQuestion) -> list[str]:
    return json.loads(question.options_json) if question.options_json else []


def normalized_unit(value: str | None) -> str:
    return (value or "").strip().lower().replace(" ", "")


def significant_figures(value: str) -> int:
    cleaned = value.strip().lower()
    if "e" in cleaned:
        cleaned = cleaned.split("e", 1)[0]
    cleaned = cleaned.lstrip("+-").replace(".", "").lstrip("0")
    return len(cleaned.rstrip("0")) if "." not in value else len(cleaned)


def grade_answer(question: HomeworkQuestion, answer: HomeworkAnswer) -> None:
    if question.question_type == "written":
        answer.is_correct = None
        answer.points_awarded = None
        answer.feedback = "Awaiting teacher or tutor review."
        return
    if question.question_type == "multiple_choice":
        correct = answer.answer_text.strip() == (question.correct_answer or "").strip()
    elif question.question_type == "numerical":
        try:
            expected = float(question.correct_answer or "")
            entered = float(answer.answer_text)
            tolerance = question.tolerance if question.tolerance is not None else 0.0
            correct = math.isclose(entered, expected, abs_tol=tolerance, rel_tol=0.0)
            correct = correct and normalized_unit(answer.unit) == normalized_unit(question.expected_unit)
            if correct and question.significant_figures:
                correct = significant_figures(answer.answer_text) == question.significant_figures
            answer.numerical_value = entered
        except ValueError:
            correct = False
            answer.numerical_value = None
    else:
        correct = False
    answer.is_correct = correct
    answer.points_awarded = question.points if correct else 0.0
    answer.feedback = "Correct." if correct else "Review the explanation and try this idea again when revision is available."
