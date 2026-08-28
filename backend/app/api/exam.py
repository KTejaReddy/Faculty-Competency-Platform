"""Exam flow endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from ..exam.engine import (
    auto_submit_if_expired,
    build_exam_payload,
    build_submit_response,
    get_attempt_or_404,
    load_attempt_owner,
    now_utc,
    record_violation,
    save_answer,
    start_attempt,
    violation_summary,
)
from ..models.models import (
    VIOLATION_TYPES,
    ExamAttempt,
    ExamConfig,
    Recording,
    Subject,
    Violation,
)
from ..schemas.schemas import (
    AnswerSubmit,
    AttemptStatusOut,
    ResultOut,
    StartExamOut,
    StartExamRequest,
    SubmitOut,
    ViolationCreate,
)
from .deps import CurrentUser, DbDep

router = APIRouter(prefix="/exams", tags=["exam"])


def _duration_of(db: DbDep, attempt: ExamAttempt) -> int:
    cfg = db.scalar(select(ExamConfig).where(ExamConfig.subject_id == attempt.subject_id))
    return cfg.duration_minutes if cfg else 60


@router.post("/start", response_model=StartExamOut)
def start_exam(payload: StartExamRequest, db: DbDep, user: CurrentUser):
    if user.role != "faculty":
        raise HTTPException(403, "Only faculty can take examinations.")
    subject = db.get(Subject, payload.subject_id)
    if subject is None or not subject.active:
        raise HTTPException(404, "Subject not found")

    attempt = start_attempt(db, user.id, payload.subject_id, payload.experience_band)
    resuming = any(eq.chosen_options is not None for eq in attempt.exam_questions)

    return StartExamOut(
        attempt_id=attempt.id,
        subject_id=attempt.subject_id,
        subject_name=subject.name,
        experience_band=attempt.experience_band,
        deadline=attempt.deadline,
        server_time=now_utc(),
        duration_minutes=_duration_of(db, attempt),
        num_questions=len(attempt.exam_questions),
        questions=build_exam_payload(attempt),
        resuming=resuming,
    )


@router.get("/attempts/{attempt_id}/status", response_model=AttemptStatusOut)
def attempt_status(attempt_id: int, db: DbDep, user: CurrentUser):
    attempt = load_attempt_owner(db, attempt_id, user.id)
    attempt = auto_submit_if_expired(db, attempt)

    answered = [eq.position for eq in attempt.exam_questions if eq.chosen_options is not None]
    answers = {
        str(eq.position): (eq.chosen_options or []) for eq in attempt.exam_questions if eq.chosen_options is not None
    }
    violations = db.scalars(select(Violation).where(Violation.attempt_id == attempt.id)).all()

    return AttemptStatusOut(
        attempt_id=attempt.id,
        subject_id=attempt.subject_id,
        subject_name=attempt.subject.name,
        experience_band=attempt.experience_band,
        status=attempt.status,
        started_at=attempt.start_time,
        deadline=attempt.deadline,
        server_time=now_utc(),
        duration_minutes=_duration_of(db, attempt),
        num_questions=len(attempt.exam_questions),
        last_position=max(answered) if answered else 0,
        answered_positions=answered,
        answers=answers,
        violation_count=len(violations),
        penalty_total=attempt.penalty_total,
        questions=None,
    )


@router.post("/attempts/{attempt_id}/answers")
def submit_answer(attempt_id: int, payload: AnswerSubmit, db: DbDep, user: CurrentUser):
    attempt = load_attempt_owner(db, attempt_id, user.id)
    attempt = auto_submit_if_expired(db, attempt)
    if attempt.status != "in_progress":
        raise HTTPException(409, "This attempt has already been submitted.")
    save_answer(db, attempt, payload.position, payload.chosen_options)
    return {"ok": True, "position": payload.position}


@router.post("/attempts/{attempt_id}/violations")
def report_violation(attempt_id: int, payload: ViolationCreate, db: DbDep, user: CurrentUser):
    attempt = load_attempt_owner(db, attempt_id, user.id)
    attempt = auto_submit_if_expired(db, attempt)
    if attempt.status != "in_progress":
        raise HTTPException(409, "This attempt has already been submitted.")
    if payload.type not in VIOLATION_TYPES:
        raise HTTPException(400, f"Unknown violation type: {payload.type}")

    violation = record_violation(
        db, attempt, payload.type, payload.duration_seconds, payload.metadata
    )
    return {
        "id": violation.id,
        "type": violation.type,
        "penalty": violation.penalty,
        "penalty_total": attempt.penalty_total,
        "violation_count": len(attempt.violations),
    }


@router.post("/attempts/{attempt_id}/submit", response_model=SubmitOut)
def submit_exam(attempt_id: int, db: DbDep, user: CurrentUser):
    attempt = load_attempt_owner(db, attempt_id, user.id)
    if attempt.status == "in_progress":
        attempt = auto_submit_if_expired(db, attempt)  # submits if the deadline passed
        if attempt.status == "in_progress":
            from ..exam.engine import submit_attempt

            submit_attempt(db, attempt, auto=False)
            attempt = get_attempt_or_404(db, attempt.id)
    summary = violation_summary(db, attempt)
    return build_submit_response(attempt, summary)


@router.get("/attempts/{attempt_id}/result", response_model=ResultOut)
def exam_result(attempt_id: int, db: DbDep, user: CurrentUser):
    attempt = load_attempt_owner(db, attempt_id, user.id)
    if attempt.status == "in_progress":
        raise HTTPException(409, "This attempt has not been submitted yet.")

    summary = violation_summary(db, attempt)
    answered = sum(1 for eq in attempt.exam_questions if eq.chosen_options is not None)
    return ResultOut(
        attempt_id=attempt.id,
        subject_name=attempt.subject.name,
        status=attempt.status,
        num_questions=len(attempt.exam_questions),
        answered=answered,
        violations=summary,
        total_penalty=attempt.penalty_total,
        time_used_seconds=attempt.time_used_seconds or 0,
        score_hidden=True,
        subject_locked=True,
    )


@router.get("/attempts/{attempt_id}/recording")
def recording_status(attempt_id: int, db: DbDep, user: CurrentUser):
    attempt = load_attempt_owner(db, attempt_id, user.id)
    recording = db.scalar(select(Recording).where(Recording.attempt_id == attempt.id))
    if recording is None:
        return {"attempt_id": attempt.id, "status": "none"}
    return {
        "attempt_id": attempt.id,
        "status": recording.status,
        "mime_type": recording.mime_type,
        "segment_count": recording.segment_count,
        "duration_seconds": recording.duration_seconds,
    }
