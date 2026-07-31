from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from starlette.middleware.sessions import SessionMiddleware

from .content import COURSE, LESSONS
from .database import Base, SessionLocal, engine
from .lesson_content import LESSON_CONTENTS
from .migrations import migrate_legacy_schema
from .models import (
    AIConversation,
    Course,
    Curriculum,
    Enrollment,
    GuardianContact,
    HomeworkSubmission,
    Lesson,
    LessonVariant,
    Progress,
    StudentProfile,
    TutorSession,
    TutorStudentAssignment,
    User,
)
from .security import hash_password, new_csrf_token, valid_csrf, verify_password
from .services.ai_scientist import answer_as_scientist

BASE_DIR = Path(__file__).resolve().parent
APP_ENV = os.getenv("APP_ENV", "development").lower()
SESSION_SECRET = os.getenv("SESSION_SECRET")
if not SESSION_SECRET:
    if APP_ENV == "production":
        raise RuntimeError("SESSION_SECRET is required in production.")
    SESSION_SECRET = "development-only-change-me-vector-academy"

app = FastAPI(title="Vector Academy", version="0.2.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = db.get(User, int(user_id))
    if not user or not user.is_active:
        request.session.clear()
        return None
    return user


def csrf(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not token:
        token = new_csrf_token()
        request.session["csrf_token"] = token
    return token


def check_csrf(request: Request, submitted: str) -> None:
    if not valid_csrf(request.session.get("csrf_token"), submitted):
        raise HTTPException(status_code=403, detail="Invalid or expired form token.")


def login_redirect(request: Request) -> RedirectResponse:
    return RedirectResponse(url=f"/login?next={quote(request.url.path)}", status_code=303)


def require_user(request: Request, db: Session, *roles: str) -> User:
    user = current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    if roles and user.role not in roles:
        raise HTTPException(status_code=403, detail="You do not have permission to view this page.")
    return user


@app.exception_handler(401)
async def authentication_error(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api/"):
        return JSONResponse({"detail": exc.detail}, status_code=401)
    return login_redirect(request)


@app.middleware("http")
async def account_context(request: Request, call_next):
    csrf(request)
    with SessionLocal() as db:
        request.state.user = current_user(request, db)
    response = await call_next(request)
    response.headers.setdefault("Cache-Control", "no-store" if request.url.path in {"/login", "/register", "/account", "/onboarding"} else "private")
    return response


app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="vector_session",
    max_age=60 * 60 * 24 * 14,
    same_site="lax",
    https_only=APP_ENV == "production",
)


def build_lesson_steps(content: dict) -> list[dict[str, str]]:
    detailed_foundation = bool(content.get("prerequisite_review"))
    steps = [
        {"key": "overview", "label": "Lesson introduction" if detailed_foundation else "Start and diagnostic", "group": "Start", "description": "Understand the lesson goal, course relationship, and learning objectives."},
    ]
    if detailed_foundation:
        steps.extend([
            {"key": "prerequisite-review", "label": "Prerequisite review", "group": "Foundation", "description": "Reconnect position, coordinates, origins, and direction to the new topic."},
            {"key": "diagnostic", "label": "Diagnostic questions", "group": "Foundation", "description": "Check your current thinking without affecting lesson access."},
        ])
    steps.append({"key": "vocabulary", "label": "Key vocabulary" if detailed_foundation else "Physics vocabulary", "group": "Foundation", "description": "Learn the exact language used throughout the lesson."})
    for chapter in content.get("theory_chapters", []):
        steps.append({"key": f"theory-{chapter['number']}", "label": chapter["heading"], "group": "Theory", "description": chapter["lead"]})
    steps.extend(
        [
            {"key": "video", "label": "Video explanation", "group": "Explore", "description": "Reinforce the theory with a filmed physical demonstration."},
            {
                "key": "simulation",
                "label": "Interactive laboratory",
                "group": "Explore",
                "description": (
                    content["simulation"]["instruction"]
                    if content.get("simulation", {}).get("type") in {"distance_displacement_journey", "speed_lab"}
                    else "Change the reference frame and observe what changes and what stays invariant."
                ),
            },
            {"key": "examples", "label": "Worked examples", "group": "Apply", "description": "Follow complete reasoning from the physical situation to the answer."},
            {"key": "misconceptions", "label": "Common misconceptions", "group": "Apply", "description": "Replace common but incorrect ideas with precise physics."},
            *([{"key": "guided-practice", "label": "Guided practice", "group": "Practice", "description": "Use progressive hints to organize complete solutions."}] if content.get("guided_practice") else []),
            {"key": "practice", "label": "Independent practice", "group": "Practice", "description": "Solve questions at foundation, standard, and challenge levels."},
            {"key": "assistant", "label": f"Ask {content['scientist']['name']}", "group": "Support", "description": "Ask for another explanation, guided help, or feedback on your work."},
            {"key": "assessment", "label": "Mastery assessment", "group": "Check", "description": "Demonstrate complete understanding and identify what to revisit."},
            {"key": "homework", "label": "Homework investigation", "group": "Extend", "description": "Apply the lesson to a real space and submit your reasoning."},
            {"key": "summary", "label": "Summary and reflection", "group": "Finish", "description": "Consolidate the essential ideas and finish the lesson."},
        ]
    )
    return steps


CURRICULA = (
    {
        "name": "US Physical Science — Grades 7–9",
        "slug": "us-physical-science-7-9",
        "description": "A United States physical-science pathway for grades 7–9. It is not a claim of standards certification or complete compliance.",
    },
    {
        "name": "Vector Academy Physics Pathway",
        "slug": "vector-academy-physics",
        "description": "Vector Academy’s concept-first teaching sequence: theory, investigation, practice, feedback, and mastery.",
    },
)
DEMO_USERS = (
    ("grade7@student.local", "VectorDemo7!", "student", "Maya Carter", 7, "foundation"),
    ("grade8@student.local", "VectorDemo8!", "student", "Alex Morgan", 8, "standard"),
    ("grade9@student.local", "VectorDemo9!", "student", "Jordan Lee", 9, "advanced"),
    ("tutor@vector.local", "VectorTutor1!", "tutor", "", 0, ""),
    ("admin@vector.local", "VectorAdmin1!", "admin", "", 0, ""),
)


def seed_database(db: Session) -> None:
    curricula: dict[str, Curriculum] = {}
    for item in CURRICULA:
        record = db.scalar(select(Curriculum).where(Curriculum.slug == item["slug"]))
        if not record:
            record = Curriculum(**item, country="United States", grade_min=7, grade_max=9, is_active=True)
            db.add(record)
            db.flush()
        curricula[record.slug] = record

    course = db.scalar(select(Course).where(Course.slug == COURSE["slug"]))
    if not course:
        course = Course(title=COURSE["title"], slug=COURSE["slug"], description=COURSE.get("description", ""), is_active=True)
        db.add(course)
        db.flush()

    # Preserve the existing Lesson 3 record while separating Speed from the later Velocity lesson.
    legacy_speed = db.scalar(select(Lesson).where(Lesson.slug == "speed-velocity"))
    current_speed = db.scalar(select(Lesson).where(Lesson.slug == "speed"))
    if legacy_speed and not current_speed:
        legacy_speed.slug = "speed"
        legacy_speed.title = "Speed"
        db.flush()
    elif legacy_speed and current_speed:
        legacy_speed.publication_status = "archived"
    retired_investigation = db.scalar(select(Lesson).where(Lesson.slug == "motion-investigation"))
    if retired_investigation:
        retired_investigation.publication_status = "archived"

    lessons: list[Lesson] = []
    for index, item in enumerate(LESSONS, 1):
        lesson = db.scalar(select(Lesson).where(Lesson.slug == item["slug"]))
        if not lesson:
            lesson = Lesson(slug=item["slug"], title=item["title"], unit=item["unit"], order_index=index, summary=item["summary"], duration_minutes=item["duration"])
            db.add(lesson)
        lesson.title = item["title"]
        lesson.concept_key = item["slug"].replace("-", "_")
        lesson.course_id = course.id
        lesson.order_index = index
        lesson.publication_status = "published"
        lessons.append(lesson)
    db.flush()

    for lesson in lessons:
        for curriculum in curricula.values():
            for level in ("foundation", "standard", "advanced"):
                variant = db.scalar(
                    select(LessonVariant).where(
                        LessonVariant.lesson_id == lesson.id,
                        LessonVariant.curriculum_id == curriculum.id,
                        LessonVariant.learning_level == level,
                    )
                )
                if not variant:
                    db.add(LessonVariant(lesson_id=lesson.id, curriculum_id=curriculum.id, grade_min=7, grade_max=9, learning_level=level, content_reference=lesson.slug, publication_status="published"))
    db.flush()

    if APP_ENV != "production":
        for email, password, role, display_name, grade, level in DEMO_USERS:
            user = db.scalar(select(User).where(User.email == email))
            if not user:
                user = User(email=email, password_hash=hash_password(password), role=role, is_active=True, email_verified=True)
                db.add(user)
                db.flush()
            if role == "student":
                profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
                if not profile:
                    profile = StudentProfile(
                        user_id=user.id, name=display_name, display_name=display_name, email=email, grade=grade, grade_level=grade,
                        curriculum_id=curricula["vector-academy-physics"].id, learning_level=level, timezone="America/New_York",
                        preferred_unit_system="metric", onboarding_completed=True,
                    )
                    db.add(profile)
                    db.flush()
                enrollment = db.scalar(select(Enrollment).where(Enrollment.student_id == profile.id, Enrollment.course_id == course.id))
                if not enrollment:
                    db.add(Enrollment(student_id=profile.id, course_id=course.id, curriculum_id=profile.curriculum_id, grade_level=grade, status="active"))

        tutor = db.scalar(select(User).where(User.email == "tutor@vector.local"))
        students = db.scalars(select(StudentProfile).where(StudentProfile.user_id.is_not(None)).order_by(StudentProfile.grade_level)).all()
        for profile in students[:2]:
            assignment = db.scalar(select(TutorStudentAssignment).where(TutorStudentAssignment.tutor_id == tutor.id, TutorStudentAssignment.student_id == profile.id))
            if not assignment:
                db.add(TutorStudentAssignment(tutor_id=tutor.id, student_id=profile.id, is_active=True))

    # Preserve and connect a pre-account demo row if one exists.
    legacy = db.scalar(select(StudentProfile).where(StudentProfile.email == "demo@student.example"))
    if legacy and not legacy.user_id:
        user = db.scalar(select(User).where(User.email == legacy.email))
        if not user:
            user = User(email=legacy.email, password_hash=hash_password("LegacyDemo1!"), role="student", is_active=True, email_verified=False)
            db.add(user)
            db.flush()
        legacy.user_id = user.id
        legacy.display_name = legacy.display_name or legacy.name
        legacy.grade_level = legacy.grade_level or legacy.grade
        legacy.curriculum_id = legacy.curriculum_id or curricula["vector-academy-physics"].id
        legacy.onboarding_completed = True
    db.commit()


def initialize_database() -> None:
    migrate_legacy_schema(engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)


@app.on_event("startup")
def startup() -> None:
    initialize_database()


initialize_database()


def profile_for(user: User, db: Session) -> StudentProfile:
    profile = db.scalar(
        select(StudentProfile)
        .where(StudentProfile.user_id == user.id)
        .options(selectinload(StudentProfile.curriculum), selectinload(StudentProfile.enrollments))
    )
    if not profile:
        raise HTTPException(status_code=409, detail="Student onboarding is incomplete.")
    return profile


def active_enrollment(profile: StudentProfile, db: Session) -> Enrollment | None:
    return db.scalar(
        select(Enrollment)
        .where(Enrollment.student_id == profile.id, Enrollment.status == "active")
        .options(selectinload(Enrollment.course), selectinload(Enrollment.curriculum))
        .order_by(Enrollment.start_date)
    )


def accessible_lessons(user: User, db: Session) -> list[Lesson]:
    if user.role in {"admin", "tutor"}:
        return list(db.scalars(select(Lesson).where(Lesson.publication_status == "published").order_by(Lesson.order_index)).all())
    profile = profile_for(user, db)
    enrollment = active_enrollment(profile, db)
    if not enrollment:
        return []
    return list(
        db.scalars(
            select(Lesson)
            .join(LessonVariant)
            .where(
                Lesson.course_id == enrollment.course_id,
                Lesson.publication_status == "published",
                LessonVariant.curriculum_id == enrollment.curriculum_id,
                LessonVariant.grade_min <= profile.grade_level,
                LessonVariant.grade_max >= profile.grade_level,
                LessonVariant.learning_level == profile.learning_level,
                LessonVariant.publication_status == "published",
            )
            .distinct()
            .order_by(Lesson.order_index)
        ).all()
    )


def lesson_for_user(slug: str, user: User, db: Session) -> Lesson:
    lesson = db.scalar(select(Lesson).where(Lesson.slug == slug))
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    if lesson.id not in {item.id for item in accessible_lessons(user, db)}:
        raise HTTPException(status_code=403, detail="This lesson is not included in your enrollment.")
    return lesson


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request, "course": COURSE})


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@app.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    check_csrf(request, csrf_token)
    normalized = email.strip().lower()
    error = None
    if "@" not in normalized:
        error = "Enter a valid email address."
    elif password != password_confirm:
        error = "Passwords do not match."
    elif len(password) < 10:
        error = "Use at least 10 characters."
    elif db.scalar(select(User).where(User.email == normalized)):
        error = "An account with this email already exists."
    if error:
        return templates.TemplateResponse("register.html", {"request": request, "error": error, "email": normalized}, status_code=400)
    user = User(email=normalized, password_hash=hash_password(password), role="student", is_active=True, email_verified=False)
    db.add(user)
    db.commit()
    db.refresh(user)
    request.session.clear()
    request.session.update({"user_id": user.id, "csrf_token": new_csrf_token()})
    return RedirectResponse("/onboarding", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, next: str = "/dashboard"):
    return templates.TemplateResponse("login.html", {"request": request, "error": None, "next": next if next.startswith("/") else "/dashboard"})


