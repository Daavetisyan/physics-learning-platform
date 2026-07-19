from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    grade: Mapped[int] = mapped_column(Integer, default=8)

    progress: Mapped[list["Progress"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    homework_attempts: Mapped[list["HomeworkAttempt"]] = relationship(back_populates="student", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(180))
    unit: Mapped[str] = mapped_column(String(120))
    order_index: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str] = mapped_column(Text)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=35)

    progress: Mapped[list["Progress"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
    homework_assignments: Mapped[list["HomeworkAssignment"]] = relationship(back_populates="lesson")


class Progress(Base):
    __tablename__ = "progress"
    __table_args__ = (UniqueConstraint("student_id", "lesson_id", name="uq_student_lesson_progress"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    status: Mapped[str] = mapped_column(String(30), default="not_started")
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student: Mapped[Student] = relationship(back_populates="progress")
    lesson: Mapped[Lesson] = relationship(back_populates="progress")


class LegacyHomeworkSubmission(Base):
    """Preserves submissions created by the prototype's former lesson textarea."""

    __tablename__ = "homework_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    answer: Mapped[str] = mapped_column(Text)
    feedback: Mapped[str] = mapped_column(Text, default="Submitted for review.")
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HomeworkAssignment(Base):
    __tablename__ = "homework_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    instructions: Mapped[str] = mapped_column(Text)
    reference_text: Mapped[str] = mapped_column(Text, default="")
    due_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=30)
    assigned_by: Mapped[str] = mapped_column(String(100), default="Platform")
    status: Mapped[str] = mapped_column(String(30), default="assigned")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lesson: Mapped[Lesson] = relationship(back_populates="homework_assignments")
    questions: Mapped[list["HomeworkQuestion"]] = relationship(
        back_populates="homework", cascade="all, delete-orphan", order_by="HomeworkQuestion.order_index"
    )
    attempts: Mapped[list["HomeworkAttempt"]] = relationship(back_populates="homework", cascade="all, delete-orphan")


class HomeworkQuestion(Base):
    __tablename__ = "homework_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    homework_id: Mapped[int] = mapped_column(ForeignKey("homework_assignments.id"), index=True)
    order_index: Mapped[int] = mapped_column(Integer)
    question_type: Mapped[str] = mapped_column(String(30))
    prompt: Mapped[str] = mapped_column(Text)
    options_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    correct_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, default="")
    expected_unit: Mapped[str | None] = mapped_column(String(40), nullable=True)
    tolerance: Mapped[float | None] = mapped_column(Float, nullable=True)
    significant_figures: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hint: Mapped[str] = mapped_column(Text, default="")
    points: Mapped[float] = mapped_column(Float, default=1.0)
    required: Mapped[bool] = mapped_column(Boolean, default=True)

    homework: Mapped[HomeworkAssignment] = relationship(back_populates="questions")
    answers: Mapped[list["HomeworkAnswer"]] = relationship(back_populates="question")


class HomeworkAttempt(Base):
    __tablename__ = "homework_attempts"
    __table_args__ = (UniqueConstraint("homework_id", "student_id", name="uq_homework_student_attempt"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    homework_id: Mapped[int] = mapped_column(ForeignKey("homework_assignments.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="assigned")
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str] = mapped_column(Text, default="")
    feedback_status: Mapped[str] = mapped_column(String(30), default="not_submitted")

    homework: Mapped[HomeworkAssignment] = relationship(back_populates="attempts")
    student: Mapped[Student] = relationship(back_populates="homework_attempts")
    answers: Mapped[list["HomeworkAnswer"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")


class HomeworkAnswer(Base):
    __tablename__ = "homework_answers"
    __table_args__ = (UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question_answer"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("homework_attempts.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("homework_questions.id"), index=True)
    answer_text: Mapped[str] = mapped_column(Text, default="")
    numerical_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(40), nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    points_awarded: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str] = mapped_column(Text, default="")
    saved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    attempt: Mapped[HomeworkAttempt] = relationship(back_populates="answers")
    question: Mapped[HomeworkQuestion] = relationship(back_populates="answers")


class TutorSession(Base):
    __tablename__ = "tutor_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    topic: Mapped[str] = mapped_column(String(200))
    starts_at: Mapped[datetime] = mapped_column(DateTime)
    price_usd: Mapped[float] = mapped_column(Float, default=35.0)
    payment_status: Mapped[str] = mapped_column(String(30), default="demo_paid")
    meeting_url: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(30), default="scheduled")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
