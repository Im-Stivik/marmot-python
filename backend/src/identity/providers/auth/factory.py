from __future__ import annotations

from sqlalchemy.orm import Session

from src.identity.providers.auth.base import LocalAuthProvider, SsoAuthProvider
from src.identity.providers.auth.local import DatabaseLocalAuthProvider
from src.identity.providers.auth.sso import StubSsoAuthProvider


def get_local_auth_provider(db: Session) -> LocalAuthProvider:
    return DatabaseLocalAuthProvider(db)


def get_sso_auth_provider() -> SsoAuthProvider:
    return StubSsoAuthProvider()
