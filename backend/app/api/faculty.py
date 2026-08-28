"""Faculty-facing endpoints: dashboard subject statuses, profile."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models.models import (
    ExamAttempt,
    ExamConfig,
    Subject,
    User,
)
from ..schemas.schemas import SubjectStatusOut, UserOut
from .deps import CurrentUser, DbDep

router = APIRouter(tags=["faculty"])


@router.get("/departments")
def public_departments(db: DbDep):
    """Public department list for the registration/login forms."""
    from ..models.models import Department

    from ..schemas.schemas import DepartmentOut

    departments = db.scalars(select(Department).order_by(Department.name)).all()
    return [DepartmentOut.model_validate(d) for d in departments if d.code != "ADMIN"]


@router.get("/subjects", response_model=list[SubjectStatusOut])
def list_subjects(user: CurrentUser, db: DbDep):
    """All active subjects with the faculty's status for each."""
    subjects = db.scalars(
        select(Subject).where(Subject.active.is_(True)).options(selectinload(Subject.questions))
    ).all()
    configs = {c.subject_id: c for c in db.scalars(select(ExamConfig)).all()}
    attempts = db.scalars(
        select(ExamAttempt).where(ExamAttempt.faculty_id == user.id)
    ).all()

    status_by_subject: dict[int, tuple[str, int | None]] = {}
    for a in attempts:
        if a.status == "in_progress":
            status_by_subject.setdefault(a.subject_id, ("IN_PROGRESS", a.id))
        else:  # completed / auto_submitted
            status_by_subject[a.subject_id] = ("COMPLETED", a.id)

    result = []
    for s in subjects:
        cfg = configs.get(s.id)
        if cfg is None:
            continue
        status, attempt_id = status_by_subject.get(s.id, ("AVAILABLE", None))
        from ..schemas.schemas import SubjectOut

        result.append(
            SubjectStatusOut(
                subject=SubjectOut.model_validate(s),
                status=status,
                attempt_id=attempt_id,
                total_questions=len(s.questions),
                duration_minutes=cfg.duration_minutes,
                question_count=cfg.num_questions,
            )
        )
    return result


@router.get("/profile", response_model=UserOut)
def profile(user: CurrentUser):
    return UserOut(id=user.id, full_name=user.full_name, department=user.department.name, role=user.role)


@router.get("/faculty/{user_id}")
def get_faculty(user_id: int, db: DbDep, user: CurrentUser):
    if user.role != "admin":
        raise HTTPException(403, "Insufficient permissions")
    target = db.get(User, user_id)
    if target is None or target.role != "faculty":
        raise HTTPException(404, "Faculty not found")
    return UserOut(id=target.id, full_name=target.full_name, department=target.department.name, role=target.role)
