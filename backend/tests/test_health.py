from __future__ import annotations

from fastapi.testclient import TestClient

from main import create_app


def test_health() -> None:
    client = TestClient(create_app())
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "ok"

    assert body["service"] == "marmot-api"


def test_livez() -> None:
    client = TestClient(create_app())
    response = client.get("/livez")

    assert response.status_code == 200

    assert response.json()["status"] == "alive"


def test_readyz_returns_status() -> None:
    """readyz reports database status; may be not_ready if Postgres is down."""
    client = TestClient(create_app())
    response = client.get("/readyz")

    assert response.status_code == 200
    body = response.json()

    assert body["status"] in ("ready", "not_ready")

    assert "database" in body


def test_openapi_available() -> None:
    client = TestClient(create_app())
    response = client.get("/openapi.json")

    assert response.status_code == 200

    assert response.json()["info"]["title"] == "Marmot API"
