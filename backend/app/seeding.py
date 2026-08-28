"""Idempotent database seeding.

Runs automatically on first startup and can be re-run manually:
    python -m app.seed [--force]
"""
from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models.models import (
    DEFAULT_EXPERIENCE_DISTRIBUTION,
    DEFAULT_VIOLATION_PENALTIES,
    Department,
    ExamConfig,
    ExperienceBandConfig,
    Question,
    Subject,
    Topic,
    User,
    ViolationPenalty,
    normalize_name,
)
from .security.passwords import hash_password
from .config import settings

logger = logging.getLogger("faculty-testing")

DEFAULT_DEPARTMENTS = [
    ("COMPUTER SCIENCE AND ENGINEERING", "CSE"),
    ("INFORMATION TECHNOLOGY", "IT"),
    ("ELECTRONICS AND COMMUNICATION ENGINEERING", "ECE"),
    ("ELECTRICAL AND ELECTRONICS ENGINEERING", "EEE"),
    ("MECHANICAL ENGINEERING", "MECH"),
    ("CIVIL ENGINEERING", "CIVIL"),
    ("ADMINISTRATION", "ADMIN"),
]

PENALTY_LABELS = {
    "TAB_SWITCH": "Tab Switch",
    "COPY_ATTEMPT": "Copy Attempt",
    "PASTE_ATTEMPT": "Paste Attempt",
    "CUT_ATTEMPT": "Cut Attempt",
    "FULLSCREEN_EXIT": "Fullscreen Exit",
    "CONTEXT_MENU": "Context Menu",
    "FOCUS_LOSS": "Focus Loss",
    "PRINT_ATTEMPT": "Print Attempt",
    "KEYBOARD_SHORTCUT": "Keyboard Shortcut",
    "CAMERA_OBSTRUCTED": "Camera Obstructed",
    "CAMERA_TOO_DARK": "Camera Too Dark",
    "CAMERA_TOO_BRIGHT": "Camera Too Bright",
    "CAMERA_DISCONNECTED": "Camera Disconnected",
    "CAMERA_PERMISSION_LOST": "Camera Permission Lost",
}

BAND_LABELS = {
    "1-3": "1–3 Years",
    "4-7": "4–7 Years",
    "8-12": "8–12 Years",
    "13-20": "13–20 Years",
    "20+": "20+ Years",
}


def seed_if_empty(db: Session) -> bool:
    """Seed reference data and the full question bank when the DB is empty."""
    if (db.scalar(select(func.count(Department.id))) or 0) > 0:
        return False
    seed_all(db)
    return True


def seed_all(db: Session, force: bool = False) -> None:
    if force or db.scalar(select(func.count(Department.id))) == 0:
        _seed_departments(db)
    if force or db.scalar(select(func.count(ViolationPenalty.id))) == 0:
        _seed_penalties(db)
    if force or db.scalar(select(func.count(ExperienceBandConfig.id))) == 0:
        _seed_band_configs(db)
    if force or db.scalar(select(func.count(User.id))) == 0:
        _seed_admin(db)
    if db.scalar(select(func.count(Subject.id))) == 0:
        _seed_question_bank(db)
    elif force:
        logger.info("Question bank already present; delete the database file to re-seed from scratch.")
    db.commit()
    logger.info("Seeding complete.")


def _seed_departments(db: Session) -> None:
    for name, code in DEFAULT_DEPARTMENTS:
        if db.scalar(select(Department).where(Department.code == code)) is None:
            db.add(Department(name=name, code=code))
    db.flush()


def _seed_penalties(db: Session) -> None:
    for vtype, penalty in DEFAULT_VIOLATION_PENALTIES.items():
        if db.scalar(select(ViolationPenalty).where(ViolationPenalty.type == vtype)) is None:
            db.add(
                ViolationPenalty(
                    type=vtype,
                    label=PENALTY_LABELS.get(vtype, vtype.title()),
                    penalty=penalty,
                    enabled=True,
                )
            )
    db.flush()


def _seed_band_configs(db: Session) -> None:
    for band, dist in DEFAULT_EXPERIENCE_DISTRIBUTION.items():
        if db.scalar(select(ExperienceBandConfig).where(ExperienceBandConfig.band == band)) is None:
            db.add(
                ExperienceBandConfig(
                    band=band,
                    hard_pct=dist["hard"],
                    very_hard_pct=dist["very_hard"],
                    expert_pct=dist["expert"],
                )
            )
    db.flush()


def _seed_admin(db: Session) -> None:
    admin_dept = db.scalar(select(Department).where(Department.code == "ADMIN"))
    if admin_dept is None:
        admin_dept = Department(name="ADMINISTRATION", code="ADMIN")
        db.add(admin_dept)
        db.flush()
    username = normalize_name(settings.admin_username) or "ADMIN"
    existing = db.scalar(select(User).where(User.full_name == username, User.role == "admin"))
    if existing is None:
        db.add(
            User(
                full_name=username,
                name_normalized=username,
                department_id=admin_dept.id,
                password_hash=hash_password(settings.admin_password),
                role="admin",
            )
        )
        logger.info("Admin account created: username=%s", username)
    db.flush()


def _seed_question_bank(db: Session) -> None:
    from .seed_data import QUESTION_BANK, SUBJECTS

    subjects_by_code: dict[str, Subject] = {}
    for meta in SUBJECTS:
        subject = Subject(
            name=meta["name"],
            code=meta["code"],
            description=meta.get("description", ""),
            difficulty_label="Expert Assessment",
        )
        db.add(subject)
        db.flush()
        db.add(ExamConfig(subject_id=subject.id, num_questions=16, duration_minutes=60))
        subjects_by_code[meta["code"]] = subject

    db.flush()

    topic_cache: dict[tuple[int, str], Topic] = {}
    for q in QUESTION_BANK:
        subject = subjects_by_code[q["subject"]]
        topic_key = (subject.id, q["topic"])
        if topic_key not in topic_cache:
            topic = Topic(subject_id=subject.id, name=q["topic"])
            db.add(topic)
            db.flush()
            topic_cache[topic_key] = topic

        db.add(
            Question(
                subject_id=subject.id,
                topic_id=topic_cache[topic_key].id,
                difficulty=q["difficulty"],
                experience_min=q.get("experience_min", 1),
                question_type=q["type"],
                question_text=q["text"],
                options=q["options"],
                correct_answer=q["answer"],
                explanation=q.get("explanation", ""),
                marks=1,
                active=True,
            )
        )
    db.flush()
    logger.info("Seeded %d questions across %d subjects.", len(QUESTION_BANK), len(subjects_by_code))
