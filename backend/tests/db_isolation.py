from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.core.config import Settings, get_settings
from src.core.db import Database, set_database


def assert_safe_test_database_name(name: str) -> None:
    if not name.endswith("_test"):
        raise RuntimeError(
            "Test database name must end with '_test', got: {0}".format(name)
        )


def _admin_engine(settings: Settings) -> Engine:
    return create_engine(
        settings.database.url,
        isolation_level="AUTOCOMMIT",
        future=True,
    )


def database_exists(name: str, settings: Settings = None) -> bool:
    active_settings = settings or get_settings()

    assert_safe_test_database_name(name)

    admin = _admin_engine(active_settings)

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
    active_settings = settings or get_settings()

    assert_safe_test_database_name(name)

    if database_exists(name, active_settings):
        raise RuntimeError(
            "Test database {0!r} already exists. Aborting so we do not "
            "touch or drop an unexpected database. Drop it manually if it "
            "is leftover from a crashed test run.".format(name)
        )

    admin = _admin_engine(active_settings)

    try:
        with admin.connect() as conn:
            conn.execute(text('CREATE DATABASE "{0}"'.format(name)))
    finally:
        admin.dispose()


def drop_test_database(name: str, settings: Settings = None) -> None:
    active_settings = settings or get_settings()

    assert_safe_test_database_name(name)

    admin = _admin_engine(active_settings)

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


@contextmanager
def temporary_test_database() -> Iterator[str]:
    """
    Create an isolated test DB, point the app Database at it, then drop it.

    Aborts if the test DB already exists (safety against wiping unexpected data).
    """
    settings = get_settings()
    name = settings.test_database_name

    assert_safe_test_database_name(name)

    create_test_database(name, settings)
    set_database(Database(settings.database.url_for_database(name)))

    try:
        yield name
    finally:
        set_database(Database.from_settings())
        drop_test_database(name, settings)
