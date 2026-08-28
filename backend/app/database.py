"""Database engine / session setup. SQLite for local dev, PostgreSQL for production."""
from collections.abc import Generator
import logging

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings

logger = logging.getLogger("faculty-testing")

settings.ensure_sqlite_dir()

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)


if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):  # noqa: ANN001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    """Lightweight in-place migrations for existing databases (no Alembic).

    Login no longer requires a department, so user names must be globally
    unique. On databases created before that change the column-level index is
    added here; if a duplicate name already exists the index is skipped and a
    warning is logged (login will still work, but enforce uniqueness manually).
    """
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS uq_users_name_normalized "
                    "ON users (name_normalized)"
                )
            )
    except Exception:
        logger.warning(
            "Could not create unique index on users.name_normalized — duplicate "
            "names may exist. Deduplicate users to enforce unique login names.",
            exc_info=True,
        )
