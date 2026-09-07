from __future__ import annotations

from src.identity.model import User


class LocalAuthProvider(object):
    def authenticate(self, username: str, password: str) -> User:
        raise NotImplementedError


class SsoAuthProvider(object):
    def authenticate(self, token: str) -> User:
        raise NotImplementedError