@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/dashboard"),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    check_csrf(request, csrf_token)
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect email or password.", "next": next}, status_code=400)
    user.last_login_at = datetime.utcnow()
    db.commit()
    request.session.clear()
    request.session.update({"user_id": user.id, "csrf_token": new_csrf_token()})
    if user.role == "student":
        profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
        destination = "/onboarding" if not profile or not profile.onboarding_completed else "/dashboard"
    elif user.role == "tutor":
        destination = "/tutor/students"
    else:
        destination = "/admin"
    if next.startswith("/") and next not in {"/dashboard", "/"}:
        destination = next
    return RedirectResponse(destination, status_code=303)


@app.post("/logout")
def logout(request: Request, csrf_token: str = Form(...)):
    check_csrf(request, csrf_token)
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@app.get("/onboarding", response_class=HTMLResponse)
def onboarding_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db, "student")
    curricula = db.scalars(select(Curriculum).where(Curriculum.is_active.is_(True)).order_by(Curriculum.id)).all()
    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
    return templates.TemplateResponse("onboarding.html", {"request": request, "curricula": curricula, "profile": profile, "error": None})


@app.post("/onboarding")
def onboarding(
    request: Request,
    display_name: str = Form(...),
    grade_level: int = Form(...),
    curriculum_id: int = Form(...),
    learning_level: str = Form(...),
    timezone: str = Form(...),
    preferred_unit_system: str = Form(...),
    guardian_name: str = Form(...),
    guardian_email: str = Form(...),
    guardian_relationship: str = Form(...),
    receives_progress_emails: bool = Form(False),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    check_csrf(request, csrf_token)
    user = require_user(request, db, "student")
    curriculum = db.get(Curriculum, curriculum_id)
    if grade_level not in {7, 8, 9} or learning_level not in {"foundation", "standard", "advanced"}:
        raise HTTPException(status_code=400, detail="Unsupported grade or learning level.")
    if not curriculum or not curriculum.is_active or not curriculum.grade_min <= grade_level <= curriculum.grade_max:
        raise HTTPException(status_code=400, detail="Curriculum is unavailable for this grade.")
    if preferred_unit_system not in {"metric", "us_customary"}:
        raise HTTPException(status_code=400, detail="Unsupported unit system.")
    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == user.id))
    if not profile:
        profile = StudentProfile(user_id=user.id, email=user.email)
        db.add(profile)
        db.flush()
    profile.display_name = display_name.strip()
    profile.name = profile.display_name
    profile.grade_level = grade_level
    profile.grade = grade_level
    profile.curriculum_id = curriculum.id
    profile.learning_level = learning_level
    profile.timezone = timezone.strip() or "America/New_York"
    profile.preferred_unit_system = preferred_unit_system
    profile.onboarding_completed = True
    guardian = db.scalar(select(GuardianContact).where(GuardianContact.student_id == profile.id))
    if not guardian:
        guardian = GuardianContact(student_id=profile.id, full_name="", email="", relationship_type="")
        db.add(guardian)
    guardian.full_name = guardian_name.strip()
    guardian.email = guardian_email.strip().lower()
    guardian.relationship_type = guardian_relationship.strip()
    guardian.receives_progress_emails = receives_progress_emails
    guardian.consent_recorded_at = datetime.utcnow()
    course = db.scalar(select(Course).where(Course.slug == COURSE["slug"]))
    enrollment = db.scalar(select(Enrollment).where(Enrollment.student_id == profile.id, Enrollment.course_id == course.id))
    if not enrollment:
        enrollment = Enrollment(student_id=profile.id, course_id=course.id, curriculum_id=curriculum.id, grade_level=grade_level)
        db.add(enrollment)
    else:
        enrollment.curriculum_id = curriculum.id
        enrollment.grade_level = grade_level
        enrollment.status = "active"
    db.commit()
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/account", response_class=HTMLResponse)
def account_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    profile = profile_for(user, db) if user.role == "student" else None
    return templates.TemplateResponse("account.html", {"request": request, "account_user": user, "profile": profile, "saved": request.query_params.get("saved")})


