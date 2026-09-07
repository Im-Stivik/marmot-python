from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    material_resource_name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    providers: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    environments: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict
    )
    schema_: Mapped[Dict[str, Any]] = mapped_column(
        "schema", JSONB, nullable=False, default=dict
    )
    sources: Mapped[List[Any]] = mapped_column(JSONB, nullable=False, default=list)
    external_links: Mapped[List[Any]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    owner_group_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by: Mapped[str] = mapped_column(
        String(255), nullable=False, default="system"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_sync_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
