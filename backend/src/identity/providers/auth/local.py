from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.identity.auth import validate_username_format, verify_password
from src.identity.model import User
from src.identity.providers.auth.base import AuthProvider, LoginCredentials


class LocalAuthProvider(AuthProvider):
    def __init__(self, db: Session) -> None:
        self._db = db

    def authenticate(self, credentials: LoginCredentials) -> User:
        username = credentials.username.strip()
        if not validate_username_format(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid username format",
            )

        user = self._db.query(User).filter(User.username == username).one_or_none()
        if user is None or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
            )
        if not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        return user
