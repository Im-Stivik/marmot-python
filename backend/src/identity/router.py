from __future__ import annotations

from fastapi import APIRouter, Depends

from src.identity.auth import get_current_user
from src.identity.model import User
from src.identity.schemas import LoginRequest, LoginResponse, MeResponse
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
    body: LoginRequest,
    service: IdentityService = Depends(get_identity_service),
) -> LoginResponse:
    return service.login_sso(body.username, body.password)


@router.get("/users/me", response_model=MeResponse)
def me(
    current_user: User = Depends(get_current_user),
    service: IdentityService = Depends(get_identity_service),
) -> MeResponse:
    return service.get_me(current_user)
