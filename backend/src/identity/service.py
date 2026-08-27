from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.db import get_db
from src.identity.auth import create_access_token, get_current_user
from src.identity.model import Group, User
from src.identity.providers.auth.base import LoginCredentials
from src.identity.providers.auth.factory import (
    get_local_auth_provider,
    get_sso_auth_provider,
)
from src.identity.providers.groups.factory import get_group_membership_provider
from src.identity.repository import IdentityRepository
from src.identity.schemas import (
    GroupSummary,
    LoginResponse,
    MeResponse,
    RoleSummary,
    UserSummary,
)


class IdentityService(object):
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = IdentityRepository(db)
        self._local_auth = get_local_auth_provider(db)
        self._sso_auth = get_sso_auth_provider()
        self._group_provider = get_group_membership_provider(db, get_settings())

    def login(self, username: str, password: str) -> LoginResponse:
        user = self._local_auth.authenticate(
            LoginCredentials(username=username, password=password)
        )
        return self._issue_token(user)

    def login_sso(self, username: str, password: str) -> LoginResponse:
        # SSO provider is intentionally unimplemented for now.
        try:
            user = self._sso_auth.authenticate(
                LoginCredentials(username=username, password=password)
            )
        except NotImplementedError as exc:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="SSO login is not implemented yet",
            ) from exc
        return self._issue_token(user)

    def get_me(self, user: User) -> MeResponse:
        roles = self._repo.get_user_roles(user.id)
        groups = self._group_provider.get_groups(user)
        permissions = self._repo.get_user_permissions(user.id)
        return MeResponse(
            user=_user_summary(user),
            roles=[_role_summary(role) for role in roles],
            groups=[_group_summary(group) for group in groups],
            permissions=[permission.name for permission in permissions],
        )

    def _issue_token(self, user: User) -> LoginResponse:
        token = create_access_token(user.id)
        return LoginResponse(
            access_token=token,
            user=_user_summary(user),
        )


def _user_summary(user: User) -> UserSummary:
    return UserSummary(
        id=str(user.id),
        username=user.username,
        name=user.name,
        active=user.active,
        must_change_password=user.must_change_password,
    )


def _role_summary(role) -> RoleSummary:
    return RoleSummary(
        id=str(role.id),
        name=role.name,
        description=role.description,
    )


def _group_summary(group: Group) -> GroupSummary:
    return GroupSummary(
        id=str(group.id),
        name=group.name,
        description=group.description,
        external_id=group.external_id,
    )


def get_identity_service(db: Session = Depends(get_db)) -> IdentityService:
    return IdentityService(db)


def require_permission(resource_type: str, action: str) -> Callable:
    def dependency(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        repo = IdentityRepository(db)
        if not repo.has_permission(user.id, resource_type, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return dependency
