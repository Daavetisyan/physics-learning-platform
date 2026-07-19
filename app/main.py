from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .content import COURSE, LESSONS
from .lesson_content import LESSON_CONTENTS
from .database import Base, SessionLocal, engine
from .homework import (
    ACTIVE_STATUSES,
    effective_status,
    grade_answer,
    homework_summary,
    homework_view,
    parse_options,
    seed_homework,
)
from .models import (
    HomeworkAnswer,
    HomeworkAssignment,
    HomeworkAttempt,
    LegacyHomeworkSubmission,
    Lesson,
    Progress,
    Student,
    TutorSession,
)
from .services.ai_scientist import answer_as_scientist

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Physics Learning Platform MVP", version="0.1.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_database(db: Session) -> None:
    student = db.scalar(select(Student).where(Student.email == "demo@student.example"))
    if not student:
        student = Student(name="Alex Morgan", email="demo@student.example", grade=8)
        db.add(student)

    for idx, item in enumerate(LESSONS, start=1):
        existing = db.scalar(select(Lesson).where(Lesson.slug == item["slug"]))
        if not existing:
            db.add(
                Lesson(
                    slug=item["slug"],
                    title=item["title"],
                    unit=item["unit"],
                    order_index=idx,
                    summary=item["summary"],
                    duration_minutes=item["duration"],
                )
            )
        else:
            existing.title = item["title"]
            existing.unit = item["unit"]
            existing.order_index = idx
            existing.summary = item["summary"]
            existing.duration_minutes = item["duration"]
    db.commit()

    student = db.scalar(select(Student).where(Student.email == "demo@student.example"))
    first_lesson = db.scalar(select(Lesson).order_by(Lesson.order_index).limit(1))
    if first_lesson:
        progress = db.scalar(
            select(Progress).where(
                Progress.student_id == student.id,
                Progress.lesson_id == first_lesson.id,
            )
        )
        if not progress:
            db.add(Progress(student_id=student.id, lesson_id=first_lesson.id, status="in_progress", score=None))
    db.commit()
    seed_homework(db, student)


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)


@app.on_event("startup")
def startup() -> None:
    initialize_database()


# Initialize during import as well, so scripts and test clients have seeded data.
initialize_database()


def build_lesson_steps(content: dict) -> list[dict[str, str]]:
    steps: list[dict[str, str]] = [
        {"key": "overview", "label": "Start and diagnostic", "group": "Start", "description": "Understand the lesson goal, prerequisites, and your current idea."},
        {"key": "vocabulary", "label": "Physics vocabulary", "group": "Foundation", "description": "Learn the exact language used throughout the lesson."},
    ]
    for chapter in content.get("theory_chapters", []):
        steps.append(
            {
                "key": f"theory-{chapter['number']}",
                "label": chapter["heading"],
                "group": "Theory",
                "description": chapter["lead"],
            }
        )
    steps.extend(
        [
            {"key": "video", "label": "Video explanation", "group": "Explore", "description": "Reinforce the theory with a filmed physical demonstration."},
            {"key": "simulation", "label": "Interactive laboratory", "group": "Explore", "description": "Change the reference frame and observe what changes and what stays invariant."},
            {"key": "examples", "label": "Worked examples", "group": "Apply", "description": "Follow complete reasoning from the physical situation to the answer."},
            {"key": "misconceptions", "label": "Common misconceptions", "group": "Apply", "description": "Replace common but incorrect ideas with precise physics."},
            {"key": "practice", "label": "Independent practice", "group": "Practice", "description": "Solve questions at foundation, standard, and challenge levels."},
            {"key": "assistant", "label": f"Ask {content['scientist']['name']}", "group": "Support", "description": "Ask for another explanation, guided help, or feedback on your work."},
            {"key": "assessment", "label": "Mastery assessment", "group": "Check", "description": "Demonstrate complete understanding and identify what to revisit."},
            {"key": "homework", "label": "Homework investigation", "group": "Extend", "description": "Apply the lesson to a real space and submit your reasoning."},
            {"key": "summary", "label": "Summary and reflection", "group": "Finish", "description": "Consolidate the essential ideas and finish the lesson."},
        ]
    )
    return steps


