from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from main import create_app
from src.core.config import get_settings
from src.core.db import engine


@pytest.fixture(scope="session")
def db_available() -> bool:
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return True
    except SQLAlchemyError:
        return False


@pytest.fixture
def client(db_available: bool) -> TestClient:
    if not db_available:
        pytest.skip("Postgres is not available")
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def admin_credentials():
    settings = get_settings()
    return {
        "username": settings.seed_admin_username,
        "password": settings.seed_admin_password,
    }
