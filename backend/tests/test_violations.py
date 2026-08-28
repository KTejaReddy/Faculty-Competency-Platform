"""Violation recording and penalty tests."""
from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.models import ExamAttempt, Violation, ViolationPenalty
from .conftest import register_faculty, violations_for_attempt

PASSWORD = "secret1234"


def unique_name() -> str:
    return f"VIOLATOR {uuid.uuid4().hex[:8].upper()}"


def start_exam(client, token, subject_id):
    r = client.post(
        "/api/exams/start",
        headers={"Authorization": f"Bearer {token}"},
        json={"subject_id": subject_id, "experience_band": "8-12"},
    )
    assert r.status_code == 200
    return r.json()


class TestViolations:
    def test_all_violation_types_accepted(self, client, db, first_subject_id):
        from app.models.models import VIOLATION_TYPES

        token = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        for vtype in VIOLATION_TYPES:
            r = client.post(
                f"/api/exams/attempts/{aid}/violations",
                headers={"Authorization": f"Bearer {token}"},
                json={"type": vtype, "duration_seconds": 1.5, "metadata": {"detail": "test"}},
            )
            assert r.status_code == 200, f"{vtype}: {r.text}"

        rows = violations_for_attempt(db, aid)
        assert len(rows) == len(VIOLATION_TYPES)
        assert all(v.duration_seconds == 1.5 for v in rows)

    def test_unknown_violation_type_rejected(self, client, first_subject_id):
        token = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        r = client.post(
            f"/api/exams/attempts/{attempt['attempt_id']}/violations",
            headers={"Authorization": f"Bearer {token}"},
            json={"type": "NOT_A_REAL_VIOLATION"},
        )
        assert r.status_code == 400

    def test_penalties_applied_from_config(self, client, db, first_subject_id):
        token = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        cases = [("TAB_SWITCH", -1.0), ("COPY_ATTEMPT", -1.0), ("FULLSCREEN_EXIT", -1.0), ("FOCUS_LOSS", -0.5)]
        expected = 0.0
        for vtype, pen in cases:
            cfg = db.scalar(select(ViolationPenalty).where(ViolationPenalty.type == vtype))
            assert cfg.penalty == pen
            r = client.post(
                f"/api/exams/attempts/{aid}/violations",
                headers={"Authorization": f"Bearer {token}"},
                json={"type": vtype},
            )
            expected += pen
            assert r.json()["penalty_total"] == expected

        a = db.get(ExamAttempt, aid)
        assert a.penalty_total == -3.5

    def test_violation_requires_owner(self, client, db, first_subject_id):
        token_a = register_faculty(client, unique_name())["access_token"]
        token_b = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token_a, first_subject_id)
        r = client.post(
            f"/api/exams/attempts/{attempt['attempt_id']}/violations",
            headers={"Authorization": f"Bearer {token_b}"},
            json={"type": "TAB_SWITCH"},
        )
        assert r.status_code == 403


class TestPenaltyConfig:
    def test_admin_can_update_penalty(self, client, db, admin_token):
        cfg = db.scalar(select(ViolationPenalty).where(ViolationPenalty.type == "TAB_SWITCH"))
        r = client.put(
            f"/api/admin/penalties/{cfg.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"penalty": -2.0, "description": "stricter", "enabled": True},
        )
        assert r.status_code == 200
        assert r.json()["penalty"] == -2.0

        # restore
        client.put(
            f"/api/admin/penalties/{cfg.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"penalty": -1.0, "description": "", "enabled": True},
        )

    def test_faculty_cannot_update_penalty(self, client, db, first_subject_id):
        token = register_faculty(client, unique_name())["access_token"]
        cfg = db.scalar(select(ViolationPenalty).where(ViolationPenalty.type == "TAB_SWITCH"))
        r = client.put(
            f"/api/admin/penalties/{cfg.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"penalty": -1.0, "description": "", "enabled": True},
        )
        assert r.status_code == 403
