from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

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

    def get_user_permissions(self, user_id: UUID) -> List[Permission]:
        roles = self.get_user_roles(user_id)
        if any(role.name == "admin" for role in roles):
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

    def has_permission(self, user_id: UUID, resource_type: str, action: str) -> bool:
        roles = self.get_user_roles(user_id)
        if any(role.name == "admin" for role in roles):
            return True

        permission = (
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
        return permission is not None

    def get_user_with_roles(self, user_id: UUID) -> Optional[User]:
        return (
            self._db.query(User)
            .options(joinedload(User.roles))
            .filter(User.id == user_id)
            .one_or_none()
        )
