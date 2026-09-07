from __future__ import annotations

import importlib
import pkgutil
from typing import Generator, Optional

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.core.config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all domain models."""


class Database(object):
    """Engine and session factory bound to one database URL."""

    def __init__(self, database_url: str) -> None:
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            future=True,
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            future=True,
        )

    @classmethod
    def from_settings(cls) -> "Database":
        return cls(get_settings().database.url)

    def create_session(self) -> Session:
        return self.SessionLocal()

    def create_tables(self) -> None:
        import_domain_models()
        Base.metadata.create_all(bind=self.engine)

    def table_names(self):
        return set(inspect(self.engine).get_table_names())

    def missing_model_tables(self):
        import_domain_models()
        expected = set(Base.metadata.tables.keys())
        existing = self.table_names()

        return expected - existing

    def dispose(self) -> None:
        self.engine.dispose()


_database: Optional[Database] = None


def get_database() -> Database:
    global _database

    if _database is None:
        _database = Database.from_settings()

    return _database


def set_database(database: Database) -> None:
    global _database

    if _database is not None:
        _database.dispose()

    _database = database


def get_db() -> Generator[Session, None, None]:
    session = get_database().create_session()

    try:
        yield session
    finally:
        session.close()


def import_domain_models() -> None:
    """Import every domain ``model`` module so subclasses register on Base."""
    import src as src_package

    for module_info in pkgutil.walk_packages(
        src_package.__path__,
        prefix=src_package.__name__ + ".",
    ):
        if module_info.name.endswith(".model"):
            importlib.import_module(module_info.name)
