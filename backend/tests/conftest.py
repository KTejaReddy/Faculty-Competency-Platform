"""Pytest fixtures: isolated temp DB (seeded once), TestClient."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

_TMP = tempfile.mkdtemp(prefix="ftp_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_TMP) / 'test.db'}"
os.environ["VIDEO_STORAGE_PATH"] = str(Path(_TMP) / "recordings")
os.environ["SECRET_KEY"] = "test-secret-key-0123456789abcdef0123456789abcdef"
os.environ["ADMIN_USERNAME"] = "ADMIN"
os.environ["ADMIN_PASSWORD"] = "admin123"

from fastapi.testclient import TestClient  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models.models import (  # noqa: E402
    ExamAttempt,
    Subject,
    Violation,
)


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def db():
    with SessionLocal() as session:
        yield session


def register_faculty(client: TestClient, name: str, dept: str = "COMPUTER SCIENCE AND ENGINEERING", password: str = "secret1234") -> dict:
    r = client.post(
        "/api/auth/register",
        json={
            "full_name": name,
            "department": dept,
            "password": password,
            "confirm_password": password,
        },
    )
    assert r.status_code == 201, r.text
    return r.json()


def faculty_token(client: TestClient, name: str, password: str = "secret1234") -> str:
    r = client.post(
        "/api/auth/login",
        json={"full_name": name, "password": password},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture
def admin_token(client):
    r = client.post("/api/auth/admin-login", json={"username": "ADMIN", "password": "admin123"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture
def first_subject_id(db):
    return db.query(Subject).order_by(Subject.id).first().id


def answer_all_correct(client, token, attempt_id, db, session=None):
    """Answer every question of an attempt with its actual correct option (DB access)."""
    from sqlalchemy import select

    s = session or db
    attempt = s.get(ExamAttempt, attempt_id)
    for eq in attempt.exam_questions:
        correct_display = [eq.option_order.index(ci) for ci in eq.question.correct_answer]
        r = client.post(
            f"/api/exams/attempts/{attempt_id}/answers",
            headers={"Authorization": f"Bearer {token}"},
            json={"position": eq.position, "chosen_options": correct_display},
        )
        assert r.status_code == 200, r.text
    return attempt


def violations_for_attempt(session, attempt_id: int) -> list[Violation]:
    from sqlalchemy import select

    return list(session.scalars(select(Violation).where(Violation.attempt_id == attempt_id)))
