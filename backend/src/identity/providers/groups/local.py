from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session, joinedload

from src.identity.model import Group, User, UserGroup
from src.identity.providers.groups.base import GroupMembershipProvider


class LocalGroupMembershipProvider(GroupMembershipProvider):
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_groups(self, user: User) -> List[Group]:
        return (
            self._db.query(Group)
            .join(UserGroup, UserGroup.group_id == Group.id)
            .filter(UserGroup.user_id == user.id)
            .options(joinedload(Group.users))
            .order_by(Group.name)
            .all()
        )