@app.post("/account")
def update_account(
    request: Request,
    display_name: str = Form(...),
    timezone: str = Form(...),
    preferred_unit_system: str = Form(...),
    learning_level: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    check_csrf(request, csrf_token)
    user = require_user(request, db, "student")
    profile = profile_for(user, db)
    if learning_level not in {"foundation", "standard", "advanced"} or preferred_unit_system not in {"metric", "us_customary"}:
        raise HTTPException(status_code=400, detail="Invalid profile choice.")
    profile.display_name = display_name.strip()
    profile.name = profile.display_name
    profile.timezone = timezone.strip()
    profile.preferred_unit_system = preferred_unit_system
    profile.learning_level = learning_level
    db.commit()
    return RedirectResponse("/account?saved=1", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db, "student")
    profile = profile_for(user, db)
    if not profile.onboarding_completed:
        return RedirectResponse("/onboarding", status_code=303)
    enrollment = active_enrollment(profile, db)
    lessons = accessible_lessons(user, db)
    progress_rows = db.scalars(select(Progress).where(Progress.student_id == profile.id)).all()
    progress_map = {row.lesson_id: row for row in progress_rows}
    completed = sum(row.status == "completed" for row in progress_rows)
    percent = round(100 * completed / len(lessons)) if lessons else 0
    sessions = db.scalars(select(TutorSession).where(TutorSession.student_id == profile.id).order_by(TutorSession.starts_at)).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "student": profile, "enrollment": enrollment, "course": COURSE, "lessons": lessons,
        "progress_map": progress_map, "progress_percent": percent, "sessions": sessions,
        "production_slugs": set(LESSON_CONTENTS), "homework_available": False,
    })


