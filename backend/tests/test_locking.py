"""Subject locking and authorization tests."""
from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy import select

from app.exam.engine import now_utc
from app.models.models import ExamAttempt, Recording
from .conftest import answer_all_correct, register_faculty


def unique_name() -> str:
    return f"LOCKED USER {uuid.uuid4().hex[:8].upper()}"


def start_exam(client, token, subject_id):
    r = client.post(
        "/api/exams/start",
        headers={"Authorization": f"Bearer {token}"},
        json={"subject_id": subject_id, "experience_band": "8-12"},
    )
    assert r.status_code == 200
    return r.json()


class TestLocking:
    def test_completed_subject_locked(self, client, db, first_subject_id):
        token = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]
        answer_all_correct(client, token, aid, db)
        client.post(f"/api/exams/attempts/{aid}/submit", headers={"Authorization": f"Bearer {token}"})

        r = client.post(
            "/api/exams/start",
            headers={"Authorization": f"Bearer {token}"},
            json={"subject_id": first_subject_id, "experience_band": "8-12"},
        )
        assert r.status_code == 409
        assert "locked" in r.json()["detail"].lower()

    def test_auto_submitted_subject_locked(self, client, db, first_subject_id):
        token = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        a = db.get(ExamAttempt, aid)
        a.deadline = now_utc() - timedelta(seconds=1)
        db.commit()

        client.post(f"/api/exams/attempts/{aid}/submit", headers={"Authorization": f"Bearer {token}"})
        r = client.post(
            "/api/exams/start",
            headers={"Authorization": f"Bearer {token}"},
            json={"subject_id": first_subject_id, "experience_band": "8-12"},
        )
        assert r.status_code == 409

    def test_dashboard_shows_completed_status(self, client, db, first_subject_id):
        token = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        answer_all_correct(client, token, attempt["attempt_id"], db)
        client.post(
            f"/api/exams/attempts/{attempt['attempt_id']}/submit",
            headers={"Authorization": f"Bearer {token}"},
        )
        r = client.get("/api/subjects", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        entry = next(s for s in r.json() if s["subject"]["id"] == first_subject_id)
        assert entry["status"] == "COMPLETED"

    def test_database_constraint_prevents_duplicate_completed_attempts(self, db, first_subject_id):
        """The partial unique index blocks a second completed row even bypassing the API."""
        from app.models.models import User, utcnow

        user = db.scalar(select(User).where(User.role == "faculty"))
        now = utcnow()
        db.add(
            ExamAttempt(
                faculty_id=user.id,
                subject_id=first_subject_id,
                experience_band="8-12",
                status="completed",
                start_time=now,
                deadline=now + timedelta(minutes=60),
                submitted_at=now,
            )
        )
        db.flush()
        db.add(
            ExamAttempt(
                faculty_id=user.id,
                subject_id=first_subject_id,
                experience_band="8-12",
                status="completed",
                start_time=now,
                deadline=now + timedelta(minutes=60),
                submitted_at=now,
            )
        )
        from sqlalchemy.exc import IntegrityError

        try:
            db.commit()
            raise AssertionError("Expected IntegrityError for duplicate completed attempt")
        except IntegrityError:
            db.rollback()


class TestAuthorization:
    def test_faculty_cannot_access_admin_stats(self, client, first_subject_id):
        token = register_faculty(client, unique_name())["access_token"]
        r = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 403

    def test_faculty_cannot_view_other_faculty_attempt(self, client, db, first_subject_id):
        token_a = register_faculty(client, unique_name())["access_token"]
        token_b = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token_a, first_subject_id)
        aid = attempt["attempt_id"]

        for path in (f"/api/exams/attempts/{aid}/status", f"/api/exams/attempts/{aid}/result"):
            r = client.get(path, headers={"Authorization": f"Bearer {token_b}"})
            assert r.status_code == 403

        r = client.post(
            f"/api/exams/attempts/{aid}/submit",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r.status_code == 403

    def test_faculty_cannot_read_correct_answers(self, client, db, first_subject_id):
        from sqlalchemy import select

        from app.models.models import ExamQuestion

        token = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        qids = db.scalars(
            select(ExamQuestion.question_id).where(ExamQuestion.attempt_id == aid)
        ).all()
        # the question-bank admin endpoint is admin-only
        r = client.get("/api/admin/questions", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 403

        # the exam payload must not include answers
        assert all("correct_answer" not in q for q in attempt["questions"])
        assert all("explanation" not in q for q in attempt["questions"])

    def test_faculty_result_hides_score(self, client, db, first_subject_id):
        token = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]
        answer_all_correct(client, token, aid, db)
        client.post(f"/api/exams/attempts/{aid}/submit", headers={"Authorization": f"Bearer {token}"})

        r = client.get(f"/api/exams/attempts/{aid}/result", headers={"Authorization": f"Bearer {token}"})
        body = r.json()
        assert body["score_hidden"] is True
        assert "raw_score" not in body
        assert "final_score" not in body
        assert body["subject_locked"] is True

    def test_faculty_cannot_access_recording_video(self, client, db, first_subject_id):
        token = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        r = client.get(
            f"/api/recordings/admin/video/{attempt['attempt_id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code in (401, 403, 404)

    def test_admin_can_read_full_report(self, client, db, first_subject_id, admin_token):
        token = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]
        answer_all_correct(client, token, aid, db)
        client.post(f"/api/exams/attempts/{aid}/submit", headers={"Authorization": f"Bearer {token}"})

        r = client.get(f"/api/admin/attempts/{aid}/report", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        body = r.json()
        assert body["raw_score"] >= 0
        assert body["final_score"] >= 0
        assert len(body["questions"]) == body["num_questions"]
        # every question in the report carries its correct options and explanation
        for q in body["questions"]:
            assert "correct_options" in q
            assert "explanation" in q

    def test_admin_attempt_list_loads(self, client, db, first_subject_id, admin_token):
        """Regression: the admin attempt list (faculty history) must not 500."""
        data = register_faculty(client, unique_name())
        token = data["access_token"]
        faculty_id = data["user"]["id"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]
        answer_all_correct(client, token, aid, db)
        client.post(f"/api/exams/attempts/{aid}/submit", headers={"Authorization": f"Bearer {token}"})

        # unfiltered list
        r = client.get("/api/admin/attempts", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, list)
        assert any(a["id"] == aid for a in body)
        first = body[0]
        for key in ("faculty_name", "subject_name", "status", "started_at"):
            assert key in first

        # faculty-filtered list (what the faculty history page calls)
        r = client.get(
            f"/api/admin/attempts?faculty_id={faculty_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert r.status_code == 200
        filtered = r.json()
        assert isinstance(filtered, list)
        assert all(a["id"] == aid for a in filtered)
