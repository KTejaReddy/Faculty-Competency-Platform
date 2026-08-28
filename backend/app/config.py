"""Application configuration loaded from environment / .env file."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Faculty Competency Testing Platform"
    debug: bool = False

    database_url: str = "sqlite:///./data/app.db"

    secret_key: str = "dev-secret-change-me-0123456789abcdef0123456789abcdef"
    access_token_expire_minutes: int = 720

    admin_username: str = "ADMIN"
    admin_password: str = "admin123"

    video_storage_path: str = "../storage/recordings"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    exam_duration_minutes: int = 60
    exam_question_count: int = 40

    camera_grace_seconds: int = 5

    login_rate_limit_attempts: int = 10
    login_rate_limit_window_seconds: int = 900

    def ensure_sqlite_dir(self) -> None:
        """Create the parent directory for a file-backed SQLite database."""
        if not self.database_url.startswith("sqlite"):
            return
        path_part = self.database_url.replace("sqlite:///", "", 1)
        if path_part in ("", ":memory:") or path_part.startswith(":"):
            return
        db_path = Path(path_part)
        if not db_path.is_absolute():
            db_path = (BACKEND_DIR / db_path).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def recordings_dir(self) -> Path:
        p = Path(self.video_storage_path)
        if not p.is_absolute():
            p = (BACKEND_DIR / p).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
