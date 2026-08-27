from __future__ import annotations

from src.core import db as db_module
from src.core.config import get_settings
from src.identity.auth import hash_password
from src.identity.model import Permission, Role, RolePermission, User, UserRole

PERMISSIONS = [
    ("view_users", "View user information", "users", "view"),
    ("manage_users", "Create/update/delete users", "users", "manage"),
    ("view_assets", "View assets", "assets", "view"),
    ("manage_assets", "Create/update/delete assets", "assets", "manage"),
    ("preview_assets", "Preview sample data from table assets", "assets", "preview"),
    ("manage_roles", "Manage roles and permissions", "roles", "manage"),
    ("view_metrics", "View system metrics and analytics", "metrics", "view"),
    ("view_glossary", "View glossary terms", "glossary", "view"),
    ("manage_glossary", "Create/update/delete glossary terms", "glossary", "manage"),
    ("view_teams", "View teams", "teams", "view"),
    ("manage_teams", "Create/update/delete teams", "teams", "manage"),
    ("manage_sso_mappings", "Manage SSO team mappings", "sso", "manage"),
    ("view_ingestion", "View ingestion schedules and job runs", "ingestion", "view"),
    ("manage_ingestion", "Create/update/delete ingestion schedules", "ingestion", "manage"),
    ("emit_agent_runs", "Record agent run telemetry", "agents", "emit"),
    ("service_accounts_view", "View service accounts", "service_accounts", "view"),
    (
        "service_accounts_manage",
        "Create, edit, delete service accounts and their API keys",
        "service_accounts",
        "manage",
    ),
]

DEFAULT_USER_PERMISSIONS = [
    "view_assets",
    "view_metrics",
    "view_glossary",
    "view_teams",
    "view_ingestion",
]


def is_database_initialized(db) -> bool:
    """True once first-init seed has already run."""
    return db.query(Permission).count() > 0


def seed_database() -> None:
    """First-init seed only. Never mutates data on later rollouts."""
    db = db_module.SessionLocal()
    try:
        if is_database_initialized(db):
            return

        _seed_permissions(db)
        admin_role, _user_role = _seed_roles(db)
        _seed_admin_user(db, admin_role)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _seed_permissions(db) -> None:
    for name, description, resource_type, action in PERMISSIONS:
        db.add(
            Permission(
                name=name,
                description=description,
                resource_type=resource_type,
                action=action,
            )
        )
    db.flush()


def _seed_roles(db):
    admin_role = Role(
        name="admin",
        description="Administrator role with full system access",
        is_system=True,
    )
    user_role = Role(
        name="user",
        description="Standard user role with basic access",
        is_system=True,
    )
    db.add(admin_role)
    db.add(user_role)
    db.flush()

    all_permissions = db.query(Permission).all()
    for permission in all_permissions:
        db.add(RolePermission(role_id=admin_role.id, permission_id=permission.id))

    permissions_by_name = {permission.name: permission for permission in all_permissions}
    for name in DEFAULT_USER_PERMISSIONS:
        db.add(
            RolePermission(
                role_id=user_role.id,
                permission_id=permissions_by_name[name].id,
            )
        )

    return admin_role, user_role


def _seed_admin_user(db, admin_role: Role) -> None:
    settings = get_settings()
    admin_user = User(
        username=settings.seed_admin_username,
        name="Admin User",
        password_hash=hash_password(settings.seed_admin_password),
        must_change_password=True,
        active=True,
    )
    db.add(admin_user)
    db.flush()
    db.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