def demo_student(db: Session) -> Student:
    student = db.scalar(select(Student).where(Student.email == "demo@student.example"))
    if not student:
        seed_database(db)
        student = db.scalar(select(Student).where(Student.email == "demo@student.example"))
    return student


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request, "course": COURSE})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    student = demo_student(db)
    lessons = db.scalars(select(Lesson).order_by(Lesson.order_index)).all()
    progress_rows = db.scalars(select(Progress).where(Progress.student_id == student.id)).all()
    progress_map = {row.lesson_id: row for row in progress_rows}
    completed = sum(1 for row in progress_rows if row.status == "completed")
    percent = round(100 * completed / len(lessons)) if lessons else 0
    sessions = db.scalars(
        select(TutorSession).where(TutorSession.student_id == student.id).order_by(TutorSession.starts_at)
    ).all()
    assignments = db.scalars(
        select(HomeworkAssignment)
        .options(selectinload(HomeworkAssignment.lesson), selectinload(HomeworkAssignment.questions))
        .order_by(HomeworkAssignment.due_date)
    ).all()
    attempts = db.scalars(
        select(HomeworkAttempt)
        .where(HomeworkAttempt.student_id == student.id)
        .options(selectinload(HomeworkAttempt.answers))
    ).all()
    attempt_map = {attempt.homework_id: attempt for attempt in attempts}
    homework_items = [homework_view(item, attempt_map.get(item.id)) for item in assignments]
    active_homework = [item for item in homework_items if item["status"] in ACTIVE_STATUSES][:3]
    homework_stats = homework_summary(homework_items)
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "student": student,
            "course": COURSE,
            "lessons": lessons,
            "progress_map": progress_map,
            "progress_percent": percent,
            "sessions": sessions,
            "production_slugs": set(LESSON_CONTENTS),
            "upcoming_homework": active_homework,
            "homework_stats": homework_stats,
        },
    )


@app.get("/course/{course_slug}", response_class=HTMLResponse)
def course_page(course_slug: str, request: Request, db: Session = Depends(get_db)):
    if course_slug != COURSE["slug"]:
        raise HTTPException(status_code=404, detail="Course not found")
    student = demo_student(db)
    lessons = db.scalars(select(Lesson).order_by(Lesson.order_index)).all()
    progress_rows = db.scalars(select(Progress).where(Progress.student_id == student.id)).all()
    progress_map = {row.lesson_id: row for row in progress_rows}
    return templates.TemplateResponse(
        "course.html",
        {
            "request": request,
            "course": COURSE,
            "lessons": lessons,
            "progress_map": progress_map,
            "production_slugs": set(LESSON_CONTENTS),
        },
    )


@app.get("/lesson/{lesson_slug}", response_class=HTMLResponse)
def lesson_page(lesson_slug: str, request: Request, db: Session = Depends(get_db)):
    lesson = db.scalar(select(Lesson).where(Lesson.slug == lesson_slug))
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    detailed_content = LESSON_CONTENTS.get(lesson_slug)
    if detailed_content:
        return RedirectResponse(url=f"/lesson/{lesson_slug}/overview", status_code=302)
    student = demo_student(db)
    progress = db.scalar(select(Progress).where(Progress.student_id == student.id, Progress.lesson_id == lesson.id))
    return templates.TemplateResponse(
        "lesson.html",
        {
            "request": request,
            "lesson": lesson,
            "course": COURSE,
            "content": None,
            "progress": progress,
        },
    )


