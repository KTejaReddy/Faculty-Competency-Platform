# Run: Faculty Competency Testing Platform

Full-stack app: FastAPI backend (port 8100) + React/Vite frontend (port 5175).
Vite proxies `/api` to the backend on :8100. Default admin login: `ADMIN` / `admin123`
(backend has no `.env` — sensible defaults from `backend/app/config.py` are used).

## Reproduce setup artifacts

A fresh checkout needs these one-time steps:

1. Backend venv (project root, `T:\FACULTY COMPETENCY TESTING PLATFORM\.venv`):
   ```bash
   cd backend
   python -m venv ../.venv        # Windows: .venv\Scripts\python.exe
   ../.venv/Scripts/python.exe -m pip install -r requirements.txt
   ```
2. Backend env: `cp backend/.env.example backend/.env` is optional — defaults work.
3. Database: SQLite file `backend/data/app.db` is created and auto-seeded on first
   backend startup (`app.seeding` runs idempotently; `python -m app.seed` re-seeds).
4. Frontend deps:
   ```bash
   cd frontend
   npm install
   ```

## Run the servers

Backend (from `backend/`, venv lives at project root):

```bash
../.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8100
```

Frontend (from `frontend/`):

```bash
npm run dev        # http://localhost:5175
```

Default ports are 8100 / 5175; pick a free port if occupied and update
`frontend/vite.config.ts`'s proxy target accordingly.

Detached (Windows, PowerShell) — stdout and stderr must go to different files:

```powershell
# backend
(Start-Process -FilePath 'T:\FACULTY COMPETENCY TESTING PLATFORM\.venv\Scripts\python.exe' -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8100' -WorkingDirectory 'T:\FACULTY COMPETENCY TESTING PLATFORM\backend' -RedirectStandardOutput '<log>' -RedirectStandardError '<log>.err' -WindowStyle Hidden -PassThru).Id
# frontend (npm.cmd is required — Start-Process does not resolve shims)
(Start-Process -FilePath 'npm.cmd' -ArgumentList 'run','dev' -WorkingDirectory 'T:\FACULTY COMPETENCY TESTING PLATFORM\frontend' -RedirectStandardOutput '<log>' -RedirectStandardError '<log>.err' -WindowStyle Hidden -PassThru).Id
```

Health checks: `http://127.0.0.1:8100/docs` (backend) and `http://localhost:5175/`
(frontend). Note: vite binds to IPv6 `::1` only, so plain IPv4 curl gets no reply —
use `localhost` or PowerShell `Invoke-WebRequest`.
