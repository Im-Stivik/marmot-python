from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.core import db as db_module
from src.core.config import Settings, get_settings
from src.core.db import configure_engine

# Never allow create/drop against these database names.
_PROTECTED_DATABASES = frozenset(
    {
        "marmot",
        "metastore",
        "postgres",
        "template0",
        "template1",
    }
)


def assert_safe_test_database_name(name: str) -> None:
    if name in _PROTECTED_DATABASES:
        raise RuntimeError(
            "Refusing to use protected database name for tests: {0}".format(name)
        )
    if not name.endswith("_test"):
        raise RuntimeError(
            "Test database name must end with '_test', got: {0}".format(name)
        )


def _admin_engine(settings: Settings) -> Engine:
    """Connect to the app DB only to run CREATE/DROP DATABASE statements."""
    url = (
        "postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
        "?sslmode={sslmode}"
    ).format(
        user=settings.database_user,
        password=settings.database_password,
        host=settings.database_host,
        port=settings.database_port,
        name=settings.database_name,
        sslmode=settings.database_sslmode,
    )
    return create_engine(url, isolation_level="AUTOCOMMIT", future=True)


def database_exists(name: str, settings: Settings = None) -> bool:
    cfg = settings or get_settings()
    assert_safe_test_database_name(name)
    admin = _admin_engine(cfg)
    try:
        with admin.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": name},
            )
            return result.scalar() is not None
    finally:
        admin.dispose()


def create_test_database(name: str, settings: Settings = None) -> None:
    cfg = settings or get_settings()
    assert_safe_test_database_name(name)
    if database_exists(name, cfg):
        raise RuntimeError(
            "Test database {0!r} already exists. Aborting so we do not "
            "touch or drop an unexpected database. Drop it manually if it "
            "is leftover from a crashed test run.".format(name)
        )

    admin = _admin_engine(cfg)
    try:
        with admin.connect() as conn:
            conn.execute(text('CREATE DATABASE "{0}"'.format(name)))
    finally:
        admin.dispose()


def drop_test_database(name: str, settings: Settings = None) -> None:
    cfg = settings or get_settings()
    assert_safe_test_database_name(name)
    admin = _admin_engine(cfg)
    try:
        with admin.connect() as conn:
            conn.execute(
                text(
                    "SELECT pg_terminate_backend(pid) "
                    "FROM pg_stat_activity "
                    "WHERE datname = :name AND pid <> pg_backend_pid()"
                ),
                {"name": name},
            )
            conn.execute(text('DROP DATABASE IF EXISTS "{0}"'.format(name)))
    finally:
        admin.dispose()


def _database_url_for(name: str, settings: Settings) -> str:
    return (
        "postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
        "?sslmode={sslmode}"
    ).format(
        user=settings.database_user,
        password=settings.database_password,
        host=settings.database_host,
        port=settings.database_port,
        name=name,
        sslmode=settings.database_sslmode,
    )


@contextmanager
def temporary_test_database() -> Iterator[str]:
    """
    Create an isolated test DB, point the app engine at it, then drop it.

    Aborts if the test DB already exists (safety against wiping unexpected data).
    """
    # Capture settings before we rewrite MARMOT_DATABASE_NAME.
    settings = get_settings()
    name = settings.test_database_name
    assert_safe_test_database_name(name)

    previous_name = os.environ.get("MARMOT_DATABASE_NAME")
    create_test_database(name, settings)

    os.environ["MARMOT_DATABASE_NAME"] = name
    get_settings.cache_clear()
    configure_engine(_database_url_for(name, settings))

    try:
        yield name
    finally:
        db_module.engine.dispose()

        if previous_name is None:
            os.environ.pop("MARMOT_DATABASE_NAME", None)
        else:
            os.environ["MARMOT_DATABASE_NAME"] = previous_name

        get_settings.cache_clear()
        configure_engine()
        drop_test_database(name, settings)
