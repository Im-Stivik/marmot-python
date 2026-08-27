from __future__ import annotations

from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.core.config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all domain models."""


engine: Engine
SessionLocal: sessionmaker


def _build_engine(database_url: Optional[str] = None) -> Engine:
    url = database_url or get_settings().database_url
    return create_engine(
        url,
        pool_pre_ping=True,
        future=True,
    )


def configure_engine(database_url: Optional[str] = None) -> Engine:
    """(Re)bind the global engine and session factory to a database URL."""
    global engine, SessionLocal

    if "engine" in globals() and engine is not None:
        engine.dispose()

    engine = _build_engine(database_url)
    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        future=True,
    )
    return engine


configure_engine()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all tables from SQLAlchemy metadata (no migration tool)."""
    import src.core.models  # noqa: F401 — register all ORM models with Base.metadata

    Base.metadata.create_all(bind=engine)
