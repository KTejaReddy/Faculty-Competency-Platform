"""Exam recording endpoints.

Recordings are uploaded in chunks (MediaRecorder timeslices) so a single failed
request never loses the recording. WebM chunks from the same recording session
are concatenated server-side into one playable file; MP4 chunks (Safari) are
kept as a playlist of segments played sequentially by the admin player.

Video files are only served through authenticated, admin-only endpoints using
short-lived signed URLs (HTML5 <video> cannot send Authorization headers).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import SessionLocal, get_db
from ..exam.engine import load_attempt_owner, now_utc
from ..models.models import Recording, User, VideoSegment
from ..security.tokens import decode_access_token
from .deps import get_current_user

router = APIRouter(prefix="/recordings", tags=["recordings"])

DbDep = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

VIDEO_ALGORITHM = "HS256"
VIDEO_TOKEN_TTL_MINUTES = 15


def make_video_token(attempt_id: int) -> str:
    payload = {
        "rid": attempt_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=VIDEO_TOKEN_TTL_MINUTES),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=VIDEO_ALGORITHM)


def verify_video_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[VIDEO_ALGORITHM])
        return int(payload["rid"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        return None


def attempt_dir(attempt_id: int) -> Path:
    d = settings.recordings_dir / str(attempt_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def ext_for_mime(mime: str) -> str:
    return "mp4" if "mp4" in mime else "webm"


# ---------------------------------------------------------------------------
# Faculty recording lifecycle
# ---------------------------------------------------------------------------


@router.post("/{attempt_id}/start")
def start_recording(
    attempt_id: int,
    mime_type: str = Form(...),
    db: DbDep = None,
    user: CurrentUser = None,  # type: ignore[assignment]
):
    attempt = load_attempt_owner(db, attempt_id, user.id)
    if attempt.status != "in_progress":
        raise HTTPException(409, "Recording cannot start: attempt is not in progress.")

    recording = db.scalar(select(Recording).where(Recording.attempt_id == attempt.id))
    if recording is None:
        recording = Recording(
            attempt_id=attempt.id,
            faculty_id=user.id,
            subject_id=attempt.subject_id,
            status="recording",
            mime_type=mime_type,
            started_at=now_utc(),
        )
        db.add(recording)
    else:
        recording.mime_type = mime_type
        recording.status = "recording"
        if recording.started_at is None:
            recording.started_at = now_utc()
    db.commit()
    db.refresh(recording)
    return {"recording_id": recording.id, "status": recording.status}


@router.post("/{attempt_id}/chunks")
async def upload_chunk(
    attempt_id: int,
    index: int = Form(...),
    duration: float = Form(0.0),
    file: UploadFile = File(...),
    db: DbDep = None,
    user: CurrentUser = None,  # type: ignore[assignment]
):
    attempt = load_attempt_owner(db, attempt_id, user.id)
    recording = db.scalar(select(Recording).where(Recording.attempt_id == attempt.id))
    if recording is None:
        raise HTTPException(404, "No recording started for this attempt.")

    ext = ext_for_mime(recording.mime_type)
    chunk_path = attempt_dir(attempt_id) / f"chunk_{index:05d}.{ext}"
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty chunk upload.")
    chunk_path.write_bytes(data)

    segment = db.scalar(
        select(VideoSegment).where(
            VideoSegment.recording_id == recording.id, VideoSegment.index == index
        )
    )
    if segment is None:
        segment = VideoSegment(recording_id=recording.id, index=index, file_path=str(chunk_path))
        db.add(segment)
    segment.size_bytes = len(data)
    segment.duration_seconds = duration
    segment.uploaded_at = now_utc()
    db.commit()

    return {"ok": True, "index": index, "size_bytes": len(data)}


@router.post("/{attempt_id}/finalize")
def finalize_recording(
    attempt_id: int,
    duration_seconds: float = Form(0.0),
    db: DbDep = None,
    user: CurrentUser = None,  # type: ignore[assignment]
):
    attempt = load_attempt_owner(db, attempt_id, user.id)
    recording = db.scalar(select(Recording).where(Recording.attempt_id == attempt.id))
    if recording is None:
        raise HTTPException(404, "No recording started for this attempt.")

    segments = db.scalars(
        select(VideoSegment)
        .where(VideoSegment.recording_id == recording.id)
        .order_by(VideoSegment.index)
    ).all()

    recording.duration_seconds = duration_seconds
    recording.ended_at = now_utc()
    recording.segment_count = len(segments)

    if not segments:
        recording.status = "failed"
        db.commit()
        return {"status": "failed", "reason": "no segments uploaded"}

    if len(segments) == 1:
        recording.file_path = segments[0].file_path
        recording.status = "ready"
    elif recording.mime_type.startswith("video/webm"):
        # WebM chunks from the same MediaRecorder session concatenate into one
        # valid stream (only the first chunk carries the EBML/Tracks header).
        try:
            combined = attempt_dir(attempt_id) / f"recording.{ext_for_mime(recording.mime_type)}"
            with combined.open("wb") as out:
                for seg in segments:
                    out.write(Path(seg.file_path).read_bytes())
            recording.file_path = str(combined)
            recording.status = "ready"
        except OSError:
            recording.status = "failed"
    else:
        # MP4: cannot raw-concatenate; keep segments, served via signed playlist
        recording.file_path = None
        recording.status = "ready"

    db.commit()
    return {"status": recording.status, "segment_count": recording.segment_count}


# ---------------------------------------------------------------------------
# Admin playback (authenticated)
# ---------------------------------------------------------------------------


def _authorize_video_access(token: str | None, authorization: str | None, attempt_id: int) -> None:
    """Accept either a signed video token or an admin Bearer token."""
    if token:
        if verify_video_token(token) == attempt_id:
            return
        raise HTTPException(401, "Invalid or expired video token.")
    if authorization and authorization.startswith("Bearer "):
        payload = decode_access_token(authorization[7:])
        if payload is None:
            raise HTTPException(401, "Invalid token.")
        with SessionLocal() as session:
            admin = session.get(User, int(payload["sub"]))
            if admin is not None and admin.role == "admin":
                return
        raise HTTPException(403, "Administrators only.")
    raise HTTPException(401, "Authentication required.")


@router.get("/admin/video/{attempt_id}")
def stream_video(
    attempt_id: int,
    token: str | None = Query(default=None),
    authorization: str | None = Query(default=None, alias="Authorization"),
    authorization_header: str | None = Header(default=None, alias="Authorization"),
):
    """Serve the concatenated recording file (or single segment) to an admin."""
    _authorize_video_access(token, authorization or authorization_header, attempt_id)

    with SessionLocal() as session:
        recording = session.scalar(select(Recording).where(Recording.attempt_id == attempt_id))
        if recording is None or recording.status != "ready" or not recording.file_path:
            raise HTTPException(404, "Recording not ready or not available.")
        path = Path(recording.file_path)
        mime = recording.mime_type

    if not path.exists():
        raise HTTPException(404, "Recording file missing on disk.")
    return FileResponse(str(path), media_type=mime, filename=f"recording_{attempt_id}")


@router.get("/admin/video/{attempt_id}/playlist")
def video_playlist(attempt_id: int, db: DbDep, user: CurrentUser):
    if user.role != "admin":
        raise HTTPException(403, "Administrators only.")
    recording = db.scalar(select(Recording).where(Recording.attempt_id == attempt_id))
    if recording is None or recording.status != "ready":
        raise HTTPException(404, "Recording not ready.")

    if recording.file_path is not None:
        return {
            "mode": "single",
            "mime_type": recording.mime_type,
            "duration": recording.duration_seconds,
            "url": f"/api/recordings/admin/video/{attempt_id}?token={make_video_token(attempt_id)}",
        }

    segments = db.scalars(
        select(VideoSegment)
        .where(VideoSegment.recording_id == recording.id)
        .order_by(VideoSegment.index)
    ).all()
    items = [
        {
            "index": seg.index,
            "duration": seg.duration_seconds,
            "url": f"/api/recordings/admin/segment/{attempt_id}/{seg.index}?token={make_video_token(attempt_id)}",
        }
        for seg in segments
    ]
    return {
        "mode": "segments",
        "mime_type": recording.mime_type,
        "duration": recording.duration_seconds,
        "segments": items,
    }


@router.get("/admin/segment/{attempt_id}/{index}")
def stream_segment(
    attempt_id: int,
    index: int,
    token: str | None = Query(default=None),
    authorization: str | None = Query(default=None, alias="Authorization"),
    authorization_header: str | None = Header(default=None, alias="Authorization"),
):
    _authorize_video_access(token, authorization or authorization_header, attempt_id)

    with SessionLocal() as session:
        recording = session.scalar(select(Recording).where(Recording.attempt_id == attempt_id))
        if recording is None or recording.status != "ready":
            raise HTTPException(404, "Recording not ready.")
        seg = session.scalar(
            select(VideoSegment).where(
                VideoSegment.recording_id == recording.id, VideoSegment.index == index
            )
        )
        if seg is None:
            raise HTTPException(404, "Segment not found.")
        path = Path(seg.file_path)
        mime = recording.mime_type

    if not path.exists():
        raise HTTPException(404, "Segment file missing on disk.")
    return FileResponse(str(path), media_type=mime)
