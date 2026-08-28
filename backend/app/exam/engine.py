"""Core exam engine.

- Question selection honors the experience band's difficulty distribution.
- Question order and option order are randomized server-side.
- Correct answers NEVER leave the server (options are sent shuffled; the
  server stores the remapping and evaluates submitted display indices).
- Scoring, penalties, deadlines and subject locking are all server-side.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..models.models import (
    DIFFICULTIES as EXAM_DIFFICULTIES,
    ExamAttempt,
    ExamConfig,
    ExamQuestion,
    ExperienceBandConfig,
    Question,
    Recording,
    Violation,
    ViolationPenalty,
    utcnow,
)


def now_utc() -> datetime:
    """Naive UTC now, matching how datetimes are stored/compared."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ---------------------------------------------------------------------------
# Attempt lifecycle helpers
# ---------------------------------------------------------------------------


def get_attempt_or_404(db: Session, attempt_id: int) -> ExamAttempt:
    attempt = db.scalar(
        select(ExamAttempt)
        .where(ExamAttempt.id == attempt_id)
        .options(
            selectinload(ExamAttempt.exam_questions).selectinload(ExamQuestion.question),
            selectinload(ExamAttempt.violations),
            selectinload(ExamAttempt.subject),
        )
    )
    if attempt is None:
        raise HTTPException(404, "Exam attempt not found")
    return attempt


def load_attempt_owner(db: Session, attempt_id: int, faculty_id: int) -> ExamAttempt:
    attempt = get_attempt_or_404(db, attempt_id)
    if attempt.faculty_id != faculty_id:
        raise HTTPException(403, "This attempt does not belong to you")
    return attempt


def is_expired(attempt: ExamAttempt) -> bool:
    return now_utc() > attempt.deadline


def auto_submit_if_expired(db: Session, attempt: ExamAttempt) -> ExamAttempt:
    """Lazily auto-submit an in-progress attempt whose deadline has passed."""
    if attempt.status == "in_progress" and is_expired(attempt):
        submit_attempt(db, attempt, auto=True)
        db.commit()
        db.refresh(attempt)
    return attempt


def get_band_years_max(band: str) -> int:
    return {"1-3": 3, "4-7": 7, "8-12": 12, "13-20": 20, "20+": 99}.get(band, 99)


def band_distribution(db: Session, band: str) -> dict[str, int]:
    cfg = db.scalar(select(ExperienceBandConfig).where(ExperienceBandConfig.band == band))
    if cfg is not None:
        return {"hard": cfg.hard_pct, "very_hard": cfg.very_hard_pct, "expert": cfg.expert_pct}
    return {"hard": 30, "very_hard": 40, "expert": 30}


# ---------------------------------------------------------------------------
# Question selection
# ---------------------------------------------------------------------------


def select_questions(db: Session, subject_id: int, band: str, num_questions: int) -> list[Question]:
    """Pick `num_questions` distinct, active questions for the subject.

    Eligibility: question.experience_min must be within the band's year range.
    Distribution: the band's difficulty percentages are applied; if a
    difficulty bucket runs out of eligible questions the remainder is filled
    from other difficulties so an exam can still be generated.
    """
    max_years = get_band_years_max(band)
    eligible = db.scalars(
        select(Question).where(
            Question.subject_id == subject_id,
            Question.active.is_(True),
            Question.experience_min <= max_years,
        )
    ).all()

    all_pool = db.scalars(
        select(Question).where(
            Question.subject_id == subject_id, Question.active.is_(True)
        )
    ).all()

    if len(all_pool) < num_questions:
        raise HTTPException(
            409,
            f"Not enough questions in the bank for this subject "
            f"({len(all_pool)} available, {num_questions} required). ",
        )
    # If the band-eligible pool alone is too small, top it up from the full
    # subject pool so every experience band can always start an exam.
    if len(eligible) < num_questions:
        used = {q.id for q in eligible}
        eligible = eligible + [q for q in all_pool if q.id not in used]

    dist = band_distribution(db, band)
    by_diff: dict[str, list[Question]] = {d: [] for d in EXAM_DIFFICULTIES}
    for q in eligible:
        by_diff.setdefault(q.difficulty, []).append(q)

    picked: list[Question] = []
    quotas = {
        "hard": round(num_questions * dist["hard"] / 100),
        "very_hard": round(num_questions * dist["very_hard"] / 100),
        "expert": round(num_questions * dist["expert"] / 100),
    }
    # Fix rounding drift so quotas sum to num_questions
    diff_sum = quotas["hard"] + quotas["very_hard"] + quotas["expert"]
    quotas["expert"] += num_questions - diff_sum

    for diff in EXAM_DIFFICULTIES:
        pool = by_diff.get(diff, [])
        random.shuffle(pool)
        take = min(quotas[diff], len(pool))
        picked.extend(pool[:take])

    # Top up any shortfall from the remaining eligible pool
    if len(picked) < num_questions:
        used_ids = {q.id for q in picked}
        remaining = [q for q in eligible if q.id not in used_ids]
        random.shuffle(remaining)
        picked.extend(remaining[: num_questions - len(picked)])

    random.shuffle(picked)
    return picked[:num_questions]


