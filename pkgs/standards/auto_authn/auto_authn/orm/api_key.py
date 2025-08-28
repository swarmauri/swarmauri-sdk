"""API key model for the authentication service."""

from __future__ import annotations

import hashlib
import secrets

from autoapi.v3.tables import ApiKey as ApiKeyBase
from autoapi.v3.types import UniqueConstraint, relationship
from autoapi.v3.mixins import UserMixin
from autoapi.v3 import hook_ctx


class ApiKey(ApiKeyBase, UserMixin):
    __table_args__ = (
        UniqueConstraint("digest"),
        {"extend_existing": True, "schema": "authn"},
    )

    _user = relationship(
        "auto_authn.orm.tables.User",
        back_populates="_api_keys",
        lazy="joined",  # optional: eager load to avoid N+1
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


__all__ = ["ApiKey"]