@app.get("/course/{course_slug}", response_class=HTMLResponse)
def course_page(course_slug: str, request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db, "student", "tutor", "admin")
    if course_slug != COURSE["slug"]:
        raise HTTPException(status_code=404, detail="Course not found")
    lessons = accessible_lessons(user, db)
    progress_map = {}
    if user.role == "student":
        profile = profile_for(user, db)
        progress_map = {row.lesson_id: row for row in db.scalars(select(Progress).where(Progress.student_id == profile.id)).all()}
    return templates.TemplateResponse("course.html", {"request": request, "course": COURSE, "lessons": lessons, "progress_map": progress_map, "production_slugs": set(LESSON_CONTENTS)})


@app.get("/lesson/{lesson_slug}", response_class=HTMLResponse)
def lesson_page(lesson_slug: str, request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db, "student", "tutor", "admin")
    lesson = lesson_for_user(lesson_slug, user, db)
    if LESSON_CONTENTS.get(lesson_slug):
        return RedirectResponse(f"/lesson/{lesson_slug}/overview", status_code=302)
    progress = None
    if user.role == "student":
        profile = profile_for(user, db)
        progress = db.scalar(select(Progress).where(Progress.student_id == profile.id, Progress.lesson_id == lesson.id))
    return templates.TemplateResponse("lesson.html", {"request": request, "lesson": lesson, "course": COURSE, "content": None, "progress": progress})


