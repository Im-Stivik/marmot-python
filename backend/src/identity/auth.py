from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.core.config import Settings, get_settings
from src.core.consts import USERNAME_PATTERN
from src.core.db import get_db
from src.identity.model import User

_USERNAME_REGEX = re.compile(USERNAME_PATTERN)
_password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bearer_scheme = HTTPBearer(auto_error=False)


def validate_username_format(username: str) -> bool:
    return _USERNAME_REGEX.match(username) is not None


def hash_password(password: str) -> str:
    return _password_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return _password_context.verify(plain_password, password_hash)


def create_access_token(
    user_id: UUID, settings: Optional[Settings] = None
) -> str:
    active_settings = settings or get_settings()
    expire = datetime.utcnow() + timedelta(
        minutes=active_settings.jwt.expire_minutes
    )
    payload = {"sub": str(user_id), "exp": expire}

    return jwt.encode(
        payload,
        active_settings.jwt.secret,
        algorithm=active_settings.jwt.algorithm,
    )


def decode_access_token(
    token: str, settings: Optional[Settings] = None
) -> Dict[str, Any]:
    active_settings = settings or get_settings()

    return jwt.decode(
        token,
        active_settings.jwt.secret,
        algorithms=[active_settings.jwt.algorithm],
    )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc

    user = db.query(User).filter(User.id == UUID(user_id)).one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
