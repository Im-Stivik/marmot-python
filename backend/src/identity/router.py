from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.identity.auth import get_current_user
from src.identity.model import User
from src.identity.schemas import (
    LoginRequest,
    LoginResponse,
    MeResponse,
    SsoLoginRequest,
)
from src.identity.service import IdentityService, get_identity_service

router = APIRouter(tags=["identity"])


@router.post("/users/login", response_model=LoginResponse)
def login(
    body: LoginRequest,
    service: IdentityService = Depends(get_identity_service),
) -> LoginResponse:
    return service.login(body.username, body.password)


@router.post("/users/login/sso", response_model=LoginResponse)
def login_sso(
    body: SsoLoginRequest,
    service: IdentityService = Depends(get_identity_service),
) -> LoginResponse:
    try:
        return service.login_sso(body.token)
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="SSO login is not implemented yet",
        ) from exc


@router.get("/users/me", response_model=MeResponse)
def me(
    current_user: User = Depends(get_current_user),
    service: IdentityService = Depends(get_identity_service),
) -> MeResponse:
    return service.get_me(current_user)
