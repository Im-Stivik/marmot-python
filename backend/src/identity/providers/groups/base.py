from __future__ import annotations

from typing import List, Protocol

from src.identity.model import Group, User


class GroupMembershipProvider(Protocol):
    def get_groups(self, user: User) -> List[Group]:
        ...
