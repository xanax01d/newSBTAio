from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    admin_ids: list[int] = Field(default_factory=list)
    report_chat_id: int | None = None

    database_url: str = "postgresql+asyncpg://sbt:sbt_password@localhost:5432/sbt_bot"
    redis_url: str = "redis://localhost:6379/0"

    bsac_vo_url: str = "http://bsac.by/tasks/vo/do"
    bsac_vo_zo_url: str = "http://bsac.by/tasks/vo/zo"
    bsac_sso_url: str = "http://bsac.by/tasks/sso/do"
    bsac_sso_zo_url: str = "http://bsac.by/tasks/sso/zo"
    parse_interval_minutes: Annotated[int, Field(ge=5)] = 180
    timezone: str = "Europe/Minsk"

    pictures_dir: Path = Path("pictures")
    log_level: str = "INFO"
    log_file: Path = Path("logs/bot.log")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def _parse_admin_ids(cls, value: object) -> list[int]:
        if isinstance(value, str):
            stripped = value.strip().strip("[]")
            if not stripped:
                return []
            return [int(item.strip()) for item in stripped.split(",") if item.strip()]
        return list(value) if isinstance(value, (list, tuple, set)) else []

    def picture_path(self, index: int) -> Path:
        """Return path to menu picture (1-based index matching pictures/<n>.png)."""
        return self.pictures_dir / f"{index}.png"


def load_settings() -> Settings:
    """Instantiate and validate application settings."""
    return Settings()
