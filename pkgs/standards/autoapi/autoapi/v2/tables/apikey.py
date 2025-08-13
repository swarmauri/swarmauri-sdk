from __future__ import annotations


from datetime import datetime, timezone
from hashlib import sha256
from secrets import token_urlsafe

from fastapi import HTTPException

from ..types import (
    Column,
    String,
    HookProvider,
    ResponseExtrasProvider,
)
from ._base import Base
from ..mixins import (
    GUIDPk,
    Created,
    LastUsed,
    ValidityWindow,
)


# ------------------------------------------------------------------ model
class ApiKey(
    Base,
    GUIDPk,
    Created,
    LastUsed,
    ValidityWindow,
    ResponseExtrasProvider,
    HookProvider,
):
    __tablename__ = "api_keys"
    __abstract__ = True

    label = Column(String(120), nullable=False)

    digest = Column(
        String(64),
        nullable=False,
        unique=True,
        info={
            "autoapi": {
                # hide from Update / Replace verbs
                "disable_on": ["update", "replace"],
                # show in READ / LIST responses only
                "read_only": True,
            }
        },
    )

    # ------------------------------------------------------------------
    # Digest helpers
    # ------------------------------------------------------------------
    @staticmethod
    def digest_of(value: str) -> str:
        return sha256(value.encode()).hexdigest()

    @property
    def raw_key(self) -> str:  # pragma: no cover - write-only
        raise AttributeError("raw_key is write-only")

    @raw_key.setter
    def raw_key(self, value: str) -> None:
        self.digest = self.digest_of(value)

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------
    @classmethod
    async def _pre_create_generate(cls, ctx):
        params = ctx["env"].params
        raw = token_urlsafe(32)
        digest = cls.digest_of(raw)
        now = datetime.now(timezone.utc)
        if hasattr(params, "model_dump"):
            params = params.model_dump()
        else:  # pragma: no cover - defensive
            params = dict(params)
        if params.get("digest"):
            raise HTTPException(status_code=422, detail="digest is server generated")
        params["digest"] = digest
        params["last_used_at"] = now
        ctx["env"].params = params
        ctx["raw_api_key"] = raw

    @staticmethod
    def _inject_raw_key(ctx, res):
        raw = ctx.pop("raw_api_key", None)
        return {"api_key": raw} if raw else {}

    __autoapi_response_extras__ = {"create": _inject_raw_key}

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        from autoapi.v2 import Phase

        model = cls.__name__
        api.register_hook(Phase.PRE_TX_BEGIN, model=model, op="create")(
            cls._pre_create_generate
        )
