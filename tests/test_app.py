from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.main import app
from app.database import SessionLocal
from app.homework import effective_status
from app.models import HomeworkAnswer, HomeworkAssignment, HomeworkAttempt, HomeworkQuestion, Lesson, Student

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_landing_and_production_lesson():
    assert client.get("/").status_code == 200
    lesson = client.get("/lesson/position-reference-points")
    assert lesson.status_code == 200
    assert "Position and Reference Points" in lesson.text
    assert "Start and diagnostic" in lesson.text
    assert "STEP 1 OF" in lesson.text
    assert "Ask Galileo" in lesson.text

    theory = client.get("/lesson/position-reference-points/theory-1")
    assert theory.status_code == 200
    assert "THEORY CHAPTER 1 OF" in theory.text
    assert "Location words are incomplete" in theory.text

    assessment = client.get("/lesson/position-reference-points/assessment")
    assert assessment.status_code == 200
    assert "quiz-question-card" in assessment.text
    assert "Which information is required" in assessment.text


def test_unbuilt_lesson_uses_step_by_step_state():
    lesson = client.get("/lesson/distance-displacement")
    assert lesson.status_code == 200
    assert "BUILDING STEP BY STEP" in lesson.text


def test_ai_scientist_position_context():
    response = client.post(
        "/api/ai-chat",
        json={
            "message": "What does a negative position mean?",
            "mode": "explain",
            "lesson_slug": "position-reference-points",
        },
    )
    assert response.status_code == 200
    assert "positive direction" in response.json()["reply"].lower()


