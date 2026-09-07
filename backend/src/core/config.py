from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "marmot"
    password: str = "marmot"
    name: str = "marmot"
    sslmode: str = "disable"

    @property
    def url(self) -> str:
        return (
            "postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
            "?sslmode={sslmode}"
        ).format(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            name=self.name,
            sslmode=self.sslmode,
        )

    def url_for_database(self, database_name: str) -> str:
        return (
            "postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
            "?sslmode={sslmode}"
        ).format(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            name=database_name,
            sslmode=self.sslmode,
        )


class JwtSettings(BaseModel):
    secret: str = "change-me-in-production"
    algorithm: str = "HS256"
    expire_minutes: int = 1440


class SeedSettings(BaseModel):
    admin_username: str = "s1234567"
    admin_password: str = "admin"


class TrinoSettings(BaseModel):
    host: str = "localhost"
    port: int = 8081
    user: str = "marmot"
    password: Optional[str] = None
    http_scheme: str = "http"


class Settings(BaseSettings):
    """Application settings loaded from MARMOT_* environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="MARMOT_",
        env_nested_delimiter="_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "marmot-api"
    debug: bool = False
    group_source: str = "local"
    # Isolated DB used by pytest. Must end with "_test".
    test_database_name: str = "marmot_test"

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    jwt: JwtSettings = Field(default_factory=JwtSettings)
    seed: SeedSettings = Field(default_factory=SeedSettings)
    trino: TrinoSettings = Field(default_factory=TrinoSettings)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
