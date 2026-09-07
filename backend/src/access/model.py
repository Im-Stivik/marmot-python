from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class TableGrant(Base):
    """Maps which assets a group can see."""

    __tablename__ = "table_grants"

    asset_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("assets.id", ondelete="CASCADE"),
        primary_key=True,
    )
    group_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
