from __future__ import annotations

from src.core.db import SessionLocal
from src.identity.model import Permission, Role, User
from src.identity.repository import IdentityRepository


def test_seed_creates_permissions_and_admin(client) -> None:
    db = SessionLocal()
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
