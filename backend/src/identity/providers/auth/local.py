from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.identity.auth import validate_username_format, verify_password
from src.identity.model import User
from src.identity.providers.auth.base import LocalAuthProvider


class DatabaseLocalAuthProvider(LocalAuthProvider):
    def __init__(self, db: Session) -> None:
        self._db = db

    def authenticate(self, username: str, password: str) -> User:
        cleaned_username = username.strip()

        if not validate_username_format(cleaned_username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid username format",
            )

        user = (
            self._db.query(User)
            .filter(User.username == cleaned_username)
            .one_or_none()
        )
        invalid_credentials = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

        if user is None or not user.password_hash:
            raise invalid_credentials

        if not verify_password(password, user.password_hash):
            raise invalid_credentials

        return user