@app.get("/lesson/{lesson_slug}/{section_key}", response_class=HTMLResponse)
def lesson_section_page(lesson_slug: str, section_key: str, request: Request, db: Session = Depends(get_db)):
    lesson = db.scalar(select(Lesson).where(Lesson.slug == lesson_slug))
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    content = LESSON_CONTENTS.get(lesson_slug)
    if not content:
        raise HTTPException(status_code=404, detail="This lesson is still being built")

    steps = build_lesson_steps(content)
    step_keys = [step["key"] for step in steps]
    if section_key not in step_keys:
        raise HTTPException(status_code=404, detail="Lesson section not found")

    active_index = step_keys.index(section_key)
    current_step = steps[active_index]
    previous_step = steps[active_index - 1] if active_index > 0 else None
    next_step = steps[active_index + 1] if active_index + 1 < len(steps) else None
    chapter = None
    if section_key.startswith("theory-"):
        chapter_number = int(section_key.split("-", 1)[1])
        chapter = next(
            (item for item in content["theory_chapters"] if item["number"] == chapter_number),
            None,
        )
        if chapter is None:
            raise HTTPException(status_code=404, detail="Theory chapter not found")

    student = demo_student(db)
    progress = db.scalar(select(Progress).where(Progress.student_id == student.id, Progress.lesson_id == lesson.id))
    homework_assignment = db.scalar(
        select(HomeworkAssignment)
        .where(HomeworkAssignment.lesson_id == lesson.id)
        .options(selectinload(HomeworkAssignment.questions))
    )
    homework_attempt = None
    homework_card = None
    if homework_assignment:
        homework_attempt = db.scalar(
            select(HomeworkAttempt)
            .where(
                HomeworkAttempt.homework_id == homework_assignment.id,
                HomeworkAttempt.student_id == student.id,
            )
            .options(selectinload(HomeworkAttempt.answers))
        )
        homework_card = homework_view(homework_assignment, homework_attempt)
    return templates.TemplateResponse(
        "lesson_section.html",
        {
            "request": request,
            "lesson": lesson,
            "course": COURSE,
            "content": content,
            "progress": progress,
            "steps": steps,
            "current_step": current_step,
            "previous_step": previous_step,
            "next_step": next_step,
            "step_index": active_index + 1,
            "step_percent": round(100 * (active_index + 1) / len(steps)),
            "chapter": chapter,
            "homework_card": homework_card,
        },
    )


@app.post("/api/progress/{lesson_slug}")
def update_progress(lesson_slug: str, request_data: dict, db: Session = Depends(get_db)):
    lesson = db.scalar(select(Lesson).where(Lesson.slug == lesson_slug))
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    student = demo_student(db)
    progress = db.scalar(select(Progress).where(Progress.student_id == student.id, Progress.lesson_id == lesson.id))
    if not progress:
        progress = Progress(student_id=student.id, lesson_id=lesson.id)
        db.add(progress)
    progress.status = str(request_data.get("status", "in_progress"))
    score = request_data.get("score")
    if score is not None:
        progress.score = float(score)
    db.commit()
    return {"ok": True, "status": progress.status, "score": progress.score}


@app.post("/api/homework/{lesson_slug}")
def submit_legacy_homework(lesson_slug: str, request_data: dict, db: Session = Depends(get_db)):
    lesson = db.scalar(select(Lesson).where(Lesson.slug == lesson_slug))
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    answer = str(request_data.get("answer", "")).strip()
    if len(answer) < 10:
        return JSONResponse({"ok": False, "message": "Please show more of your reasoning before submitting."}, status_code=400)
    student = demo_student(db)
    submission = LegacyHomeworkSubmission(student_id=student.id, lesson_id=lesson.id, answer=answer)
    db.add(submission)
    db.commit()
    return {"ok": True, "message": "Homework submitted. Your tutor can review it from the teaching dashboard."}


def homework_records(db: Session, student: Student) -> tuple[list[HomeworkAssignment], dict[int, HomeworkAttempt]]:
    assignments = db.scalars(
        select(HomeworkAssignment)
        .options(selectinload(HomeworkAssignment.lesson), selectinload(HomeworkAssignment.questions))
        .order_by(HomeworkAssignment.due_date)
    ).all()
    attempts = db.scalars(
        select(HomeworkAttempt)
        .where(HomeworkAttempt.student_id == student.id)
        .options(selectinload(HomeworkAttempt.answers))
    ).all()
    return list(assignments), {attempt.homework_id: attempt for attempt in attempts}


@app.get("/homework", response_class=HTMLResponse)
def homework_dashboard(request: Request, db: Session = Depends(get_db)):
    student = demo_student(db)
    assignments, attempt_map = homework_records(db, student)
    items = [homework_view(item, attempt_map.get(item.id)) for item in assignments]
    sections = {
        "assigned": [item for item in items if item["status"] in ACTIVE_STATUSES and item["assignment"].due_date <= datetime.now() + timedelta(days=7)],
        "upcoming": [item for item in items if item["status"] in ACTIVE_STATUSES and item["assignment"].due_date > datetime.now() + timedelta(days=7)],
        "submitted": [item for item in items if item["status"] == "submitted"],
        "completed": [item for item in items if item["status"] == "completed"],
    }
    return templates.TemplateResponse(
        "homework_dashboard.html",
        {"request": request, "student": student, "sections": sections, "summary": homework_summary(items)},
    )


