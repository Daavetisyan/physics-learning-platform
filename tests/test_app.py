import re
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.database import SessionLocal
from app.main import app, initialize_database
from app.models import Curriculum, Enrollment, Progress, StudentProfile, TutorStudentAssignment, User
from app.security import verify_password


def token(response) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    assert match, response.text[:500]
    return match.group(1)


def login(client: TestClient, email: str, password: str):
    page = client.get("/login")
    return client.post("/login", data={"email": email, "password": password, "next": "/dashboard", "csrf_token": token(page)}, follow_redirects=False)


def register_and_onboard(client: TestClient, grade: int = 8, level: str = "standard") -> tuple[str, int]:
    email = f"student-{uuid4().hex}@example.test"
    page = client.get("/register")
    response = client.post(
        "/register",
        data={"email": email, "password": "SecureVector1!", "password_confirm": "SecureVector1!", "csrf_token": token(page)},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/onboarding"
    onboarding = client.get("/onboarding")
    with SessionLocal() as db:
        curriculum_id = db.scalar(select(Curriculum.id).where(Curriculum.slug == "vector-academy-physics"))
    response = client.post(
        "/onboarding",
        data={
            "display_name": f"Grade {grade} Learner",
            "grade_level": grade,
            "curriculum_id": curriculum_id,
            "learning_level": level,
            "timezone": "America/Chicago",
            "preferred_unit_system": "metric",
            "guardian_name": "Casey Learner",
            "guardian_email": "guardian@example.test",
            "guardian_relationship": "Guardian",
            "receives_progress_emails": "true",
            "csrf_token": token(onboarding),
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        return email, user.id


def test_health_and_public_auth_pages():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/").status_code == 200
    assert client.get("/register").status_code == 200
    assert client.get("/login").status_code == 200


def test_protected_routes_redirect_unauthenticated_users():
    client = TestClient(app)
    for path in ("/dashboard", "/course/foundations-of-physics", "/lesson/position-reference-points", "/account", "/tutoring"):
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"].startswith("/login")


def test_registration_hashes_password_and_starts_onboarding():
    client = TestClient(app)
    email = f"register-{uuid4().hex}@example.test"
    page = client.get("/register")
    response = client.post(
        "/register",
        data={"email": email, "password": "SecureVector1!", "password_confirm": "SecureVector1!", "csrf_token": token(page)},
        follow_redirects=False,
    )
    assert response.status_code == 303
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        assert user.password_hash != "SecureVector1!"
        assert user.password_hash.startswith("scrypt$")
        assert verify_password("SecureVector1!", user.password_hash)
    assert client.get("/onboarding").status_code == 200


def test_login_rejects_wrong_password_and_accepts_correct_password():
    client = TestClient(app)
    wrong = login(client, "grade8@student.local", "not-the-password")
    assert wrong.status_code == 400
    assert "Incorrect email or password" in wrong.text
    correct = login(client, "grade8@student.local", "VectorDemo8!")
    assert correct.status_code == 303
    assert correct.headers["location"] == "/dashboard"
    cookie = correct.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=lax" in cookie


def test_logout_clears_session():
    client = TestClient(app)
    login(client, "grade8@student.local", "VectorDemo8!")
    account = client.get("/account")
    response = client.post("/logout", data={"csrf_token": token(account)}, follow_redirects=False)
    assert response.status_code == 303
    assert client.get("/dashboard", follow_redirects=False).status_code == 303


def test_onboarding_supports_grades_and_independent_learning_levels():
    combinations = ((7, "advanced"), (8, "foundation"), (9, "standard"))
    for grade, level in combinations:
        client = TestClient(app)
        email, user_id = register_and_onboard(client, grade, level)
        with SessionLocal() as db:
            profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user_id))
            enrollment = db.scalar(select(Enrollment).where(Enrollment.student_id == profile.id))
            assert profile.grade_level == grade
            assert profile.learning_level == level
            assert profile.curriculum.slug == "vector-academy-physics"
            assert profile.onboarding_completed
            assert enrollment.grade_level == grade
            assert enrollment.curriculum_id == profile.curriculum_id
        dashboard = client.get("/dashboard")
        assert dashboard.status_code == 200
        assert f"Grade {grade} Learner" in dashboard.text


def test_existing_course_lesson_and_ai_routes_work_for_enrolled_student():
    client = TestClient(app)
    login(client, "grade8@student.local", "VectorDemo8!")
    assert client.get("/course/foundations-of-physics").status_code == 200
    lesson = client.get("/lesson/position-reference-points")
    assert lesson.status_code == 200
    assert "Start and diagnostic" in lesson.text
    theory = client.get("/lesson/position-reference-points/theory-1")
    assert theory.status_code == 200
    assert "THEORY CHAPTER 1 OF" in theory.text
    reply = client.post("/api/ai-chat", json={"message": "What does negative mean?", "mode": "explain", "lesson_slug": "position-reference-points"})
    assert reply.status_code == 200
    assert "positive direction" in reply.json()["reply"].lower()


def test_student_progress_is_owned_by_current_student():
    first = TestClient(app)
    second = TestClient(app)
    login(first, "grade7@student.local", "VectorDemo7!")
    login(second, "grade9@student.local", "VectorDemo9!")
    response = first.post("/api/progress/position-reference-points", json={"status": "completed", "score": 91})
    assert response.status_code == 200
    with SessionLocal() as db:
        first_profile = db.scalar(select(StudentProfile).where(StudentProfile.email == "grade7@student.local"))
        second_profile = db.scalar(select(StudentProfile).where(StudentProfile.email == "grade9@student.local"))
        first_progress = db.scalar(select(Progress).where(Progress.student_id == first_profile.id))
        second_progress = db.scalar(select(Progress).where(Progress.student_id == second_profile.id))
        assert first_progress.score == 91
        assert second_progress is None or second_progress.score != 91


def test_tutor_sees_only_assigned_students():
    client = TestClient(app)
    response = login(client, "tutor@vector.local", "VectorTutor1!")
    assert response.headers["location"] == "/tutor/students"
    page = client.get("/tutor/students")
    assert page.status_code == 200
    assert "Maya Carter" in page.text
    with SessionLocal() as db:
        unrelated = db.scalar(select(StudentProfile).where(StudentProfile.email == "grade9@student.local"))
    assert client.get(f"/tutor/students/{unrelated.id}").status_code == 403


def test_role_based_admin_restrictions():
    for email, password in (("grade8@student.local", "VectorDemo8!"), ("tutor@vector.local", "VectorTutor1!")):
        client = TestClient(app)
        login(client, email, password)
        assert client.get("/admin").status_code == 403
    admin = TestClient(app)
    login(admin, "admin@vector.local", "VectorAdmin1!")
    page = admin.get("/admin")
    assert page.status_code == 200
    assert "Academic operations" in page.text


def test_navigation_changes_with_authentication():
    logged_out = TestClient(app).get("/")
    assert "Log in" in logged_out.text and "Create account" in logged_out.text
    client = TestClient(app)
    login(client, "grade8@student.local", "VectorDemo8!")
    page = client.get("/dashboard")
    assert "Homework" in page.text
    assert "Account" in page.text
    assert "Log out" in page.text
    assert "Creator view" not in page.text


def test_csrf_rejects_state_changing_form_without_token():
    client = TestClient(app)
    login(client, "grade8@student.local", "VectorDemo8!")
    assert client.post("/logout", data={"csrf_token": "wrong"}).status_code == 403


def test_seed_initialization_is_idempotent():
    initialize_database()
    with SessionLocal() as db:
        before = {
            "users": db.scalar(select(func.count(User.id))),
            "curricula": db.scalar(select(func.count(Curriculum.id))),
            "enrollments": db.scalar(select(func.count(Enrollment.id))),
            "assignments": db.scalar(select(func.count(TutorStudentAssignment.id))),
        }
    initialize_database()
    with SessionLocal() as db:
        after = {
            "users": db.scalar(select(func.count(User.id))),
            "curricula": db.scalar(select(func.count(Curriculum.id))),
            "enrollments": db.scalar(select(func.count(Enrollment.id))),
            "assignments": db.scalar(select(func.count(TutorStudentAssignment.id))),
        }
    assert before == after
