from __future__ import annotations

from fastapi.testclient import TestClient

from src.identity.auth import validate_username_format


def test_validate_username_format() -> None:
    assert validate_username_format("A1234567") is True

    assert validate_username_format("z9876543") is True

    assert validate_username_format("admin") is False

    assert validate_username_format("A123456") is False

    assert validate_username_format("AB1234567") is False


def test_login_success(client: TestClient, admin_credentials: dict) -> None:
    response = client.post("/api/v1/users/login", json=admin_credentials)

    assert response.status_code == 200
    body = response.json()

    assert body["token_type"] == "bearer"

    assert body["access_token"]

    assert body["user"]["username"] == admin_credentials["username"]


def test_login_invalid_password(client: TestClient, admin_credentials: dict) -> None:
    response = client.post(
        "/api/v1/users/login",
        json={"username": admin_credentials["username"], "password": "wrong"},
    )

    assert response.status_code == 401


def test_login_invalid_username_format(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users/login",
        json={"username": "not-valid", "password": "admin"},
    )

    assert response.status_code == 422 or response.status_code == 400


def test_login_sso_not_implemented(
    client: TestClient, admin_credentials: dict
) -> None:
    response = client.post("/api/v1/users/login/sso", json=admin_credentials)

    assert response.status_code == 501


def test_me_requires_auth(client: TestClient) -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_me_with_token(client: TestClient, admin_credentials: dict) -> None:
    login = client.post("/api/v1/users/login", json=admin_credentials)
    token = login.json()["access_token"]
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer {0}".format(token)},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["user"]["username"] == admin_credentials["username"]

    assert "admin" in [role["name"] for role in body["roles"]]

    assert len(body["permissions"]) == 17
