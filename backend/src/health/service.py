from __future__ import annotations

from src.core import db as db_module
from src.core.config import get_settings


class HealthService(object):
    def health(self) -> dict:
        return {"status": "ok", "service": get_settings().app_name}

    def livez(self) -> dict:
        return {"status": "alive"}

    def readyz(self) -> dict:
        try:
            with db_module.get_database().engine.connect() as conn:
                conn.exec_driver_sql("SELECT 1")

            return {"status": "ready", "database": "ok"}
        except Exception as exc:
            return {
                "status": "not_ready",
                "database": "error",
                "detail": str(exc),
            }
