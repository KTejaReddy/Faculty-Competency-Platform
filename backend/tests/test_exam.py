"""Exam engine tests."""
from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy import select

from app.models.models import ExamAttempt, ExamConfig, ExamQuestion
from .conftest import answer_all_correct, faculty_token, register_faculty

PASSWORD = "secret1234"


def unique_name() -> str:
    return f"EXAM TAKER {uuid.uuid4().hex[:8].upper()}"


def start_exam(client, token, subject_id, band="8-12"):
    r = client.post(
        "/api/exams/start",
        headers={"Authorization": f"Bearer {token}"},
        json={"subject_id": subject_id, "experience_band": band},
    )
    assert r.status_code == 200, r.text
    return r.json()


class TestExamStart:
    def test_exactly_config_question_count_and_one_mark(self, client, db, first_subject_id):
        name = unique_name()
        token = register_faculty(client, name)["access_token"]
        data = start_exam(client, token, first_subject_id)

        cfg = db.scalar(select(ExamConfig).where(ExamConfig.subject_id == first_subject_id))
        assert data["num_questions"] == cfg.num_questions
        assert len(data["questions"]) == cfg.num_questions

        # 1 mark each, no answer leakage
        for q in data["questions"]:
            assert q["marks"] == 1
            assert "correct_answer" not in q
            assert "explanation" not in q
            assert len(q["options"]) >= 2

        # questions are unique within the attempt
        qids = db.scalars(
            select(ExamQuestion.question_id).where(
                ExamQuestion.attempt_id == data["attempt_id"]
            )
        ).all()
        assert len(qids) == len(set(qids))

    def test_deadline_is_60_minutes_ahead(self, client, db, first_subject_id):
        name = unique_name()
        token = register_faculty(client, name)["access_token"]
        data = start_exam(client, token, first_subject_id)
        from datetime import datetime

        deadline = datetime.fromisoformat(data["deadline"])
        server = datetime.fromisoformat(data["server_time"])
        minutes = (deadline - server).total_seconds() / 60
        assert 59.9 <= minutes <= 60.0  # deadline = start + 60min; server_time captured after

    def test_question_order_and_option_order_randomized(self, client, db, first_subject_id):
        name_a, name_b = unique_name(), unique_name()
        token_a = register_faculty(client, name_a)["access_token"]
        token_b = register_faculty(client, name_b)["access_token"]

        a = start_exam(client, token_a, first_subject_id)
        b = start_exam(client, token_b, first_subject_id)

        qa = [q["question_text"] for q in a["questions"]]
        qb = [q["question_text"] for q in b["questions"]]
        assert len(qa) == len(qb)

        # Option order must differ somewhere (permutations per question)
        options_differ = any(
            q1["options"] != q2["options"] for q1, q2 in zip(a["questions"], b["questions"])
        )
        order_differ = qa != qb
        assert order_differ or options_differ, (
            "Two generated exams were identical — randomization failed"
        )

    def test_in_progress_attempt_is_resumed_not_duplicated(self, client, db, first_subject_id):
        name = unique_name()
        token = register_faculty(client, name)["access_token"]
        first = start_exam(client, token, first_subject_id)
        second = start_exam(client, token, first_subject_id)
        assert first["attempt_id"] == second["attempt_id"]
        assert second["resuming"] is False

    def test_unknown_subject_rejected(self, client):
        token = register_faculty(client, unique_name())["access_token"]
        r = client.post(
            "/api/exams/start",
            headers={"Authorization": f"Bearer {token}"},
            json={"subject_id": 999999, "experience_band": "8-12"},
        )
        assert r.status_code == 404


