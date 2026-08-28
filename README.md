# Faculty Competency Testing Platform

A production-quality **faculty examination web application** for difficult, subject-based MCQ
examinations with live camera monitoring, full-session recording, anti-cheating event logging,
configurable violation penalties, permanent subject locking and a complete admin review panel.

**No AI anywhere in the examination system.** Every question, subject, difficulty distribution,
experience rule, answer, penalty and exam configuration is static/preloaded or managed through the
application. The platform is generic and reusable by any educational institution (no institution
is referenced anywhere in the UI or code).

---

## Feature Overview

| Area | Highlights |
| --- | --- |
| Faculty accounts | Full name (auto-uppercased), department, password. No Google/Microsoft/OAuth/OTP. |
| Login | Full name + password (names are globally unique, department not needed); rate-limited; bcrypt-hashed passwords; JWT sessions. |
| Dashboard | Subject cards with status: `AVAILABLE`, `IN PROGRESS`, `COMPLETED` (locked). |
| Exam engine | Server-side question selection per experience band + difficulty distribution, randomized question & option order, 1 mark per question, server-authoritative 60-minute timer. |
| Camera | Mandatory verification (detected, accessible, face visible, lighting, unobstructed) and continuous monitoring (dark / bright / obstructed / disconnected / permission lost) with a grace period and a continuous warning tone. |
| Recording | MediaRecorder → chunked upload with retry → secure storage; admin-only playback with click-to-seek security timeline. |
| Anti-cheating | Tab switch, focus loss, copy/cut/paste, context menu, print, keyboard shortcuts, fullscreen exit — all logged server-side with timestamps and configurable penalties. |
| Scoring | Raw − penalties (never below 0) computed **server-side**. Faculty never sees raw/final score; admins see everything. |
| Subject locking | Enforced by the backend AND a partial unique database index — a completed subject can never be retaken. |
| Admin panel | Dashboard analytics, faculty list, exam reports, question-by-question review, security timeline, camera recordings, question bank CRUD, subjects/topics/departments, penalties & experience distributions. |

---

## Quick Start (local development)

Prerequisites: Python 3.11+ and Node.js 20+.

### 1. Backend (FastAPI + SQLite by default)

```bash
cd backend
python -m venv .venv                 # Windows: .venv\Scripts\activate
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # optional — sensible defaults exist
python -m app.seed                   # seeds departments, admin, 12 subjects, 192 questions
uvicorn app.main:app --reload --port 8100
```

The database is seeded automatically on first startup as well. API docs: http://localhost:8100/docs

### 2. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev        # http://localhost:5175  (proxies /api to the backend on :8100)
```

### 3. Log in

| Role | Credentials (dev default, from `backend/.env`) |
| --- | --- |
| Admin | username `ADMIN`, password `admin123` |
| Faculty | register a new account on the landing page |

> ⚠ Change `ADMIN_PASSWORD` and `SECRET_KEY` before any real deployment.

### Tests

```bash
cd backend
python -m pytest tests/ -q        # 48 tests: auth, exam engine, scoring, violations, locking, authorization, recordings
```

A live end-to-end smoke test exercises every major flow against the running stack
(register → exam → answers/violations → recording → submit → locking → admin report →
video playback → question CRUD → config → auto-submit):

```bash
bash smoke_test.sh              # requires backend (:8100) and frontend dev server (:5175) running
```

---

## Docker (PostgreSQL + backend + frontend)

```bash
docker compose up --build
```

- Frontend: http://localhost:5175 (served by nginx, `/api` proxied to the backend)
- Backend API: http://localhost:8100
- PostgreSQL runs on the internal `db` service (see `docker-compose.yml`)

Local dev defaults to SQLite; the compose file runs PostgreSQL in production-style.

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/            # routes: auth, faculty, exam, recordings, admin
│   │   ├── exam/           # exam engine: selection, randomization, scoring, locking
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response models
│   │   ├── security/       # bcrypt + JWT
│   │   ├── seed_data/      # static question bank (192 questions, 12 subjects)
│   │   ├── seeding.py      # idempotent seeding (auto-runs on first startup)
│   │   ├── config.py       # env configuration (pydantic-settings)
│   │   └── main.py         # FastAPI app
│   ├── tests/              # pytest suite
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── pages/          # landing, auth, dashboard, exam, camera check, admin pages
│       ├── components/     # UI kit, toast, video player
│       ├── hooks/          # auth, server-authoritative timer
│       ├── services/       # api client, camera analysis, violation monitor, recording, audio
│       ├── types/          # shared TypeScript types
│       └── layouts/        # admin shell
├── storage/recordings/     # exam camera recordings (git-ignored)
└── docker-compose.yml
```

