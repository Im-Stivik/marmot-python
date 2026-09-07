from __future__ import annotations

from collections import namedtuple

PermissionDefinition = namedtuple(
    "PermissionDefinition",
    ["name", "description", "resource_type", "action"],
)

USERNAME_PATTERN = r"^[a-z]\d{7}$"

PERMISSIONS = [
    PermissionDefinition(
        "view_users",
        "View user information",
        "users",
        "view",
    ),
    PermissionDefinition(
        "manage_users",
        "Create/update/delete users",
        "users",
        "manage",
    ),
    PermissionDefinition(
        "view_assets",
        "View assets",
        "assets",
        "view",
    ),
    PermissionDefinition(
        "manage_assets",
        "Create/update/delete assets",
        "assets",
        "manage",
    ),
    PermissionDefinition(
        "preview_assets",
        "Preview sample data from table assets",
        "assets",
        "preview",
    ),
    PermissionDefinition(
        "manage_roles",
        "Manage roles and permissions",
        "roles",
        "manage",
    ),
    PermissionDefinition(
        "view_metrics",
        "View system metrics and analytics",
        "metrics",
        "view",
    ),
    PermissionDefinition(
        "view_glossary",
        "View glossary terms",
        "glossary",
        "view",
    ),
    PermissionDefinition(
        "manage_glossary",
        "Create/update/delete glossary terms",
        "glossary",
        "manage",
    ),
    PermissionDefinition(
        "view_teams",
        "View teams",
        "teams",
        "view",
    ),
    PermissionDefinition(
        "manage_teams",
        "Create/update/delete teams",
        "teams",
        "manage",
    ),
    PermissionDefinition(
        "manage_sso_mappings",
        "Manage SSO team mappings",
        "sso",
        "manage",
    ),
    PermissionDefinition(
        "view_ingestion",
        "View ingestion schedules and job runs",
        "ingestion",
        "view",
    ),
    PermissionDefinition(
        "manage_ingestion",
        "Create/update/delete ingestion schedules",
        "ingestion",
        "manage",
    ),
    PermissionDefinition(
        "emit_agent_runs",
        "Record agent run telemetry",
        "agents",
        "emit",
    ),
    PermissionDefinition(
        "service_accounts_view",
        "View service accounts",
        "service_accounts",
        "view",
    ),
    PermissionDefinition(
        "service_accounts_manage",
        "Create, edit, delete service accounts and their API keys",
        "service_accounts",
        "manage",
    ),
]

# Regular users: catalog + glossary only. Metrics, ingestion, and global team
# listing are admin-only; team visibility will be membership-scoped in the API.
DEFAULT_USER_PERMISSIONS = [
    "view_assets",
    "view_glossary",
]

ADMIN_ROLE_NAME = "admin"
USER_ROLE_NAME = "user"
