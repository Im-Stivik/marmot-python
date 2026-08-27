from __future__ import annotations

from sqlalchemy.orm import Session

from src.core.config import Settings, get_settings
from src.identity.providers.auth.base import AuthProvider
from src.identity.providers.auth.local import LocalAuthProvider
from src.identity.providers.auth.sso import SsoAuthProvider


def get_auth_provider(db: Session, settings: Settings = None) -> AuthProvider:
    cfg = settings or get_settings()
    if cfg.auth_mode == "local":
        return LocalAuthProvider(db)
    if cfg.auth_mode == "sso":
        return SsoAuthProvider()
    raise ValueError("Unsupported auth mode: {0}".format(cfg.auth_mode))
