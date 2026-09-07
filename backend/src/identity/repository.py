from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from src.core.consts import ADMIN_ROLE_NAME
from src.identity.model import Permission, Role, User, UserRole


class IdentityRepository(object):
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        return self._db.query(User).filter(User.id == user_id).one_or_none()

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self._db.query(User).filter(User.username == username).one_or_none()

    def get_user_roles(self, user_id: UUID) -> List[Role]:
        return (
            self._db.query(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id, Role.deleted_at.is_(None))
            .order_by(Role.name)
            .all()
        )

    def user_has_admin_role(self, user_id: UUID) -> bool:
        roles = self.get_user_roles(user_id)

        return any(role.name == ADMIN_ROLE_NAME for role in roles)

    def get_user_permissions(self, user_id: UUID) -> List[Permission]:
        if self.user_has_admin_role(user_id):
            return self._db.query(Permission).order_by(Permission.name).all()

        return (
            self._db.query(Permission)
            .join(Role.permissions)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id)
            .distinct()
            .order_by(Permission.name)
            .all()
        )

    def find_permission_for_user(
        self, user_id: UUID, resource_type: str, action: str
    ) -> Optional[Permission]:
        return (
            self._db.query(Permission)
            .join(Role.permissions)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(
                UserRole.user_id == user_id,
                Permission.resource_type == resource_type,
                Permission.action == action,
            )
            .one_or_none()
        )

    def has_permission(self, user_id: UUID, resource_type: str, action: str) -> bool:
        if self.user_has_admin_role(user_id):
            return True

        return (
            self.find_permission_for_user(user_id, resource_type, action) is not None
        )

    def get_user_with_roles(self, user_id: UUID) -> Optional[User]:
        return (
            self._db.query(User)
            .options(joinedload(User.roles))
            .filter(User.id == user_id)
            .one_or_none()
        )
