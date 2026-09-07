from __future__ import annotations

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"

    assert body["service"] == "marmot-api"


def test_livez(client: TestClient) -> None:
    response = client.get("/livez")

    assert response.status_code == 200

    assert response.json()["status"] == "alive"


def test_readyz_returns_ready(client: TestClient) -> None:
    response = client.get("/readyz")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ready"

    assert body["database"] == "ok"


def test_openapi_available(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    assert response.json()["info"]["title"] == "Marmot API"