---

## Security Model

- **Passwords**: bcrypt-hashed (12 rounds). Plaintext is never stored.
- **Sessions**: JWT (HS256) access tokens; role-based authorization on every route.
- **Rate limiting**: in-memory login limiter (10 attempts / 15 min per identity+IP).
- **CSRF**: tokens are sent via `Authorization` headers (not cookies) — no CSRF surface.
- **Headers/CORS**: `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`,
  and a strict CORS allow-list.
- **Server is authoritative for everything**: correct answers, scoring, penalties, the exam
  deadline (auto-submit on expiry), exam completion and subject locking are all enforced
  server-side; the client only renders.
- **Recordings**: stored outside the web root, served only via authenticated admin endpoints
  using short-lived signed URLs (HTML `<video>` cannot send headers).
- **SQL injection**: SQLAlchemy ORM parameterization everywhere.

### Subject locking

Preventing a retake is enforced in two layers:

1. Application check — `start_attempt` rejects any attempt for a (faculty, subject) pair that
   already has a `completed`/`auto_submitted` attempt.
2. A **partial unique index** on `exam_attempts(faculty_id, subject_id)` filtered to completed
   statuses — even a direct database write cannot create a second completed attempt.

---

## Question Bank

`backend/app/seed_data/` holds the static bank: **192 expert-level questions across 12 subjects**
(Data Structures, DBMS, Operating Systems, Computer Networks, Computer Organization, Java,
Software Engineering, Algorithms, Machine Learning, AI, Python, Web Technologies), each tagged
with subject, topic, difficulty (`hard` / `very_hard` / `expert`), minimum teaching experience,
and question type (`single`, `multiple`, `assertion_reason`, `scenario`, `code`, `numerical`,
`debugging`).

To add questions, append dicts to the per-subject modules — hundreds/thousands can be added
without any code change. The admin can also add/edit/delete questions from the Question Bank UI.

**Demo scale note:** the seeded question banks hold ~16 questions per subject, so the seeded
exam configuration uses **16 questions per exam** so every experience band can start an exam.
The platform rule defaults to **40 questions / 60 minutes**; raise `num_questions` per subject
(Admin → Subjects → Exam config) as banks grow, exactly as configured for production.

---

## Camera & Anti-Cheating — honest limitations

A browser-based website **cannot** guarantee prevention of physical cheating: another phone
recording the screen, external cameras, hardware-level screenshots or some OS-level capture
tools are out of reach. This platform provides the strongest technically possible **browser-level**
monitoring, recording and deterrence:

- Frame analysis is **heuristic image processing** (brightness, variance, center skin-tone ratio) —
  it is not AI face recognition and should not be advertised as such.
- Fullscreen is requested and exits are detected/logged; browsers may block re-entry without a
  user gesture, so a “Re-enter fullscreen” control is provided.
- The warning buzzer requires an initial user gesture to unlock audio (browser autoplay policy);
  visual warnings always accompany sounds.
- The architecture keeps violations/recordings separate so a future kiosk/secure-browser client
  could be added without changing the backend.

---

## Environment Variables (`backend/.env`)

See `backend/.env.example`. Key variables: `DATABASE_URL`, `SECRET_KEY`, `ADMIN_USERNAME`,
`ADMIN_PASSWORD`, `VIDEO_STORAGE_PATH`, `CORS_ORIGINS`, `EXAM_DURATION_MINUTES`,
`EXAM_QUESTION_COUNT`, `CAMERA_GRACE_SECONDS`.

---

## License / Notes

Built as a self-contained reference implementation. No external identity providers, no AI
services, no analytics — the application is fully offline-capable once dependencies are installed.