def build_exam_payload(attempt: ExamAttempt) -> list[dict[str, Any]]:
    """Serialize an attempt's questions for the faculty UI (no answers)."""
    payload = []
    for eq in attempt.exam_questions:
        q = eq.question
        shuffled_options = [q.options[i] for i in eq.option_order]
        payload.append(
            {
                "position": eq.position,
                "question_type": q.question_type,
                "question_text": q.question_text,
                "options": shuffled_options,
                "marks": q.marks,
            }
        )
    return payload


def start_attempt(db: Session, faculty_id: int, subject_id: int, band: str) -> ExamAttempt:
    """Create a new attempt. Enforces subject locking on the backend/database."""
    config = db.scalar(select(ExamConfig).where(ExamConfig.subject_id == subject_id))
    if config is None or not config.active:
        raise HTTPException(400, "This subject has no active exam configuration.")
    num_questions = config.num_questions
    duration_minutes = config.duration_minutes

    # Backend lock check: no second completed attempt for (faculty, subject)
    completed = db.scalar(
        select(ExamAttempt).where(
            ExamAttempt.faculty_id == faculty_id,
            ExamAttempt.subject_id == subject_id,
            ExamAttempt.status.in_(["completed", "auto_submitted"]),
        )
    )
    if completed is not None:
        raise HTTPException(409, "This subject has already been completed and is permanently locked.")

    # Resume an existing in-progress (unexpired) attempt
    in_progress = db.scalar(
        select(ExamAttempt).where(
            ExamAttempt.faculty_id == faculty_id,
            ExamAttempt.subject_id == subject_id,
            ExamAttempt.status == "in_progress",
        )
    )
    if in_progress is not None and not is_expired(in_progress):
        return in_progress

    questions = select_questions(db, subject_id, band, num_questions)

    attempt = ExamAttempt(
        faculty_id=faculty_id,
        subject_id=subject_id,
        experience_band=band,
        status="in_progress",
        start_time=utcnow(),
        deadline=utcnow() + timedelta(minutes=duration_minutes),
    )
    db.add(attempt)
    db.flush()

    for position, question in enumerate(questions, start=1):
        option_order = list(range(len(question.options)))
        random.shuffle(option_order)
        db.add(
            ExamQuestion(
                attempt_id=attempt.id,
                question_id=question.id,
                position=position,
                option_order=option_order,
            )
        )
    db.commit()
    db.refresh(attempt)
    return get_attempt_or_404(db, attempt.id)


# ---------------------------------------------------------------------------
# Answers
# ---------------------------------------------------------------------------


def last_position(attempt: ExamAttempt) -> int:
    positions = [eq.position for eq in attempt.exam_questions if eq.chosen_options is not None]
    return max(positions) if positions else 0


def save_answer(db: Session, attempt: ExamAttempt, position: int, chosen: list[int]) -> None:
    if attempt.status != "in_progress":
        raise HTTPException(409, "This attempt is no longer in progress.")

    current_last = last_position(attempt)
    if position < current_last:
        raise HTTPException(400, "You cannot return to a previous question.")
    # Forward movement is allowed (including skips — questions may be left
    # unanswered); only navigating backwards is forbidden.

    eq = next((e for e in attempt.exam_questions if e.position == position), None)
    if eq is None:
        raise HTTPException(400, "Invalid question position.")

    valid_indices = set(range(len(eq.question.options)))
    if not set(chosen).issubset(valid_indices):
        raise HTTPException(400, "Invalid option index.")

    eq.chosen_options = chosen
    eq.answered_at = utcnow()
    db.commit()


