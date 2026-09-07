from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=8, max_length=8)
    password: str = Field(..., min_length=1)


class SsoLoginRequest(BaseModel):
    token: str = Field(..., min_length=1)


class RoleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None


class GroupSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    external_id: Optional[str] = None


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    name: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSummary


class MeResponse(BaseModel):
    user: UserSummary
    roles: List[RoleSummary]
    groups: List[GroupSummary]
    permissions: List[str]
