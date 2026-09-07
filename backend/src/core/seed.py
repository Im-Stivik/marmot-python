from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.consts import (
    ADMIN_ROLE_NAME,
    DEFAULT_USER_PERMISSIONS,
    PERMISSIONS,
    USER_ROLE_NAME,
)
from src.core.db import Database, get_database
from src.identity.auth import hash_password
from src.identity.model import Permission, Role, RolePermission, User, UserRole


def is_database_populated(db: Session) -> bool:
    return db.query(Permission).count() > 0


def database_populate(db: Session, database: Database = None) -> None:
    """Create missing tables, then insert first-init data only once."""
    active_database = database or get_database()
    active_database.create_tables()

    if is_database_populated(db):
        return

    permissions = _populate_permissions(db)
    db.flush()
    admin_role, _user_role = _populate_roles(db, permissions)
    db.flush()
    _populate_admin_user(db, admin_role)


def _populate_permissions(db: Session):
    permissions = []

    for definition in PERMISSIONS:
        permission = Permission(
            id=uuid.uuid4(),
            name=definition.name,
            description=definition.description,
            resource_type=definition.resource_type,
            action=definition.action,
        )
        db.add(permission)
        permissions.append(permission)

    return permissions


def _populate_roles(db: Session, permissions):
    admin_role = Role(
        id=uuid.uuid4(),
        name=ADMIN_ROLE_NAME,
        description="Administrator role with full system access",
        is_system=True,
    )
    user_role = Role(
        id=uuid.uuid4(),
        name=USER_ROLE_NAME,
        description="Standard user role with basic access",
        is_system=True,
    )
    db.add(admin_role)
    db.add(user_role)

    permissions_by_name = {permission.name: permission for permission in permissions}

    for permission in permissions:
        db.add(
            RolePermission(
                role_id=admin_role.id,
                permission_id=permission.id,
            )
        )

    for name in DEFAULT_USER_PERMISSIONS:
        db.add(
            RolePermission(
                role_id=user_role.id,
                permission_id=permissions_by_name[name].id,
            )
        )

    return admin_role, user_role


def _populate_admin_user(db: Session, admin_role: Role) -> None:
    settings = get_settings()
    admin_user = User(
        id=uuid.uuid4(),
        username=settings.seed.admin_username,
        name="Admin User",
        password_hash=hash_password(settings.seed.admin_password),
    )
    db.add(admin_user)
    db.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
