from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(500))
    role: Mapped[str] = mapped_column(String(20), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    student_profile: Mapped["StudentProfile | None"] = relationship(back_populates="user", uselist=False)


class Curriculum(Base):
    __tablename__ = "curricula"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180))
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True)
    country: Mapped[str] = mapped_column(String(80), default="United States")
    description: Mapped[str] = mapped_column(Text)
    grade_min: Mapped[int] = mapped_column(Integer, default=7)
    grade_max: Mapped[int] = mapped_column(Integer, default=9)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class StudentProfile(Base):
    """Academic profile. The legacy table name preserves progress/homework foreign keys."""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), unique=True, nullable=True, index=True)
    # Legacy-compatible columns retained for a safe homework-branch rebase.
    name: Mapped[str] = mapped_column(String(100), default="")
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    grade: Mapped[int] = mapped_column(Integer, default=8)
    display_name: Mapped[str] = mapped_column(String(100), default="")
    grade_level: Mapped[int] = mapped_column(Integer, default=8)
    curriculum_id: Mapped[int | None] = mapped_column(ForeignKey("curricula.id"), nullable=True)
    learning_level: Mapped[str] = mapped_column(String(20), default="standard")
    timezone: Mapped[str] = mapped_column(String(80), default="America/New_York")
    preferred_unit_system: Mapped[str] = mapped_column(String(20), default="metric")
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped[User | None] = relationship(back_populates="student_profile")
    curriculum: Mapped[Curriculum | None] = relationship()
    guardian_contacts: Mapped[list["GuardianContact"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    progress: Mapped[list["Progress"]] = relationship(back_populates="student", cascade="all, delete-orphan")


# Compatibility alias for the unmerged homework branch.
Student = StudentProfile


class GuardianContact(Base):
    __tablename__ = "guardian_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255))
    relationship_type: Mapped[str] = mapped_column("relationship", String(60))
    receives_progress_emails: Mapped[bool] = mapped_column(Boolean, default=True)
    billing_customer_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    consent_recorded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped[StudentProfile] = relationship(back_populates="guardian_contacts")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(180))
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("student_id", "course_id", "curriculum_id", name="uq_student_course_curriculum"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    curriculum_id: Mapped[int] = mapped_column(ForeignKey("curricula.id"), index=True)
    grade_level: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="active")
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completion_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    student: Mapped[StudentProfile] = relationship(back_populates="enrollments")
    course: Mapped[Course] = relationship()
    curriculum: Mapped[Curriculum] = relationship()


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(180))
    concept_key: Mapped[str] = mapped_column(String(140), default="")
    course_id: Mapped[int | None] = mapped_column(ForeignKey("courses.id"), nullable=True, index=True)
    unit: Mapped[str] = mapped_column(String(120))
    order_index: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str] = mapped_column(Text)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=35)
    publication_status: Mapped[str] = mapped_column(String(30), default="published")

    course: Mapped[Course | None] = relationship()
    variants: Mapped[list["LessonVariant"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
    progress: Mapped[list["Progress"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")


class LessonVariant(Base):
    __tablename__ = "lesson_variants"
    __table_args__ = (UniqueConstraint("lesson_id", "curriculum_id", "learning_level", name="uq_lesson_curriculum_level"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), index=True)
    curriculum_id: Mapped[int] = mapped_column(ForeignKey("curricula.id"), index=True)
    grade_min: Mapped[int] = mapped_column(Integer, default=7)
    grade_max: Mapped[int] = mapped_column(Integer, default=9)
    learning_level: Mapped[str] = mapped_column(String(20), default="standard")
    content_reference: Mapped[str] = mapped_column(String(200))
    publication_status: Mapped[str] = mapped_column(String(30), default="published")

    lesson: Mapped[Lesson] = relationship(back_populates="variants")
    curriculum: Mapped[Curriculum] = relationship()


class Progress(Base):
    __tablename__ = "progress"
    __table_args__ = (UniqueConstraint("student_id", "lesson_id", name="uq_student_lesson_progress"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    status: Mapped[str] = mapped_column(String(30), default="not_started")
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student: Mapped[StudentProfile] = relationship(back_populates="progress")
    lesson: Mapped[Lesson] = relationship(back_populates="progress")


class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    answer: Mapped[str] = mapped_column(Text)
    feedback: Mapped[str] = mapped_column(Text, default="Submitted for review.")
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TutorSession(Base):
    __tablename__ = "tutor_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    tutor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    topic: Mapped[str] = mapped_column(String(200))
    starts_at: Mapped[datetime] = mapped_column(DateTime)
    price_usd: Mapped[float] = mapped_column(Float, default=35.0)
    payment_status: Mapped[str] = mapped_column(String(30), default="demo_paid")
    meeting_url: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(30), default="scheduled")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TutorStudentAssignment(Base):
    __tablename__ = "tutor_student_assignments"
    __table_args__ = (UniqueConstraint("tutor_id", "student_id", name="uq_tutor_student"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tutor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tutor: Mapped[User] = relationship()
    student: Mapped[StudentProfile] = relationship()


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    lesson_id: Mapped[int | None] = mapped_column(ForeignKey("lessons.id"), nullable=True)
    mode: Mapped[str] = mapped_column(String(30))
    user_message: Mapped[str] = mapped_column(Text)
    assistant_message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