def get_assignment(db: Session, homework_id: int) -> HomeworkAssignment:
    assignment = db.scalar(
        select(HomeworkAssignment)
        .where(HomeworkAssignment.id == homework_id)
        .options(selectinload(HomeworkAssignment.lesson), selectinload(HomeworkAssignment.questions))
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="Homework assignment not found")
    return assignment


def get_attempt(db: Session, homework_id: int, student_id: int) -> HomeworkAttempt | None:
    return db.scalar(
        select(HomeworkAttempt)
        .where(HomeworkAttempt.homework_id == homework_id, HomeworkAttempt.student_id == student_id)
        .options(selectinload(HomeworkAttempt.answers))
    )


def workspace_context(request: Request, assignment: HomeworkAssignment, attempt: HomeworkAttempt | None, error: str | None = None) -> dict:
    answer_map = {answer.question_id: answer for answer in attempt.answers} if attempt else {}
    questions = [
        {"question": question, "options": parse_options(question), "answer": answer_map.get(question.id)}
        for question in assignment.questions
    ]
    return {
        "request": request,
        "assignment": assignment,
        "attempt": attempt,
        "questions": questions,
        "progress": homework_view(assignment, attempt)["progress"],
        "status": effective_status(assignment, attempt),
        "error": error,
    }


@app.get("/homework/{homework_id}", response_class=HTMLResponse)
def homework_workspace(homework_id: int, request: Request, db: Session = Depends(get_db)):
    student = demo_student(db)
    assignment = get_assignment(db, homework_id)
    attempt = get_attempt(db, homework_id, student.id)
    if attempt and attempt.status in {"submitted", "completed"}:
        return RedirectResponse(url=f"/homework/{homework_id}/results", status_code=303)
    error = "Complete every required answer and unit before submitting." if request.query_params.get("error") == "required" else None
    return templates.TemplateResponse("homework_workspace.html", workspace_context(request, assignment, attempt, error))


def save_homework_answers(db: Session, assignment: HomeworkAssignment, attempt: HomeworkAttempt, form: dict) -> list[int]:
    existing = {answer.question_id: answer for answer in attempt.answers}
    missing: list[int] = []
    for question in assignment.questions:
        answer_text = str(form.get(f"answer_{question.id}", "")).strip()
        unit = str(form.get(f"unit_{question.id}", "")).strip() or None
        answer = existing.get(question.id)
        if not answer:
            answer = HomeworkAnswer(attempt=attempt, question=question)
            db.add(answer)
        answer.answer_text = answer_text
        answer.unit = unit
        answer.numerical_value = None
        answer.is_correct = None
        answer.points_awarded = None
        answer.feedback = ""
        if question.required and (not answer_text or (question.question_type == "numerical" and not unit)):
            missing.append(question.id)
    return missing


async def homework_form(request: Request) -> dict[str, str]:
    form = await request.form()
    return {str(key): str(value) for key, value in form.multi_items()}


@app.post("/homework/{homework_id}/save")
async def save_homework(homework_id: int, request: Request, db: Session = Depends(get_db)):
    student = demo_student(db)
    assignment = get_assignment(db, homework_id)
    attempt = get_attempt(db, homework_id, student.id)
    if attempt and attempt.status in {"submitted", "completed"}:
        raise HTTPException(status_code=409, detail="Submitted homework cannot be changed")
    if not attempt:
        attempt = HomeworkAttempt(homework_id=homework_id, student_id=student.id, status="in_progress", started_at=datetime.now())
        db.add(attempt)
        db.flush()
    form = await homework_form(request)
    save_homework_answers(db, assignment, attempt, form)
    if attempt.status != "needs_revision":
        attempt.status = "in_progress"
    db.commit()
    return RedirectResponse(url=f"/homework/{homework_id}?saved=1", status_code=303)


