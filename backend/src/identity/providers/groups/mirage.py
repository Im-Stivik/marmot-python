from __future__ import annotations

from typing import List

from src.identity.model import Group, User
from src.identity.providers.groups.base import GroupMembershipProvider


class MirageGroupMembershipProvider(GroupMembershipProvider):
    def get_groups(self, user: User) -> List[Group]:
        raise NotImplementedError("Mirage group membership is not implemented yet")
