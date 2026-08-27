from __future__ import annotations

from src.identity.auth import hash_password
from src.identity.model import Permission, Role, RolePermission, User, UserRole
from src.core.db import SessionLocal

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


def seed_database() -> None:
    """Idempotent seed for permissions, roles, and dev admin user."""
    db = SessionLocal()
    try:
        _seed_permissions(db)
        admin_role, user_role = _seed_roles(db)
        _seed_admin_user(db, admin_role)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _seed_permissions(db) -> None:
    if db.query(Permission).count() > 0:
        return
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
    admin_role = db.query(Role).filter(Role.name == "admin").one_or_none()
    user_role = db.query(Role).filter(Role.name == "user").one_or_none()

    if admin_role is None:
        admin_role = Role(
            name="admin",
            description="Administrator role with full system access",
            is_system=True,
        )
        db.add(admin_role)

    if user_role is None:
        user_role = Role(
            name="user",
            description="Standard user role with basic access",
            is_system=True,
        )
        db.add(user_role)

    db.flush()

    all_permissions = db.query(Permission).all()

    _ensure_role_permissions(db, admin_role, [p.name for p in all_permissions])
    _ensure_role_permissions(db, user_role, DEFAULT_USER_PERMISSIONS)

    return admin_role, user_role


def _ensure_role_permissions(db, role: Role, permission_names) -> None:
    existing_ids = {
        row.permission_id
        for row in db.query(RolePermission)
        .filter(RolePermission.role_id == role.id)
        .all()
    }
    for name in permission_names:
        permission = db.query(Permission).filter(Permission.name == name).one()
        if permission.id in existing_ids:
            continue
        db.add(RolePermission(role_id=role.id, permission_id=permission.id))


def _seed_admin_user(db, admin_role: Role) -> None:
    from src.core.config import get_settings

    settings = get_settings()
    username = settings.seed_admin_username

    admin_user = db.query(User).filter(User.username == username).one_or_none()
    if admin_user is None:
        admin_user = User(
            username=username,
            name="Admin User",
            password_hash=hash_password(settings.seed_admin_password),
            must_change_password=True,
            active=True,
        )
        db.add(admin_user)
        db.flush()

    has_admin_role = any(role.name == "admin" for role in admin_user.roles)
    if not has_admin_role:
        db.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