@app.post("/homework/{homework_id}/submit")
async def submit_homework(homework_id: int, request: Request, db: Session = Depends(get_db)):
    student = demo_student(db)
    assignment = get_assignment(db, homework_id)
    attempt = get_attempt(db, homework_id, student.id)
    if attempt and attempt.status in {"submitted", "completed"}:
        return RedirectResponse(url=f"/homework/{homework_id}/results", status_code=303)
    if not attempt:
        attempt = HomeworkAttempt(homework_id=homework_id, student_id=student.id, status="in_progress", started_at=datetime.now())
        db.add(attempt)
        db.flush()
    form = await homework_form(request)
    missing = save_homework_answers(db, assignment, attempt, form)
    if missing:
        db.commit()
        return RedirectResponse(url=f"/homework/{homework_id}?error=required", status_code=303)
    db.flush()
    answer_map = {answer.question_id: answer for answer in attempt.answers}
    auto_questions = [question for question in assignment.questions if question.question_type != "written"]
    for question in assignment.questions:
        grade_answer(question, answer_map[question.id])
    earned = sum((answer_map[question.id].points_awarded or 0) for question in auto_questions)
    available = sum(question.points for question in auto_questions)
    attempt.score = round(100 * earned / available) if available else None
    attempt.max_score = 100
    attempt.submitted_at = datetime.now()
    attempt.status = "submitted"
    attempt.feedback_status = "awaiting_review" if any(q.question_type == "written" for q in assignment.questions) else "feedback_ready"
    attempt.feedback = "Written responses are awaiting teacher or tutor review." if attempt.feedback_status == "awaiting_review" else "Automatic grading complete."
    db.commit()
    return RedirectResponse(url=f"/homework/{homework_id}/results?submitted=1", status_code=303)


@app.get("/homework/{homework_id}/results", response_class=HTMLResponse)
def homework_results(homework_id: int, request: Request, db: Session = Depends(get_db)):
    student = demo_student(db)
    assignment = get_assignment(db, homework_id)
    attempt = get_attempt(db, homework_id, student.id)
    if not attempt or attempt.status not in {"submitted", "needs_revision", "completed"}:
        return RedirectResponse(url=f"/homework/{homework_id}", status_code=303)
    answer_map = {answer.question_id: answer for answer in attempt.answers}
    results = [{"question": question, "answer": answer_map.get(question.id)} for question in assignment.questions]
    return templates.TemplateResponse(
        "homework_results.html",
        {"request": request, "assignment": assignment, "attempt": attempt, "results": results, "submitted": request.query_params.get("submitted") == "1"},
    )


@app.post("/api/ai-chat")
def ai_chat(request_data: dict):
    message = str(request_data.get("message", ""))
    mode = str(request_data.get("mode", "explain"))
    lesson_slug = str(request_data.get("lesson_slug", "position-reference-points"))
    return {"reply": answer_as_scientist(message, mode, lesson_slug)}


@app.get("/tutoring", response_class=HTMLResponse)
def tutoring_page(request: Request, db: Session = Depends(get_db)):
    student = demo_student(db)
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    slots = []
    for day_offset in range(1, 8):
        day = now + timedelta(days=day_offset)
        for hour in (16, 18):
            candidate = day.replace(hour=hour)
            slots.append(candidate)
    sessions = db.scalars(
        select(TutorSession).where(TutorSession.student_id == student.id).order_by(TutorSession.starts_at)
    ).all()
    return templates.TemplateResponse(
        "tutoring.html",
        {"request": request, "student": student, "slots": slots, "sessions": sessions},
    )


@app.post("/tutoring/book")
def book_tutor(
    topic: str = Form(...),
    starts_at: str = Form(...),
    db: Session = Depends(get_db),
):
    student = demo_student(db)
    try:
        start = datetime.fromisoformat(starts_at)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date") from exc
    meeting_code = uuid4().hex[:10]
    session = TutorSession(
        student_id=student.id,
        topic=topic.strip() or "Physics support",
        starts_at=start,
        price_usd=35.0,
        payment_status="demo_paid",
        meeting_url=f"https://meet.google.com/{meeting_code}",
    )
    db.add(session)
    db.commit()
    return RedirectResponse(url="/tutoring?booked=1", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, db: Session = Depends(get_db)):
    submissions = db.scalars(select(LegacyHomeworkSubmission).order_by(LegacyHomeworkSubmission.submitted_at.desc())).all()
    sessions = db.scalars(select(TutorSession).order_by(TutorSession.starts_at)).all()
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "submissions": submissions, "sessions": sessions},
    )