def test_progress_update():
    response = client.post(
        "/api/progress/position-reference-points",
        json={"status": "completed", "score": 100},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_production_lesson_meets_depth_baseline():
    from app.lesson_content import POSITION_REFERENCE_POINTS

    content = POSITION_REFERENCE_POINTS
    theory_words = sum(
        len(paragraph.split())
        for chapter in content["theory_chapters"]
        for paragraph in chapter["paragraphs"]
    )
    assert len(content["theory_chapters"]) >= 8
    assert theory_words >= 1400
    assert len(content["worked_examples"]) >= 5
    assert sum(len(group["questions"]) for group in content["practice_groups"]) >= 12
    assert len(content["quiz"]) >= 8


@pytest.fixture
def homework_assignment():
    with SessionLocal() as db:
        lesson = db.scalar(select(Lesson).where(Lesson.slug == "position-reference-points"))
        assignment = HomeworkAssignment(
            slug="automated-homework-test",
            title="Automated Homework Test",
            lesson_id=lesson.id,
            instructions="Answer every test question.",
            reference_text="Position is measured from an origin.",
            due_date=datetime.now() + timedelta(days=2),
            estimated_minutes=10,
            assigned_by="Platform",
            status="assigned",
        )
        db.add(assignment)
        db.flush()
        questions = [
            HomeworkQuestion(homework_id=assignment.id, order_index=1, question_type="multiple_choice", prompt="Choose the origin.", options_json='["Door", "Speed"]', correct_answer="Door", explanation="A door can be a fixed origin.", hint="Choose a location.", points=1),
            HomeworkQuestion(homework_id=assignment.id, order_index=2, question_type="numerical", prompt="Find 6 m − 1 m.", correct_answer="5", expected_unit="m", tolerance=0.01, explanation="Subtract coordinates.", hint="Subtract.", points=2),
            HomeworkQuestion(homework_id=assignment.id, order_index=3, question_type="written", prompt="Explain a reference frame.", correct_answer="A coordinate system tied to an observer.", explanation="Name the observer or coordinate system.", hint="Name an observer.", points=3),
        ]
        db.add_all(questions)
        db.commit()
        assignment_id = assignment.id
        question_ids = [question.id for question in questions]
    yield assignment_id, question_ids
    with SessionLocal() as db:
        attempt_ids = list(db.scalars(select(HomeworkAttempt.id).where(HomeworkAttempt.homework_id == assignment_id)))
        if attempt_ids:
            db.execute(delete(HomeworkAnswer).where(HomeworkAnswer.attempt_id.in_(attempt_ids)))
        db.execute(delete(HomeworkAttempt).where(HomeworkAttempt.homework_id == assignment_id))
        db.execute(delete(HomeworkQuestion).where(HomeworkQuestion.homework_id == assignment_id))
        db.execute(delete(HomeworkAssignment).where(HomeworkAssignment.id == assignment_id))
        db.commit()


def test_homework_pages_navigation_and_connections():
    homework = client.get("/homework")
    assert homework.status_code == 200
    assert "Assigned" in homework.text
    assert "Upcoming" in homework.text
    assert "Speed and Velocity Practice" in homework.text
    assert "Motion Graphs Review" in homework.text
    assert 'href="/homework"' in homework.text
    assert 'class="active" aria-current="page">Homework' in homework.text

    lesson = client.get("/lesson/position-reference-points/homework")
    assert lesson.status_code == 200
    assert "HOMEWORK ASSIGNED" in lesson.text
    assert "Open homework" in lesson.text
    assert "homeworkAnswer" not in lesson.text

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert "UPCOMING HOMEWORK" in dashboard.text
    assert "due this week" in dashboard.text

    assert client.get("/lesson/position-reference-points/overview").status_code == 200
    assert client.get("/tutoring").status_code == 200


def test_homework_save_submit_grade_and_review(homework_assignment):
    assignment_id, question_ids = homework_assignment
    workspace = client.get(f"/homework/{assignment_id}")
    assert workspace.status_code == 200
    assert "Choose the origin." in workspace.text
    assert "correct_answer" not in workspace.text

    save = client.post(
        f"/homework/{assignment_id}/save",
        data={f"answer_{question_ids[0]}": "Door"},
        follow_redirects=False,
    )
    assert save.status_code == 303
    with SessionLocal() as db:
        student = db.scalar(select(Student).where(Student.email == "demo@student.example"))
        attempt = db.scalar(select(HomeworkAttempt).where(HomeworkAttempt.homework_id == assignment_id, HomeworkAttempt.student_id == student.id))
        saved = db.scalar(select(HomeworkAnswer).where(HomeworkAnswer.attempt_id == attempt.id, HomeworkAnswer.question_id == question_ids[0]))
        assert attempt.status == "in_progress"
        assert saved.answer_text == "Door"

    submit = client.post(
        f"/homework/{assignment_id}/submit",
        data={
            f"answer_{question_ids[0]}": "Door",
            f"answer_{question_ids[1]}": "5",
            f"unit_{question_ids[1]}": "m",
            f"answer_{question_ids[2]}": "A reference frame is a coordinate system tied to an observer.",
        },
        follow_redirects=False,
    )
    assert submit.status_code == 303
    assert submit.headers["location"].endswith("/results?submitted=1")
    with SessionLocal() as db:
        attempt = db.scalar(select(HomeworkAttempt).where(HomeworkAttempt.homework_id == assignment_id))
        answers = db.scalars(select(HomeworkAnswer).where(HomeworkAnswer.attempt_id == attempt.id)).all()
        assert attempt.status == "submitted"
        assert attempt.score == 100
        assert attempt.feedback_status == "awaiting_review"
        assert next(answer for answer in answers if answer.question_id == question_ids[2]).is_correct is None

    results = client.get(f"/homework/{assignment_id}/results")
    assert results.status_code == 200
    assert "AWAITING REVIEW" in results.text
    submitted_dashboard = client.get("/homework")
    submitted_section = submitted_dashboard.text.split('id="submitted"', 1)[1].split('id="completed"', 1)[0]
    assert "Automated Homework Test" in submitted_section

    duplicate = client.post(f"/homework/{assignment_id}/submit", data={}, follow_redirects=False)
    assert duplicate.status_code == 303
    with SessionLocal() as db:
        assert len(db.scalars(select(HomeworkAttempt).where(HomeworkAttempt.homework_id == assignment_id)).all()) == 1


def test_completed_and_overdue_homework_status():
    completed = client.get("/homework")
    completed_section = completed.text.split('id="completed"', 1)[1]
    assert "Motion Graphs Review" in completed_section
    with SessionLocal() as db:
        assignment = db.scalar(select(HomeworkAssignment).where(HomeworkAssignment.slug == "distance-displacement-preview"))
        original_due = assignment.due_date
        assignment.due_date = datetime.now() - timedelta(minutes=1)
        assert effective_status(assignment, None) == "overdue"
        assignment.due_date = original_due
