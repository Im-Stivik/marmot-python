from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.identity.model import User


@dataclass(frozen=True)
class LoginCredentials:
    username: str
    password: str


class AuthProvider(Protocol):
    def authenticate(self, credentials: LoginCredentials) -> User:
        ...