class TestAnswers:
    def test_answer_saved_and_forward_only(self, client, db, first_subject_id):
        name = unique_name()
        token = register_faculty(client, name)["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        r = client.post(
            f"/api/exams/attempts/{aid}/answers",
            headers={"Authorization": f"Bearer {token}"},
            json={"position": 1, "chosen_options": [0]},
        )
        assert r.status_code == 200

        # Cannot go back to a previous question
        r = client.post(
            f"/api/exams/attempts/{aid}/answers",
            headers={"Authorization": f"Bearer {token}"},
            json={"position": 1, "chosen_options": [1]},
        )
        assert r.status_code == 200  # editing current position is allowed

        r = client.post(
            f"/api/exams/attempts/{aid}/answers",
            headers={"Authorization": f"Bearer {token}"},
            json={"position": 2, "chosen_options": [0]},
        )
        assert r.status_code == 200

        # skipping back to 1 after 2 is rejected
        r = client.post(
            f"/api/exams/attempts/{aid}/answers",
            headers={"Authorization": f"Bearer {token}"},
            json={"position": 1, "chosen_options": [1]},
        )
        assert r.status_code == 400

    def test_skip_forward_is_allowed_but_back_is_not(self, client, db, first_subject_id):
        name = unique_name()
        token = register_faculty(client, name)["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        r = client.post(
            f"/api/exams/attempts/{aid}/answers",
            headers={"Authorization": f"Bearer {token}"},
            json={"position": 1, "chosen_options": [0]},
        )
        assert r.status_code == 200

        # skipping forward (leaving Q2 unanswered) is allowed
        r = client.post(
            f"/api/exams/attempts/{aid}/answers",
            headers={"Authorization": f"Bearer {token}"},
            json={"position": 5, "chosen_options": [1, 3]},
        )
        assert r.status_code == 200

        # but answering an earlier position afterwards is not
        r = client.post(
            f"/api/exams/attempts/{aid}/answers",
            headers={"Authorization": f"Bearer {token}"},
            json={"position": 2, "chosen_options": [0]},
        )
        assert r.status_code == 400

    def test_status_reports_answered_positions(self, client, db, first_subject_id):
        name = unique_name()
        token = register_faculty(client, name)["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        for p in (1, 2, 3):
            client.post(
                f"/api/exams/attempts/{aid}/answers",
                headers={"Authorization": f"Bearer {token}"},
                json={"position": p, "chosen_options": [0]},
            )
        r = client.get(f"/api/exams/attempts/{aid}/status", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["last_position"] == 3
        assert r.json()["answered_positions"] == [1, 2, 3]


class TestScoring:
    def test_correct_answers_yield_full_raw_score(self, client, db, first_subject_id):
        name = unique_name()
        token = register_faculty(client, name)["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        answer_all_correct(client, token, aid, db)
        r = client.post(f"/api/exams/attempts/{aid}/submit", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "completed"
        assert body["answered"] == body["num_questions"]
        assert body["total_penalty"] == 0
        assert body["score_hidden"] is True
        assert body["subject_locked"] is True

        # verify the score server-side
        attempt_db = db.get(ExamAttempt, aid)
        assert attempt_db.raw_score == len(attempt_db.exam_questions)
        assert attempt_db.final_score == len(attempt_db.exam_questions)

    def test_final_equals_raw_minus_penalty_and_never_negative(self, client, db, first_subject_id):
        name = unique_name()
        token = register_faculty(client, name)["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        answer_all_correct(client, token, aid, db)
        # accumulate penalties: 3× tab switch (-1 each), 1× camera disconnected (-2)
        for _ in range(3):
            client.post(
                f"/api/exams/attempts/{aid}/violations",
                headers={"Authorization": f"Bearer {token}"},
                json={"type": "TAB_SWITCH"},
            )
        client.post(
            f"/api/exams/attempts/{aid}/violations",
            headers={"Authorization": f"Bearer {token}"},
            json={"type": "CAMERA_DISCONNECTED"},
        )
        r = client.post(f"/api/exams/attempts/{aid}/submit", headers={"Authorization": f"Bearer {token}"})
        body = r.json()
        assert body["total_penalty"] == -5.0

        attempt_db = db.get(ExamAttempt, aid)
        assert attempt_db.raw_score == len(attempt_db.exam_questions)
        assert attempt_db.final_score == attempt_db.raw_score + attempt_db.penalty_total

    def test_final_score_never_below_zero(self, client, db, first_subject_id):
        name = unique_name()
        token = register_faculty(client, name)["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        # answer nothing, rack up penalties
        for _ in range(10):
            client.post(
                f"/api/exams/attempts/{aid}/violations",
                headers={"Authorization": f"Bearer {token}"},
                json={"type": "CAMERA_PERMISSION_LOST"},
            )
        client.post(f"/api/exams/attempts/{aid}/submit", headers={"Authorization": f"Bearer {token}"})
        attempt_db = db.get(ExamAttempt, aid)
        assert attempt_db.final_score == 0
        assert attempt_db.final_score >= 0


class TestTimer:
    def test_answer_after_deadline_auto_submits(self, client, db, first_subject_id):
        from app.exam.engine import now_utc

        name = unique_name()
        token = register_faculty(client, name)["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        # push the deadline into the past
        a = db.get(ExamAttempt, aid)
        a.deadline = now_utc() - timedelta(seconds=60)
        db.commit()

        r = client.post(
            f"/api/exams/attempts/{aid}/answers",
            headers={"Authorization": f"Bearer {token}"},
            json={"position": 1, "chosen_options": [0]},
        )
        assert r.status_code == 409  # auto-submitted on touch

        a = db.get(ExamAttempt, aid)
        assert a.status == "auto_submitted"

    def test_explicit_submit_marks_auto_when_expired(self, client, db, first_subject_id):
        from app.exam.engine import now_utc

        name = unique_name()
        token = register_faculty(client, name)["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        a = db.get(ExamAttempt, aid)
        a.deadline = now_utc() - timedelta(seconds=5)
        db.commit()

        r = client.post(f"/api/exams/attempts/{aid}/submit", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["status"] == "auto_submitted"
        a = db.get(ExamAttempt, aid)
        assert a.status == "auto_submitted"
