from __future__ import annotations

from fastapi import APIRouter

from src.health.service import HealthService

router = APIRouter(tags=["health"])
_service = HealthService()


@router.get("/health")
def health() -> dict:
    return _service.health()


@router.get("/livez")
def livez() -> dict:
    return _service.livez()


@router.get("/readyz")
def readyz() -> dict:
    return _service.readyz()
