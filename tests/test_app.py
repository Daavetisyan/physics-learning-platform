from fastapi.testclient import TestClient

from app.main import app

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
