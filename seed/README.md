# Seed Data

The static, preloaded seed data (subjects, topics, and the 192-question bank) lives in
`backend/app/seed_data/` so it can be imported directly by the backend:

```
backend/app/seed_data/
├── __init__.py          # aggregates SUBJECTS + QUESTION_BANK
├── subjects.py          # 12 subject definitions (extensible to hundreds)
├── questions_*.py       # per-subject question banks
```

Seeding is idempotent and runs automatically on first startup (`app/seeding.py`) or manually:

```bash
cd backend
python -m app.seed            # seed only if empty
python -m app.seed --force    # fill gaps / re-seed reference data
```

**No AI, no generation.** Every question is hand-written, expert-level, and carries
subject, topic, difficulty, minimum teaching experience, type, options, correct answer(s)
and an explanation. Add hundreds more by appending to the `QUESTIONS` lists.
