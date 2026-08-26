from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from src.access.router import router as access_router
from src.catalog.router import router as catalog_router
from src.core.config import get_settings
from src.gateway.router import router as gateway_router
from src.health.router import router as health_router
from src.identity.router import router as identity_router
from src.ingestion.router import router as ingestion_router
from src.search.router import router as search_router


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Marmot API",
        version="0.1.0",
        description="Python rewrite of the Marmot data catalog (modular monolith).",
        debug=settings.debug,
    )
    application.include_router(health_router)
    application.include_router(identity_router, prefix="/api/v1")
    application.include_router(catalog_router, prefix="/api/v1")
    application.include_router(access_router, prefix="/api/v1")
    application.include_router(ingestion_router, prefix="/api/v1")
    application.include_router(search_router, prefix="/api/v1")
    application.include_router(gateway_router, prefix="/api/v1")
    return application


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