@app.get("/lesson/{lesson_slug}/{section_key}", response_class=HTMLResponse)
def lesson_section_page(lesson_slug: str, section_key: str, request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db, "student", "tutor", "admin")
    lesson = lesson_for_user(lesson_slug, user, db)
    content = LESSON_CONTENTS.get(lesson_slug)
    if not content:
        raise HTTPException(status_code=404, detail="This lesson is still being built")
    steps = build_lesson_steps(content)
    keys = [step["key"] for step in steps]
    if section_key not in keys:
        raise HTTPException(status_code=404, detail="Lesson section not found")
    index = keys.index(section_key)
    chapter = None
    if section_key.startswith("theory-"):
        number = int(section_key.split("-", 1)[1])
        chapter = next((item for item in content["theory_chapters"] if item["number"] == number), None)
    progress = None
    student_profile = None
    if user.role == "student":
        student_profile = profile_for(user, db)
        progress = db.scalar(select(Progress).where(Progress.student_id == student_profile.id, Progress.lesson_id == lesson.id))
    return templates.TemplateResponse("lesson_section.html", {
        "request": request, "lesson": lesson, "course": COURSE, "content": content, "progress": progress, "steps": steps,
        "current_step": steps[index], "previous_step": steps[index - 1] if index else None,
        "next_step": steps[index + 1] if index + 1 < len(steps) else None, "step_index": index + 1,
        "step_percent": round(100 * (index + 1) / len(steps)), "chapter": chapter, "student_profile": student_profile,
    })


