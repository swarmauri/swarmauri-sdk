"""
peagen.models.task.raw_blob
===========================

Binary or encoded attachments tied to a TaskPayload.

Design Highlights
-----------------
• Uses the global BaseModel mixin (id, date_created, last_modified).
• Belongs to exactly one TaskPayload (FK → task_payloads.id).
• `media_type` records MIME type (e.g. 'image/png', 'text/csv').
• `encoding` specifies how `data` is represented:
      'base64' | 'utf-8' | 'binary'  (extend as needed).
"""

from __future__ import annotations

import uuid
from sqlalchemy import String, LargeBinary, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .task_payload import TaskPayload

from ..base import BaseModel


class RawBlob(BaseModel):
    """
    Opaque blob packaged with a TaskPayload.
    """

    __tablename__ = "raw_blobs"

    # ──────────────────────── Columns ────────────────────────
    task_payload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task_payloads.id", ondelete="CASCADE"),
        nullable=False,
    )

    media_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="RFC6838 media type, e.g., 'application/json', 'image/jpeg'",
    )

    encoding: Mapped[str] = mapped_column(
        Enum("utf-8", "base64", "binary", name="blob_encoding_enum"),
        nullable=False,
        default="binary",
    )

    data: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
        doc="Raw bytes (already base64-decoded if encoding == 'binary')",
    )

    # ──────────────────── Relationships ──────────────────────
    task_payload: Mapped["TaskPayload"] = relationship(
        "TaskPayload", back_populates="raw_blobs", lazy="selectin"
    )

    # ─────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<RawBlob id={self.id} payload={self.task_payload_id} "
            f"type={self.media_type!r} enc={self.encoding}>"
        )
