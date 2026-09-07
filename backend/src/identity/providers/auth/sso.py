from __future__ import annotations

from src.identity.model import User
from src.identity.providers.auth.base import SsoAuthProvider


class StubSsoAuthProvider(SsoAuthProvider):
    def authenticate(self, token: str) -> User:
        raise NotImplementedError("SSO authentication is not implemented yet")
