from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from main import create_app
from src.core.config import get_settings
from src.core.db import get_database
from tests.db_isolation import temporary_test_database


@pytest.fixture(scope="session")
def postgres_available() -> bool:
    try:
        with get_database().engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")

        return True
    except SQLAlchemyError:
        return False


@pytest.fixture
def isolated_db(postgres_available: bool):
    """Create a fresh marmot_test DB for one test; drop it afterwards.

    Aborts if marmot_test already exists so we never drop an unexpected DB.
    """
    if not postgres_available:
        pytest.skip("Postgres is not available")

    with temporary_test_database() as name:
        yield name


@pytest.fixture
def client(isolated_db: str) -> TestClient:
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def admin_credentials():
    settings = get_settings()

    return {
        "username": settings.seed.admin_username,
        "password": settings.seed.admin_password,
    }
