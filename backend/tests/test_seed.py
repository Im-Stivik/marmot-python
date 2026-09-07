from __future__ import annotations

from src.core.consts import DEFAULT_USER_PERMISSIONS
from src.core.db import get_database
from src.core.seed import database_populate
from src.identity.model import Permission, Role, User
from src.identity.repository import IdentityRepository


def test_seed_creates_permissions_and_admin(client) -> None:
    db = get_database().create_session()

    try:
        assert db.query(Permission).count() == 17

        admin = db.query(User).filter(User.username == "s1234567").one()

        assert admin.name == "Admin User"

        admin_role = db.query(Role).filter(Role.name == "admin").one()
        repo = IdentityRepository(db)

        assert repo.has_permission(admin.id, "assets", "manage") is True

        assert admin_role.is_system is True
    finally:
        db.close()


def test_default_user_permissions_exclude_admin_only(client) -> None:
    assert "view_metrics" not in DEFAULT_USER_PERMISSIONS

    assert "view_ingestion" not in DEFAULT_USER_PERMISSIONS

    assert "view_teams" not in DEFAULT_USER_PERMISSIONS


def test_database_populate_is_first_init_only(client) -> None:
    database = get_database()
    db = database.create_session()

    try:
        admin = db.query(User).filter(User.username == "s1234567").one()
        admin.name = "Changed On Purpose"
        db.commit()
    finally:
        db.close()

    db = database.create_session()

    try:
        database_populate(db, database)
        db.commit()
        admin = db.query(User).filter(User.username == "s1234567").one()

        assert admin.name == "Changed On Purpose"
    finally:
        db.close()
