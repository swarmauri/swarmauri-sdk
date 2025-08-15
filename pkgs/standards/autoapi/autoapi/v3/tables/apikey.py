from __future__ import annotations


from datetime import datetime, timezone
from hashlib import sha256
from secrets import token_urlsafe

from fastapi import HTTPException

from ..types import (
    Column,
    String,
    HookProvider,
    Field,
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
    HookProvider,
    ResponseExtrasProvider,
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

    __autoapi_response_extras__ = {"*": {"api_key": (str | None, Field(None))}}

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

    @classmethod
    async def _post_response_inject(cls, ctx):
        raw = ctx.pop("raw_api_key", None)
        if not raw:
            return
        res = getattr(ctx.get("response"), "result", None)
        if isinstance(res, dict):
            result = dict(res)
        elif hasattr(res, "__dict__"):
            result = {k: v for k, v in res.__dict__.items() if not k.startswith("_")}
        else:  # pragma: no cover - defensive
            result = {"result": res}
        result = {k: v for k, v in result.items() if v is not None}
        result["api_key"] = raw
        ctx["response"].result = result

    @classmethod
    def __autoapi_register_hooks__(cls, api) -> None:
        model = cls.__name__
        api.register_hook("PRE_TX_BEGIN", model=model, op="create")(
            cls._pre_create_generate
        )
        api.register_hook("POST_RESPONSE", model=model, op="create")(
            cls._post_response_inject
        )
