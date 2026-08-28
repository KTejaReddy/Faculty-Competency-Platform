"""Admin endpoints: analytics, faculty management, exam reports, question bank, config."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from ..exam.engine import (
    build_submit_response,
    get_attempt_or_404,
    recording_meta,
    violation_summary,
)
from ..models.models import (
    DIFFICULTIES,
    EXPERIENCE_BANDS,
    QUESTION_TYPES,
    VIOLATION_TYPES,
    Department,
    ExamAttempt,
    ExamConfig,
    ExperienceBandConfig,
    Question,
    Recording,
    Subject,
    Topic,
    User,
    Violation,
    ViolationPenalty,
)
from ..schemas.schemas import (
    AdminExamReport,
    AdminStats,
    AttemptListItem,
    DepartmentCreate,
    DepartmentOut,
    ExamConfigOut,
    ExamConfigUpdate,
    ExperienceConfigOut,
    ExperienceConfigUpdate,
    FacultyListItem,
    QuestionAdminOut,
    QuestionBase,
    QuestionListOut,
    SubjectCreate,
    SubjectOut,
    TopicCreate,
    TopicOut,
    ViolationPenaltyOut,
    ViolationPenaltyUpdate,
)
from .deps import CurrentUser, DbDep, require_role

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[])
AdminUser = require_role("admin")


# ---------------------------------------------------------------------------
# Dashboard stats
# ---------------------------------------------------------------------------


@router.get("/stats", response_model=AdminStats)
def stats(user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    completed = db.scalar(
        select(func.count(ExamAttempt.id)).where(ExamAttempt.status.in_(["completed", "auto_submitted"]))
    )
    pending = db.scalar(
        select(func.count(ExamAttempt.id)).where(ExamAttempt.status == "in_progress")
    )
    return AdminStats(
        total_faculty=db.scalar(select(func.count(User.id)).where(User.role == "faculty")) or 0,
        exams_completed=completed or 0,
        exams_pending=pending or 0,
        total_subjects=db.scalar(select(func.count(Subject.id))) or 0,
        total_questions=db.scalar(select(func.count(Question.id))) or 0,
        total_violations=db.scalar(select(func.count(Violation.id))) or 0,
    )


@router.get("/faculty", response_model=list[FacultyListItem])
def list_faculty(user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    faculty = db.scalars(
        select(User).where(User.role == "faculty").order_by(User.full_name).options(selectinload(User.department))
    ).all()

    items = []
    for f in faculty:
        attempts = db.scalars(
            select(ExamAttempt).where(ExamAttempt.faculty_id == f.id)
        ).all()
        completed = [a for a in attempts if a.status in ("completed", "auto_submitted")]
        avg = (
            round(sum(a.final_score or 0 for a in completed) / len(completed), 1)
            if completed
            else 0.0
        )
        violations = db.scalar(
            select(func.count(Violation.id)).where(Violation.faculty_id == f.id)
        ) or 0
        items.append(
            FacultyListItem(
                id=f.id,
                full_name=f.full_name,
                department=f.department.name,
                subjects_completed=len(completed),
                average_score=avg,
                total_violations=violations,
                created_at=f.created_at,
            )
        )
    return items


@router.get("/attempts", response_model=list[AttemptListItem])
def list_attempts(
    subject_id: int | None = None,
    status: str | None = None,
    faculty_id: int | None = None,
    user: CurrentUser = None,
    db: DbDep = None,  # type: ignore[assignment]
):
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    stmt = select(ExamAttempt)
    if subject_id:
        stmt = stmt.where(ExamAttempt.subject_id == subject_id)
    if status:
        stmt = stmt.where(ExamAttempt.status == status)
    if faculty_id:
        stmt = stmt.where(ExamAttempt.faculty_id == faculty_id)
    stmt = stmt.order_by(ExamAttempt.start_time.desc())

    attempts = db.scalars(
        stmt.options(selectinload(ExamAttempt.faculty).selectinload(User.department), selectinload(ExamAttempt.subject))
    ).all()

    items = []
    for a in attempts:
        vcount = db.scalar(select(func.count(Violation.id)).where(Violation.attempt_id == a.id)) or 0
        items.append(
            AttemptListItem(
                id=a.id,
                faculty_name=a.faculty.full_name,
                department=a.faculty.department.name,
                subject_name=a.subject.name,
                experience_band=a.experience_band,
                status=a.status,
                started_at=a.start_time,
                submitted_at=a.submitted_at,
                time_used_seconds=a.time_used_seconds,
                raw_score=a.raw_score,
                penalty_total=a.penalty_total,
                final_score=a.final_score,
                violation_count=vcount,
            )
        )
    return items


# ---------------------------------------------------------------------------
# Exam report
# ---------------------------------------------------------------------------


@router.get("/attempts/{attempt_id}/report", response_model=AdminExamReport)
def exam_report(attempt_id: int, user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    attempt = get_attempt_or_404(db, attempt_id)

    questions = []
    for eq in attempt.exam_questions:
        q = eq.question
        shuffled = [q.options[i] for i in eq.option_order]
        # Map correct canonical indices -> display indices for the report
        correct_display = sorted(eq.option_order.index(ci) for ci in q.correct_answer)
        questions.append(
            {
                "position": eq.position,
                "question_type": q.question_type,
                "question_text": q.question_text,
                "difficulty": q.difficulty,
                "topic": q.topic.name if q.topic else "",
                "options": shuffled,
                "correct_options": correct_display,
                "chosen_options": eq.chosen_options or [],
                "is_correct": eq.is_correct if eq.is_correct is not None else False,
                "marks_awarded": eq.marks_awarded or 0.0,
                "explanation": q.explanation,
            }
        )

    violations = db.scalars(
        select(Violation).where(Violation.attempt_id == attempt.id).order_by(Violation.timestamp)
    ).all()
    summary = violation_summary(db, attempt)

    recording = db.scalar(select(Recording).where(Recording.attempt_id == attempt.id))
    cfg = db.scalar(select(ExamConfig).where(ExamConfig.subject_id == attempt.subject_id))

    answered = sum(1 for eq in attempt.exam_questions if eq.chosen_options is not None)
    correct = sum(1 for q in questions if q["is_correct"])

    return AdminExamReport(
        attempt_id=attempt.id,
        faculty_name=attempt.faculty.full_name,
        department=attempt.faculty.department.name,
        subject_name=attempt.subject.name,
        experience_band=attempt.experience_band,
        status=attempt.status,
        started_at=attempt.start_time,
        submitted_at=attempt.submitted_at,
        time_used_seconds=attempt.time_used_seconds,
        duration_minutes=cfg.duration_minutes if cfg else 60,
        num_questions=len(attempt.exam_questions),
        answered=answered,
        unanswered=len(attempt.exam_questions) - answered,
        correct=correct,
        incorrect=answered - correct,
        raw_score=attempt.raw_score or 0.0,
        penalty_total=attempt.penalty_total,
        final_score=attempt.final_score or 0.0,
        questions=questions,
        violations=[
            {
                "id": v.id,
                "type": v.type,
                "timestamp": v.timestamp,
                "duration_seconds": v.duration_seconds,
                "penalty": v.penalty,
                "details": v.details,
            }
            for v in violations
        ],
        violation_summary=summary,
        recording=recording_meta(recording),
    )


@router.get("/attempts/{attempt_id}/recording")
def attempt_recording(attempt_id: int, user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    recording = db.scalar(select(Recording).where(Recording.attempt_id == attempt_id))
    if recording is None:
        return {"attempt_id": attempt_id, "status": "none"}
    meta = recording_meta(recording)
    from .recordings import make_video_token

    meta["url"] = f"/api/recordings/admin/video/{attempt_id}?token={make_video_token(attempt_id)}"
    return meta


# ---------------------------------------------------------------------------
# Question bank
# ---------------------------------------------------------------------------


@router.get("/questions", response_model=QuestionListOut)
def list_questions(
    subject_id: int | None = None,
    topic_id: int | None = None,
    difficulty: str | None = None,
    experience_min: int | None = None,
    question_type: str | None = None,
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = None,
    db: DbDep = None,  # type: ignore[assignment]
):
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    stmt = select(Question)
    if subject_id:
        stmt = stmt.where(Question.subject_id == subject_id)
    if topic_id:
        stmt = stmt.where(Question.topic_id == topic_id)
    if difficulty:
        stmt = stmt.where(Question.difficulty == difficulty)
    if experience_min is not None:
        stmt = stmt.where(Question.experience_min <= experience_min)
    if question_type:
        stmt = stmt.where(Question.question_type == question_type)
    if q:
        stmt = stmt.where(Question.question_text.ilike(f"%{q}%"))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    questions = db.scalars(
        stmt.order_by(Question.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()

    items = []
    for question in questions:
        out = QuestionAdminOut.model_validate(question)
        out.subject_name = question.subject.name if question.subject else ""
        out.topic_name = question.topic.name if question.topic else ""
        items.append(out)
    return QuestionListOut(items=items, total=total)


def _validate_question(payload: QuestionBase, db: DbDep) -> None:
    if payload.difficulty not in DIFFICULTIES:
        raise HTTPException(400, f"Invalid difficulty. Must be one of {DIFFICULTIES}.")
    if payload.question_type not in QUESTION_TYPES:
        raise HTTPException(400, f"Invalid question type. Must be one of {QUESTION_TYPES}.")
    if db.get(Subject, payload.subject_id) is None:
        raise HTTPException(400, "Subject does not exist.")
    if db.get(Topic, payload.topic_id) is None:
        raise HTTPException(400, "Topic does not exist.")
    if not payload.correct_answer:
        raise HTTPException(400, "At least one correct option is required.")
    if not all(0 <= idx < len(payload.options) for idx in payload.correct_answer):
        raise HTTPException(400, "Correct answer index out of range.")


@router.post("/questions", response_model=QuestionAdminOut, status_code=201)
def create_question(payload: QuestionBase, user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    _validate_question(payload, db)
    question = Question(**payload.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    out = QuestionAdminOut.model_validate(question)
    out.subject_name = question.subject.name
    out.topic_name = question.topic.name
    return out


@router.put("/questions/{question_id}", response_model=QuestionAdminOut)
def update_question(question_id: int, payload: QuestionBase, user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    question = db.get(Question, question_id)
    if question is None:
        raise HTTPException(404, "Question not found")
    _validate_question(payload, db)
    for key, value in payload.model_dump().items():
        setattr(question, key, value)
    db.commit()
    db.refresh(question)
    out = QuestionAdminOut.model_validate(question)
    out.subject_name = question.subject.name
    out.topic_name = question.topic.name
    return out


@router.delete("/questions/{question_id}")
def delete_question(question_id: int, user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    question = db.get(Question, question_id)
    if question is None:
        raise HTTPException(404, "Question not found")
    db.delete(question)
    db.commit()
    return {"ok": True}


# ---------------------------------------------------------------------------
# Subjects / topics / departments
# ---------------------------------------------------------------------------


@router.get("/subjects", response_model=list[SubjectOut])
def list_subjects_admin(user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    return db.scalars(select(Subject).order_by(Subject.name)).all()


@router.post("/subjects", response_model=SubjectOut, status_code=201)
def create_subject(payload: SubjectCreate, user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    if db.scalar(select(Subject).where(Subject.code == payload.code)) is not None:
        raise HTTPException(409, "Subject code already exists.")
    subject = Subject(
        name=payload.name,
        code=payload.code,
        description=payload.description,
        difficulty_label=payload.difficulty_label,
    )
    db.add(subject)
    db.flush()
    db.add(ExamConfig(subject_id=subject.id, num_questions=40, duration_minutes=60))
    db.commit()
    db.refresh(subject)
    return subject


@router.put("/subjects/{subject_id}", response_model=SubjectOut)
def update_subject(subject_id: int, payload: SubjectCreate, user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    subject = db.get(Subject, subject_id)
    if subject is None:
        raise HTTPException(404, "Subject not found")
    subject.name = payload.name
    subject.description = payload.description
    subject.difficulty_label = payload.difficulty_label
    db.commit()
    db.refresh(subject)
    return subject


@router.get("/subjects/{subject_id}/topics", response_model=list[TopicOut])
def list_topics(subject_id: int, user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    return db.scalars(select(Topic).where(Topic.subject_id == subject_id).order_by(Topic.name)).all()


@router.post("/topics", response_model=TopicOut, status_code=201)
def create_topic(payload: TopicCreate, subject_id: int = Query(...), user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    if db.get(Subject, subject_id) is None:
        raise HTTPException(400, "Subject does not exist.")
    topic = Topic(subject_id=subject_id, name=payload.name)
    db.add(topic)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(409, "Topic already exists for this subject.")
    db.refresh(topic)
    return topic


@router.get("/departments", response_model=list[DepartmentOut])
def list_departments(user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    return db.scalars(select(Department).order_by(Department.name)).all()


@router.post("/departments", response_model=DepartmentOut, status_code=201)
def create_department(payload: DepartmentCreate, user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    if db.scalar(select(Department).where(Department.code == payload.code)) is not None:
        raise HTTPException(409, "Department code already exists.")
    department = Department(name=payload.name, code=payload.code.upper())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


# ---------------------------------------------------------------------------
# Configuration: exam configs, experience distributions, violation penalties
# ---------------------------------------------------------------------------


@router.get("/exam-configs", response_model=list[ExamConfigOut])
def list_exam_configs(user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    return db.scalars(select(ExamConfig).order_by(ExamConfig.id)).all()


@router.put("/exam-configs/{config_id}", response_model=ExamConfigOut)
def update_exam_config(config_id: int, payload: ExamConfigUpdate, user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    config = db.get(ExamConfig, config_id)
    if config is None:
        raise HTTPException(404, "Exam config not found")
    config.num_questions = payload.num_questions
    config.duration_minutes = payload.duration_minutes
    config.active = payload.active
    db.commit()
    db.refresh(config)
    return config


@router.get("/experience-configs", response_model=list[ExperienceConfigOut])
def list_experience_configs(user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    return db.scalars(select(ExperienceBandConfig).order_by(ExperienceBandConfig.id)).all()


@router.put("/experience-configs/{config_id}", response_model=ExperienceConfigOut)
def update_experience_config(config_id: int, payload: ExperienceConfigUpdate, user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    total = payload.hard_pct + payload.very_hard_pct + payload.expert_pct
    if total != 100:
        raise HTTPException(400, "Difficulty percentages must sum to 100.")
    config = db.get(ExperienceBandConfig, config_id)
    if config is None:
        raise HTTPException(404, "Experience config not found")
    config.hard_pct = payload.hard_pct
    config.very_hard_pct = payload.very_hard_pct
    config.expert_pct = payload.expert_pct
    db.commit()
    db.refresh(config)
    return config


@router.get("/penalties", response_model=list[ViolationPenaltyOut])
def list_penalties(user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    return db.scalars(select(ViolationPenalty).order_by(ViolationPenalty.id)).all()


@router.put("/penalties/{penalty_id}", response_model=ViolationPenaltyOut)
def update_penalty(penalty_id: int, payload: ViolationPenaltyUpdate, user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    penalty = db.get(ViolationPenalty, penalty_id)
    if penalty is None:
        raise HTTPException(404, "Penalty not found")
    penalty.penalty = payload.penalty
    penalty.description = payload.description
    penalty.enabled = payload.enabled
    db.commit()
    db.refresh(penalty)
    return penalty


@router.get("/meta")
def admin_meta(user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    return {
        "difficulties": DIFFICULTIES,
        "question_types": QUESTION_TYPES,
        "experience_bands": EXPERIENCE_BANDS,
        "violation_types": VIOLATION_TYPES,
    }


@router.get("/analytics")
def analytics(user: CurrentUser = None, db: DbDep = None):  # type: ignore[assignment]
    """Aggregates for the admin dashboard charts."""
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")

    completed = db.scalars(
        select(ExamAttempt).where(ExamAttempt.status.in_(["completed", "auto_submitted"]))
    ).all()
    all_attempts = db.scalars(select(ExamAttempt)).all()

    # Average final score per subject
    by_subject: dict[str, list[float]] = {}
    for a in completed:
        by_subject.setdefault(a.subject.name, []).append(a.final_score or 0)
    subject_performance = [
        {"subject": name, "avg_score": round(sum(v) / len(v), 1), "attempts": len(v)}
        for name, v in sorted(by_subject.items())
    ]

    # Violation distribution by type
    vrows = db.execute(
        select(Violation.type, func.count(Violation.id)).group_by(Violation.type)
    ).all()
    violation_distribution = [{"type": t, "count": c} for t, c in vrows]

    completion_rate = round(
        (len(completed) / len(all_attempts) * 100) if all_attempts else 0, 1
    )
    avg_score = (
        round(sum(a.final_score or 0 for a in completed) / len(completed), 1) if completed else 0.0
    )

    return {
        "subject_performance": subject_performance,
        "violation_distribution": violation_distribution,
        "completion_rate": completion_rate,
        "average_score": avg_score,
    }
