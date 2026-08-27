from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from MARMOT_* environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="MARMOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "marmot-api"
    debug: bool = False

    database_host: str = "localhost"
    database_port: int = 5432
    database_user: str = "marmot"
    database_password: str = "marmot"
    database_name: str = "marmot"
    database_sslmode: str = "disable"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    auth_mode: str = "local"
    group_source: str = "local"
    seed_admin_username: str = "A0000000"
    seed_admin_password: str = "admin"

    trino_host: str = "localhost"
    trino_port: int = 8081
    trino_user: str = "marmot"
    trino_password: Optional[str] = None
    trino_http_scheme: str = "http"

    @property
    def database_url(self) -> str:
        return (
            "postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
            "?sslmode={sslmode}"
        ).format(
            user=self.database_user,
            password=self.database_password,
            host=self.database_host,
            port=self.database_port,
            name=self.database_name,
            sslmode=self.database_sslmode,
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
