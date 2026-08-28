"""Recording lifecycle and playback authorization tests."""
from __future__ import annotations

import uuid

from .conftest import register_faculty


def unique_name() -> str:
    return f"RECORDER {uuid.uuid4().hex[:8].upper()}"


def start_exam(client, token, subject_id):
    r = client.post(
        "/api/exams/start",
        headers={"Authorization": f"Bearer {token}"},
        json={"subject_id": subject_id, "experience_band": "8-12"},
    )
    assert r.status_code == 200
    return r.json()


class TestRecordingLifecycle:
    def test_full_lifecycle_webm(self, client, db, first_subject_id, admin_token):
        token = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        r = client.post(
            f"/api/recordings/{aid}/start",
            headers={"Authorization": f"Bearer {token}"},
            data={"mime_type": "video/webm;codecs=vp8"},
        )
        assert r.status_code == 200

        for idx in (0, 1):
            r = client.post(
                f"/api/recordings/{aid}/chunks",
                headers={"Authorization": f"Bearer {token}"},
                data={"index": idx, "duration": 5.0},
                files={"file": (f"chunk{idx}.webm", b"\x1aE\xdf\xa3fake-webm-bytes" * 100, "video/webm")},
            )
            assert r.status_code == 200, r.text

        r = client.post(
            f"/api/recordings/{aid}/finalize",
            headers={"Authorization": f"Bearer {token}"},
            data={"duration_seconds": 10.0},
        )
        assert r.status_code == 200
        assert r.json()["status"] == "ready"

        # admin can fetch the playlist
        r = client.get(
            f"/api/recordings/admin/video/{aid}/playlist",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert r.status_code == 200
        playlist = r.json()
        assert playlist["mode"] == "single"

        # and stream the video via the signed URL
        r = client.get(playlist["url"])
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("video/")

    def test_mp4_fallback_keeps_segments(self, client, db, first_subject_id, admin_token):
        token = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        client.post(
            f"/api/recordings/{aid}/start",
            headers={"Authorization": f"Bearer {token}"},
            data={"mime_type": "video/mp4"},
        )
        for idx in (0, 1, 2):
            client.post(
                f"/api/recordings/{aid}/chunks",
                headers={"Authorization": f"Bearer {token}"},
                data={"index": idx, "duration": 4.0},
                files={"file": (f"c{idx}.mp4", b"mp4bytes" * 50, "video/mp4")},
            )
        r = client.post(
            f"/api/recordings/{aid}/finalize",
            headers={"Authorization": f"Bearer {token}"},
            data={"duration_seconds": 12.0},
        )
        assert r.json()["status"] == "ready"

        r = client.get(
            f"/api/recordings/admin/video/{aid}/playlist",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        playlist = r.json()
        assert playlist["mode"] == "segments"
        assert len(playlist["segments"]) == 3

        # a segment streams via its signed url
        r = client.get(playlist["segments"][0]["url"])
        assert r.status_code == 200

    def test_video_requires_admin(self, client, db, first_subject_id, admin_token):
        token = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token, first_subject_id)
        aid = attempt["attempt_id"]

        r = client.get(f"/api/recordings/admin/video/{aid}", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code in (401, 403)

        # no token at all
        r = client.get(f"/api/recordings/admin/video/{aid}")
        assert r.status_code == 401

    def test_faculty_cannot_record_another_attempt(self, client, db, first_subject_id):
        token_a = register_faculty(client, unique_name())["access_token"]
        token_b = register_faculty(client, unique_name())["access_token"]
        attempt = start_exam(client, token_a, first_subject_id)
        r = client.post(
            f"/api/recordings/{attempt['attempt_id']}/start",
            headers={"Authorization": f"Bearer {token_b}"},
            data={"mime_type": "video/webm"},
        )
        assert r.status_code == 403
