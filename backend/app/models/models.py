"""SQLAlchemy ORM models for the platform."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

# ---------------------------------------------------------------------------
# Enums (stored as strings)
# ---------------------------------------------------------------------------

EXPERIENCE_BANDS = ["1-3", "4-7", "8-12", "13-20", "20+"]
EXPERIENCE_BAND_YEARS = {"1-3": 3, "4-7": 7, "8-12": 12, "13-20": 20, "20+": 99}

DIFFICULTIES = ["hard", "very_hard", "expert"]

QUESTION_TYPES = [
    "single",
    "multiple",
    "assertion_reason",
    "scenario",
    "code",
    "numerical",
    "debugging",
]

ATTEMPT_STATUSES = ["in_progress", "completed", "auto_submitted"]

VIOLATION_TYPES = [
    "TAB_SWITCH",
    "FOCUS_LOSS",
    "COPY_ATTEMPT",
    "PASTE_ATTEMPT",
    "CUT_ATTEMPT",
    "CONTEXT_MENU",
    "FULLSCREEN_EXIT",
    "PRINT_ATTEMPT",
    "KEYBOARD_SHORTCUT",
    "CAMERA_OBSTRUCTED",
    "CAMERA_TOO_DARK",
    "CAMERA_TOO_BRIGHT",
    "CAMERA_DISCONNECTED",
    "CAMERA_PERMISSION_LOST",
]

DEFAULT_VIOLATION_PENALTIES: dict[str, float] = {
    "TAB_SWITCH": -1.0,
    "COPY_ATTEMPT": -1.0,
    "PASTE_ATTEMPT": -1.0,
    "CUT_ATTEMPT": -1.0,
    "FULLSCREEN_EXIT": -1.0,
    "CONTEXT_MENU": -0.5,
    "FOCUS_LOSS": -0.5,
    "PRINT_ATTEMPT": -0.5,
    "KEYBOARD_SHORTCUT": -0.5,
    "CAMERA_OBSTRUCTED": -1.0,
    "CAMERA_TOO_DARK": -0.5,
    "CAMERA_TOO_BRIGHT": -0.5,
    "CAMERA_DISCONNECTED": -2.0,
    "CAMERA_PERMISSION_LOST": -2.0,
}

DEFAULT_EXPERIENCE_DISTRIBUTION: dict[str, dict[str, int]] = {
    # band -> {hard, very_hard, expert} percentages (must sum to 100)
    "1-3": {"hard": 50, "very_hard": 35, "expert": 15},
    "4-7": {"hard": 30, "very_hard": 40, "expert": 30},
    "8-12": {"hard": 15, "very_hard": 40, "expert": 45},
    "13-20": {"hard": 10, "very_hard": 30, "expert": 60},
    "20+": {"hard": 5, "very_hard": 25, "expert": 70},
}


def utcnow() -> datetime:
    """Naive UTC now. Stored/compared in UTC everywhere; SQLite drops tzinfo anyway."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def normalize_name(name: str) -> str:
    """Normalize a full name: trim, collapse whitespace, uppercase."""
    return " ".join(name.strip().upper().split())


# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("name_normalized", name="uq_user_name_normalized"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), index=True)
    name_normalized: Mapped[str] = mapped_column(String(200), index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    password_hash: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20), default="faculty", index=True)  # faculty | admin
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    department: Mapped[Department] = relationship()


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    difficulty_label: Mapped[str] = mapped_column(String(100), default="Expert Assessment")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    topics: Mapped[list[Topic]] = relationship(back_populates="subject", cascade="all, delete-orphan")  # type: ignore[name-defined]
    questions: Mapped[list[Question]] = relationship(back_populates="subject")  # type: ignore[name-defined]


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (UniqueConstraint("subject_id", "name", name="uq_topic_subject_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))

    subject: Mapped[Subject] = relationship(back_populates="topics")
    questions: Mapped[list[Question]] = relationship(back_populates="topic")  # type: ignore[name-defined]


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (
        Index("ix_questions_subject_difficulty", "subject_id", "difficulty"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), index=True)
    difficulty: Mapped[str] = mapped_column(String(20), index=True)  # hard | very_hard | expert
    experience_min: Mapped[int] = mapped_column(Integer, default=1)  # minimum teaching years
    question_type: Mapped[str] = mapped_column(String(30), default="single")
    question_text: Mapped[str] = mapped_column(Text)
    options: Mapped[list] = mapped_column(JSON)  # list[str] in canonical order
    correct_answer: Mapped[list] = mapped_column(JSON)  # list[int] indices into options
    explanation: Mapped[str] = mapped_column(Text, default="")
    marks: Mapped[int] = mapped_column(Integer, default=1)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    subject: Mapped[Subject] = relationship(back_populates="questions")
    topic: Mapped[Topic] = relationship(back_populates="questions")


class ExamConfig(Base):
    __tablename__ = "exam_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), unique=True, index=True)
    num_questions: Mapped[int] = mapped_column(Integer, default=40)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class ExperienceBandConfig(Base):
    __tablename__ = "experience_band_configs"
    __table_args__ = (UniqueConstraint("band", name="uq_band"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    band: Mapped[str] = mapped_column(String(10), index=True)
    hard_pct: Mapped[int] = mapped_column(Integer, default=30)
    very_hard_pct: Mapped[int] = mapped_column(Integer, default=40)
    expert_pct: Mapped[int] = mapped_column(Integer, default=30)


class ViolationPenalty(Base):
    __tablename__ = "violation_penalties"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(100))
    penalty: Mapped[float] = mapped_column(Float, default=-1.0)
    description: Mapped[str] = mapped_column(String(300), default="")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


# ---------------------------------------------------------------------------
# Exam runtime data
# ---------------------------------------------------------------------------


class ExamAttempt(Base):
    __tablename__ = "exam_attempts"
    __table_args__ = (
        Index("ix_attempts_faculty_subject", "faculty_id", "subject_id"),
        Index("ix_attempts_faculty_status", "faculty_id", "status"),
        # Prevents a second completed attempt for the same (faculty, subject).
        Index(
            "uq_completed_attempt",
            "faculty_id",
            "subject_id",
            unique=True,
            sqlite_where=text("status IN ('completed', 'auto_submitted')"),
            postgresql_where=text("status IN ('completed', 'auto_submitted')"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    experience_band: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20), default="in_progress", index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    time_used_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    penalty_total: Mapped[float] = mapped_column(Float, default=0.0)
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    faculty: Mapped[User] = relationship()
    subject: Mapped[Subject] = relationship()
    exam_questions: Mapped[list[ExamQuestion]] = relationship(
        back_populates="attempt", cascade="all, delete-orphan", order_by="ExamQuestion.position"
    )
    violations: Mapped[list[Violation]] = relationship(back_populates="attempt", cascade="all, delete-orphan")
    recording: Mapped[Recording | None] = relationship(back_populates="attempt", uselist=False)  # type: ignore[name-defined]


class ExamQuestion(Base):
    __tablename__ = "exam_questions"
    __table_args__ = (UniqueConstraint("attempt_id", "position", name="uq_attempt_position"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("exam_attempts.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    position: Mapped[int] = mapped_column(Integer)  # 1..N
    option_order: Mapped[list] = mapped_column(JSON)  # list[int]: new_index -> original_index
    chosen_options: Mapped[list | None] = mapped_column(JSON, nullable=True)  # chosen option indices (display order)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    marks_awarded: Mapped[float | None] = mapped_column(Float, nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    attempt: Mapped[ExamAttempt] = relationship(back_populates="exam_questions")
    question: Mapped[Question] = relationship()


class Violation(Base):
    __tablename__ = "violations"
    __table_args__ = (Index("ix_violations_attempt", "attempt_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("exam_attempts.id"), index=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(50), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    details: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    penalty: Mapped[float] = mapped_column(Float, default=0.0)

    attempt: Mapped[ExamAttempt] = relationship(back_populates="violations")


class CameraEvent(Base):
    """Periodic camera health snapshots (no penalty) - e.g. brightness, obstruction."""

    __tablename__ = "camera_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("exam_attempts.id"), index=True)
    type: Mapped[str] = mapped_column(String(50), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    details: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)


class Recording(Base):
    __tablename__ = "recordings"

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("exam_attempts.id"), unique=True, index=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="recording")  # recording|finalizing|ready|failed|none
    mime_type: Mapped[str] = mapped_column(String(100), default="video/webm")
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    segment_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)

    attempt: Mapped[ExamAttempt] = relationship(back_populates="recording")


class VideoSegment(Base):
    __tablename__ = "video_segments"

    id: Mapped[int] = mapped_column(primary_key=True)
    recording_id: Mapped[int] = mapped_column(ForeignKey("recordings.id"), index=True)
    index: Mapped[int] = mapped_column(Integer)
    file_path: Mapped[str] = mapped_column(String(500))
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
