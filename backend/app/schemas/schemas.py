"""Pydantic schemas (request/response models)."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    department: str = Field(min_length=2, max_length=200)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    full_name: str
    password: str


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    department: str
    role: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------


class DepartmentOut(BaseModel):
    id: int
    name: str
    code: str

    model_config = {"from_attributes": True}


class DepartmentCreate(BaseModel):
    name: str
    code: str


class TopicOut(BaseModel):
    id: int
    subject_id: int
    name: str

    model_config = {"from_attributes": True}


class TopicCreate(BaseModel):
    name: str


class SubjectOut(BaseModel):
    id: int
    name: str
    code: str
    description: str
    difficulty_label: str
    active: bool

    model_config = {"from_attributes": True}


class SubjectCreate(BaseModel):
    name: str
    code: str
    description: str = ""
    difficulty_label: str = "Expert Assessment"


class ExamConfigOut(BaseModel):
    id: int
    subject_id: int
    num_questions: int
    duration_minutes: int
    active: bool

    model_config = {"from_attributes": True}


class ExamConfigUpdate(BaseModel):
    num_questions: int = Field(ge=1, le=100)
    duration_minutes: int = Field(ge=5, le=240)
    active: bool = True


class ExperienceConfigOut(BaseModel):
    id: int
    band: str
    hard_pct: int
    very_hard_pct: int
    expert_pct: int

    model_config = {"from_attributes": True}


class ExperienceConfigUpdate(BaseModel):
    hard_pct: int = Field(ge=0, le=100)
    very_hard_pct: int = Field(ge=0, le=100)
    expert_pct: int = Field(ge=0, le=100)


class ViolationPenaltyOut(BaseModel):
    id: int
    type: str
    label: str
    penalty: float
    description: str
    enabled: bool

    model_config = {"from_attributes": True}


class ViolationPenaltyUpdate(BaseModel):
    penalty: float = Field(le=0)
    description: str = ""
    enabled: bool = True


# ---------------------------------------------------------------------------
# Questions (admin)
# ---------------------------------------------------------------------------


class QuestionBase(BaseModel):
    subject_id: int
    topic_id: int
    difficulty: str
    experience_min: int = Field(ge=1)
    question_type: str
    question_text: str
    options: list[str] = Field(min_length=2, max_length=6)
    correct_answer: list[int]
    explanation: str = ""


class QuestionAdminOut(QuestionBase):
    id: int
    active: bool
    subject_name: str = ""
    topic_name: str = ""

    model_config = {"from_attributes": True}


class QuestionListOut(BaseModel):
    items: list[QuestionAdminOut]
    total: int


# Public question shown to faculty during the exam (no answers, no explanation)
class QuestionPublic(BaseModel):
    position: int
    question_type: str
    question_text: str
    options: list[str]
    marks: int


# ---------------------------------------------------------------------------
# Faculty dashboard
# ---------------------------------------------------------------------------


class SubjectStatusOut(BaseModel):
    subject: SubjectOut
    status: str  # AVAILABLE | IN_PROGRESS | COMPLETED | LOCKED
    attempt_id: int | None = None
    total_questions: int
    duration_minutes: int
    question_count: int


# ---------------------------------------------------------------------------
# Exam flow
# ---------------------------------------------------------------------------


class StartExamRequest(BaseModel):
    subject_id: int
    experience_band: str


class AnswerSubmit(BaseModel):
    position: int = Field(ge=1)
    chosen_options: list[int] = Field(min_length=0, max_length=6)


class ViolationCreate(BaseModel):
    type: str
    duration_seconds: float = 0.0
    metadata: dict[str, Any] | None = None


class AttemptStatusOut(BaseModel):
    attempt_id: int
    subject_id: int
    subject_name: str
    experience_band: str
    status: str
    started_at: datetime
    deadline: datetime
    server_time: datetime
    duration_minutes: int
    num_questions: int
    last_position: int
    answered_positions: list[int]
    answers: dict[str, list[int]] = {}
    violation_count: int
    penalty_total: float
    questions: list[QuestionPublic] | None = None


class StartExamOut(BaseModel):
    attempt_id: int
    subject_id: int
    subject_name: str
    experience_band: str
    deadline: datetime
    server_time: datetime
    duration_minutes: int
    num_questions: int
    questions: list[QuestionPublic]
    resuming: bool = False


class ViolationSummaryItem(BaseModel):
    type: str
    count: int
    penalty_per: float
    total_penalty: float


class SubmitOut(BaseModel):
    attempt_id: int
    status: str  # completed | auto_submitted
    subject_id: int
    num_questions: int
    answered: int
    violations: list[ViolationSummaryItem]
    total_penalty: float
    time_used_seconds: int
    score_hidden: bool = True
    subject_locked: bool = True


class ResultOut(BaseModel):
    attempt_id: int
    subject_name: str
    status: str
    num_questions: int
    answered: int
    violations: list[ViolationSummaryItem]
    total_penalty: float
    time_used_seconds: int
    score_hidden: bool = True
    subject_locked: bool = True


# ---------------------------------------------------------------------------
# Admin analytics / reports
# ---------------------------------------------------------------------------


class AdminStats(BaseModel):
    total_faculty: int
    exams_completed: int
    exams_pending: int
    total_subjects: int
    total_questions: int
    total_violations: int


class FacultyListItem(BaseModel):
    id: int
    full_name: str
    department: str
    subjects_completed: int
    average_score: float
    total_violations: int
    created_at: datetime


class AttemptListItem(BaseModel):
    id: int
    faculty_name: str
    department: str
    subject_name: str
    experience_band: str
    status: str
    started_at: datetime
    submitted_at: datetime | None
    time_used_seconds: int | None
    raw_score: float | None
    penalty_total: float
    final_score: float | None
    violation_count: int


class AdminQuestionReportItem(BaseModel):
    position: int
    question_type: str
    question_text: str
    difficulty: str
    topic: str
    options: list[str]
    correct_options: list[int]  # indices into options
    chosen_options: list[int]
    is_correct: bool
    marks_awarded: float
    explanation: str


class ViolationTimelineItem(BaseModel):
    id: int
    type: str
    timestamp: datetime
    duration_seconds: float
    penalty: float
    details: dict[str, Any] | None = None


class AdminExamReport(BaseModel):
    attempt_id: int
    faculty_name: str
    department: str
    subject_name: str
    experience_band: str
    status: str
    started_at: datetime
    submitted_at: datetime | None
    time_used_seconds: int | None
    duration_minutes: int
    num_questions: int
    answered: int
    unanswered: int
    correct: int
    incorrect: int
    raw_score: float
    penalty_total: float
    final_score: float
    questions: list[AdminQuestionReportItem]
    violations: list[ViolationTimelineItem]
    violation_summary: list[ViolationSummaryItem]
    recording: dict[str, Any] | None = None


class RecordingMeta(BaseModel):
    attempt_id: int
    status: str
    mime_type: str
    segment_count: int
    duration_seconds: float
    started_at: datetime | None
    ended_at: datetime | None
    url: str | None = None


class CameraEventOut(BaseModel):
    id: int
    attempt_id: int
    type: str
    timestamp: datetime
    metadata: dict[str, Any] | None = None

    model_config = {"from_attributes": True}