@app.post("/api/progress/{lesson_slug}")
def update_progress(lesson_slug: str, request: Request, request_data: dict, db: Session = Depends(get_db)):
    user = require_user(request, db, "student")
    profile = profile_for(user, db)
    lesson = lesson_for_user(lesson_slug, user, db)
    progress = db.scalar(select(Progress).where(Progress.student_id == profile.id, Progress.lesson_id == lesson.id))
    if not progress:
        progress = Progress(student_id=profile.id, lesson_id=lesson.id)
        db.add(progress)
    progress.status = str(request_data.get("status", "in_progress"))
    if request_data.get("score") is not None:
        progress.score = float(request_data["score"])
    db.commit()
    return {"ok": True, "status": progress.status, "score": progress.score}


@app.post("/api/homework/{lesson_slug}")
def submit_homework(lesson_slug: str, request: Request, request_data: dict, db: Session = Depends(get_db)):
    user = require_user(request, db, "student")
    profile = profile_for(user, db)
    lesson = lesson_for_user(lesson_slug, user, db)
    answer = str(request_data.get("answer", "")).strip()
    if len(answer) < 10:
        return JSONResponse({"ok": False, "message": "Please show more reasoning before submitting."}, status_code=400)
    db.add(HomeworkSubmission(student_id=profile.id, lesson_id=lesson.id, answer=answer))
    db.commit()
    return {"ok": True, "message": "Homework submitted for review."}


@app.post("/api/ai-chat")
def ai_chat(request: Request, request_data: dict, db: Session = Depends(get_db)):
    user = require_user(request, db, "student")
    profile = profile_for(user, db)
    message = str(request_data.get("message", ""))
    mode = str(request_data.get("mode", "explain"))
    slug = str(request_data.get("lesson_slug", "position-reference-points"))
    lesson = lesson_for_user(slug, user, db)
    reply = answer_as_scientist(message, mode, slug)
    db.add(AIConversation(student_id=profile.id, lesson_id=lesson.id, mode=mode, user_message=message, assistant_message=reply))
    db.commit()
    return {"reply": reply}