# ---------------------------------------------------------------------------
# Violations
# ---------------------------------------------------------------------------


def record_violation(
    db: Session, attempt: ExamAttempt, vtype: str, duration: float = 0.0, metadata: dict | None = None
) -> Violation:
    penalty_cfg = db.scalar(select(ViolationPenalty).where(ViolationPenalty.type == vtype))
    if penalty_cfg is None or not penalty_cfg.enabled:
        penalty = 0.0
    else:
        penalty = penalty_cfg.penalty

    violation = Violation(
        attempt_id=attempt.id,
        faculty_id=attempt.faculty_id,
        type=vtype,
        duration_seconds=duration,
        details=metadata or {},
        penalty=penalty,
    )
    db.add(violation)
    db.flush()

    attempt.penalty_total = round(attempt.penalty_total + penalty, 2)
    db.commit()
    db.refresh(violation)
    return violation


def violation_summary(db: Session, attempt: ExamAttempt) -> list[dict[str, Any]]:
    rows = db.execute(
        select(Violation.type, func.count(Violation.id), func.max(Violation.penalty))
        .where(Violation.attempt_id == attempt.id)
        .group_by(Violation.type)
    ).all()
    summary = []
    for vtype, count, per in rows:
        summary.append(
            {
                "type": vtype,
                "count": count,
                "penalty_per": per if per is not None else 0.0,
                "total_penalty": round((per if per is not None else 0.0) * count, 2),
            }
        )
    return summary


# ---------------------------------------------------------------------------
# Scoring / submission
# ---------------------------------------------------------------------------


def evaluate_answers(attempt: ExamAttempt) -> tuple[float, int, int, int]:
    """Return (raw_score, answered, correct, incorrect)."""
    raw = 0.0
    answered = 0
    correct = 0
    incorrect = 0
    for eq in attempt.exam_questions:
        if eq.chosen_options is None:
            continue
        answered += 1
        # Map display indices back to canonical indices using the stored order
        original = [eq.option_order[i] for i in eq.chosen_options]
        if set(original) == set(eq.question.correct_answer):
            raw += eq.question.marks
            eq.is_correct = True
            eq.marks_awarded = float(eq.question.marks)
            correct += 1
        else:
            eq.is_correct = False
            eq.marks_awarded = 0.0
            incorrect += 1
    return raw, answered, correct, incorrect


def submit_attempt(db: Session, attempt: ExamAttempt, auto: bool = False) -> ExamAttempt:
    """Compute the final result server-side and lock the subject."""
    if attempt.status in ("completed", "auto_submitted"):
        raise HTTPException(409, "This attempt has already been submitted.")

    now = now_utc()
    raw, answered, correct, incorrect = evaluate_answers(attempt)

    penalty = round(attempt.penalty_total, 2)  # penalties are negative values
    final = max(0.0, round(raw + penalty, 2))  # raw - |penalty|, never below zero

    attempt.status = "auto_submitted" if auto else "completed"
    attempt.submitted_at = now
    attempt.time_used_seconds = max(0, int((now - attempt.start_time).total_seconds()))
    attempt.raw_score = round(raw, 2)
    attempt.penalty_total = penalty
    attempt.final_score = final

    db.commit()
    db.refresh(attempt)
    return attempt


def build_submit_response(attempt: ExamAttempt, summary: list[dict[str, Any]]) -> dict[str, Any]:
    answered = sum(1 for eq in attempt.exam_questions if eq.chosen_options is not None)
    return {
        "attempt_id": attempt.id,
        "status": attempt.status,
        "subject_id": attempt.subject_id,
        "num_questions": len(attempt.exam_questions),
        "answered": answered,
        "violations": summary,
        "total_penalty": attempt.penalty_total,
        "time_used_seconds": attempt.time_used_seconds or 0,
        "score_hidden": True,
        "subject_locked": True,
    }


def recording_meta(recording: Recording | None) -> dict[str, Any] | None:
    if recording is None:
        return None
    return {
        "attempt_id": recording.attempt_id,
        "status": recording.status,
        "mime_type": recording.mime_type,
        "segment_count": recording.segment_count,
        "duration_seconds": recording.duration_seconds,
        "started_at": recording.started_at,
        "ended_at": recording.ended_at,
        "url": f"/admin/recordings/{recording.attempt_id}/video",
    }
