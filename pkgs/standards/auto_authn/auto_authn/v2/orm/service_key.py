"""Service key model for the authentication service."""

from __future__ import annotations

import hashlib
import secrets

from autoapi.v3.tables import ApiKey as ApiKeyBase
from autoapi.v3.types import PgUUID, UniqueConstraint, relationship
from autoapi.v3.specs import IO, S, acol, vcol
from autoapi.v3.specs.storage_spec import ForeignKeySpec
from autoapi.v3 import hook_ctx
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .service import Service


class ServiceKey(ApiKeyBase):
    __tablename__ = "service_keys"
    __table_args__ = (
        UniqueConstraint("digest"),
        {"extend_existing": True, "schema": "authn"},
    )
    service_id: UUID = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="authn.services.id"),
            index=True,
            nullable=False,
        )
    )

    _service = relationship(
        "auto_authn.v2.orm.service.Service",
        back_populates="_service_keys",
        lazy="joined",
        primaryjoin="ServiceKey.service_id == Service.id",
        foreign_keys="ServiceKey.service_id",
    )
    service: "Service" = vcol(
        read_producer=lambda obj, _ctx: obj._service,
        io=IO(out_verbs=("read", "list")),
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
