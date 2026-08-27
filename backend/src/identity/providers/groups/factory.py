from __future__ import annotations

from sqlalchemy.orm import Session

from src.core.config import Settings, get_settings
from src.identity.providers.groups.base import GroupMembershipProvider
from src.identity.providers.groups.local import LocalGroupMembershipProvider
from src.identity.providers.groups.mirage import MirageGroupMembershipProvider


def get_group_membership_provider(
    db: Session, settings: Settings = None
) -> GroupMembershipProvider:
    cfg = settings or get_settings()
    if cfg.group_source == "local":
        return LocalGroupMembershipProvider(db)
    if cfg.group_source == "mirage":
        return MirageGroupMembershipProvider()
    raise ValueError("Unsupported group source: {0}".format(cfg.group_source))
