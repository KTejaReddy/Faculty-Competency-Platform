"""Manual seeding entrypoint.

Usage (from the backend/ directory):
    python -m app.seed            # seed only if the DB is empty
    python -m app.seed --force    # wipe and re-seed all reference data

The application also seeds automatically on first startup.
"""
from __future__ import annotations

import argparse

from .database import Base, SessionLocal, engine, run_migrations
from .seeding import seed_all


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the database")
    parser.add_argument("--force", action="store_true", help="Re-seed even if data exists")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    run_migrations()
    with SessionLocal() as db:
        seed_all(db, force=args.force)
    print("Seeding complete.")


if __name__ == "__main__":
    main()
