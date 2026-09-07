from __future__ import annotations

from sqlalchemy.orm import Session

from src.core.config import Settings, get_settings
from src.identity.providers.groups.base import GroupMembershipProvider
from src.identity.providers.groups.local import LocalGroupMembershipProvider
from src.identity.providers.groups.mirage import MirageGroupMembershipProvider


def get_group_membership_provider(
    db: Session, settings: Settings = None
) -> GroupMembershipProvider:
    active_settings = settings or get_settings()

    if active_settings.group_source == "local":
        return LocalGroupMembershipProvider(db)

    if active_settings.group_source == "mirage":
        return MirageGroupMembershipProvider()

    raise ValueError(
        "Unsupported group source: {0}".format(active_settings.group_source)
    )
