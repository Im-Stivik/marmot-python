from __future__ import annotations

from src.core import db as db_module
from src.identity.model import Permission, Role, User
from src.identity.repository import IdentityRepository


def test_seed_creates_permissions_and_admin(client) -> None:
    db = db_module.SessionLocal()
    try:
        assert db.query(Permission).count() == 17
        admin = db.query(User).filter(User.username == "A0000000").one()

        assert admin.active is True
        admin_role = db.query(Role).filter(Role.name == "admin").one()
        repo = IdentityRepository(db)

        assert repo.has_permission(admin.id, "assets", "manage") is True

        assert admin_role.is_system is True
    finally:
        db.close()


def test_seed_is_first_init_only(client) -> None:
    db = db_module.SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "A0000000").one()
        admin.name = "Changed On Purpose"
        db.commit()
    finally:
        db.close()

    from src.core.seed import seed_database

    seed_database()

    db = db_module.SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "A0000000").one()

        assert admin.name == "Changed On Purpose"
    finally:
        db.close()
