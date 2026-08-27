from __future__ import annotations

from src.identity.model import User
from src.identity.providers.auth.base import AuthProvider, LoginCredentials


class SsoAuthProvider(AuthProvider):
    def authenticate(self, credentials: LoginCredentials) -> User:
        raise NotImplementedError("SSO authentication is not implemented yet")
