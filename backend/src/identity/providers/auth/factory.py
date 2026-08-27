from __future__ import annotations

from sqlalchemy.orm import Session

from src.identity.providers.auth.base import AuthProvider
from src.identity.providers.auth.local import LocalAuthProvider
from src.identity.providers.auth.sso import SsoAuthProvider


def get_local_auth_provider(db: Session) -> AuthProvider:
    return LocalAuthProvider(db)


def get_sso_auth_provider() -> AuthProvider:
    return SsoAuthProvider()