@app.get("/homework", response_class=HTMLResponse)
def homework_unavailable(request: Request, db: Session = Depends(get_db)):
    require_user(request, db, "student")
    return templates.TemplateResponse("unavailable.html", {"request": request, "title": "Homework", "message": "The dedicated homework workspace is being prepared. Lesson assignments remain available in the course."}, status_code=503)


@app.get("/tutoring", response_class=HTMLResponse)
def tutoring_page(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db, "student")
    profile = profile_for(user, db)
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    slots = [(now + timedelta(days=day)).replace(hour=hour) for day in range(1, 8) for hour in (16, 18)]
    sessions = db.scalars(select(TutorSession).where(TutorSession.student_id == profile.id).order_by(TutorSession.starts_at)).all()
    return templates.TemplateResponse("tutoring.html", {"request": request, "student": profile, "slots": slots, "sessions": sessions})


@app.post("/tutoring/book")
def book_tutor(request: Request, topic: str = Form(...), starts_at: str = Form(...), csrf_token: str = Form(...), db: Session = Depends(get_db)):
    check_csrf(request, csrf_token)
    user = require_user(request, db, "student")
    profile = profile_for(user, db)
    try:
        start = datetime.fromisoformat(starts_at)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date") from exc
    assignment = db.scalar(select(TutorStudentAssignment).where(TutorStudentAssignment.student_id == profile.id, TutorStudentAssignment.is_active.is_(True)))
    db.add(TutorSession(student_id=profile.id, tutor_id=assignment.tutor_id if assignment else None, topic=topic.strip() or "Physics support", starts_at=start, price_usd=35, payment_status="demo_paid", meeting_url=f"https://meet.google.com/{uuid4().hex[:10]}"))
    db.commit()
    return RedirectResponse("/tutoring?booked=1", status_code=303)


@app.get("/tutor/students", response_class=HTMLResponse)
def tutor_students(request: Request, db: Session = Depends(get_db)):
    tutor = require_user(request, db, "tutor")
    assignments = db.scalars(
        select(TutorStudentAssignment)
        .where(TutorStudentAssignment.tutor_id == tutor.id, TutorStudentAssignment.is_active.is_(True))
        .options(selectinload(TutorStudentAssignment.student).selectinload(StudentProfile.enrollments))
    ).all()
    return templates.TemplateResponse("tutor_students.html", {"request": request, "assignments": assignments, "selected": None})


@app.get("/tutor/students/{student_id}", response_class=HTMLResponse)
def tutor_student_detail(student_id: int, request: Request, db: Session = Depends(get_db)):
    tutor = require_user(request, db, "tutor")
    assignment = db.scalar(select(TutorStudentAssignment).where(TutorStudentAssignment.tutor_id == tutor.id, TutorStudentAssignment.student_id == student_id, TutorStudentAssignment.is_active.is_(True)))
    if not assignment:
        raise HTTPException(status_code=403, detail="This student is not assigned to you.")
    student = db.get(StudentProfile, student_id)
    progress = db.scalars(select(Progress).where(Progress.student_id == student.id).options(selectinload(Progress.lesson))).all()
    sessions = db.scalars(select(TutorSession).where(TutorSession.student_id == student.id, TutorSession.tutor_id == tutor.id)).all()
    return templates.TemplateResponse("tutor_students.html", {"request": request, "assignments": [assignment], "selected": student, "progress": progress, "sessions": sessions})


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, db: Session = Depends(get_db)):
    require_user(request, db, "admin")
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "users": db.scalars(select(User).order_by(User.created_at.desc())).all(),
        "profiles": db.scalars(select(StudentProfile).options(selectinload(StudentProfile.curriculum))).all(),
        "curricula": db.scalars(select(Curriculum).order_by(Curriculum.id)).all(),
        "enrollments": db.scalars(select(Enrollment).options(selectinload(Enrollment.student), selectinload(Enrollment.course))).all(),
        "assignments": db.scalars(select(TutorStudentAssignment)).all(),
        "lessons": db.scalars(select(Lesson).order_by(Lesson.order_index)).all(),
    })
