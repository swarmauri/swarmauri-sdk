"""Service key model for the authentication service."""

from __future__ import annotations

import hashlib
import secrets

from autoapi.v3.tables import ApiKey as ApiKeyBase
from autoapi.v3.types import PgUUID, UniqueConstraint, relationship
from autoapi.v3 import hook_ctx
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    pass


class ServiceKey(ApiKeyBase):
    __tablename__ = "service_keys"
    __table_args__ = (
        UniqueConstraint("digest"),
        {"extend_existing": True, "schema": "authn"},
    )

    service_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.services.id"),
        index=True,
        nullable=False,
    )

    _service = relationship(
        "Service",
        back_populates="_service_keys",
        lazy="joined",
    )

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    async def _generate_digest(cls, ctx):
        payload = ctx.get("payload") or {}
        token = secrets.token_urlsafe(32)
        payload["digest"] = hashlib.sha256(token.encode()).hexdigest()
        ctx["raw_key"] = token

    @hook_ctx(ops="create", phase="POST_RESPONSE")
    async def _return_raw_key(cls, ctx):
        raw = ctx.get("raw_key")
        result = ctx.get("result")
        if not raw or result is None:
            return
        if hasattr(result, "model_dump"):
            data = result.model_dump()
        elif hasattr(result, "dict") and callable(result.dict):
            data = result.dict()  # type: ignore[call-arg]
        else:
            data = dict(result)
        data["raw_key"] = raw
        ctx["result"] = data


__all__ = ["ServiceKey"]
