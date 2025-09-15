"""Pushed authorization request model and helpers."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from tigrbl_auth.deps import (
    Base,
    Timestamped,
    S,
    acol,
    JSON,
    Mapped,
    String,
    Integer,
    TZDateTime,
    GUIDPk,
    ColumnSpec,
    F,
    IO,
    hook_ctx,
    op_ctx,
    HTTPException,
    status,
)


DEFAULT_PAR_EXPIRY = 90  # seconds


def _default_request_uri() -> str:
    return f"urn:ietf:params:oauth:request_uri:{uuid.uuid4()}"


def _default_expires_in() -> int:
    return DEFAULT_PAR_EXPIRY


def _default_expires_at() -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(seconds=_default_expires_in())


class PushedAuthorizationRequest(Base, GUIDPk, Timestamped):
    """ORM model backing RFC 9126 pushed authorization requests."""

    __tablename__ = "par_requests"
    __table_args__ = ({"schema": "authn"},)

    request_uri: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(
                String(255),
                nullable=False,
                unique=True,
                default=_default_request_uri,
            ),
            field=F(),
            io=IO(out_verbs=("create",)),
        )
    )
    params: Mapped[dict] = acol(
        spec=ColumnSpec(
            storage=S(JSON, nullable=False),
            field=F(),
            io=IO(),
        )
    )
    expires_in: Mapped[int] = acol(
        spec=ColumnSpec(
            storage=S(Integer, nullable=False, default=_default_expires_in),
            field=F(),
            io=IO(out_verbs=("create",)),
        )
    )
    expires_at: Mapped[datetime] = acol(
        spec=ColumnSpec(
            storage=S(TZDateTime, nullable=False, default=_default_expires_at),
            field=F(),
            io=IO(),
        )
    )

    @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
    async def _extract_form(cls, ctx):
        request = ctx.get("request")
        if request is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "request required")
        form = await request.form()
        if not form:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "form required")
        ctx["payload"] = {"params": dict(form)}

    @hook_ctx(ops=("read", "list"), phase="POST_HANDLER")
    async def _cleanup_expired(cls, ctx):
        now = datetime.now(tz=timezone.utc)

        async def expired(obj):
            expires_at = obj.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            return now > expires_at

        result = ctx.get("result")
        if getattr(result, "items", None) is not None:
            remaining = []
            for obj in result.items:
                if await expired(obj):
                    await cls.handlers.delete.core({"obj": obj})
                else:
                    remaining.append(obj)
            result.items = remaining
        elif result is not None and await expired(result):
            await cls.handlers.delete.core({"obj": result})
            ctx["result"] = None

    @op_ctx(
        alias="par",
        target="create",
        arity="collection",
        status_code=status.HTTP_201_CREATED,
        rest=False,
    )
    async def par(cls, ctx):
        from ..runtime_cfg import settings

        if not settings.enable_rfc9126:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "PAR disabled")
        obj = await cls.handlers.create.core(
            {"payload": ctx.get("payload"), "db": ctx.get("db")}
        )
        return {"request_uri": obj.request_uri, "expires_in": obj.expires_in}


__all__ = ["PushedAuthorizationRequest", "DEFAULT_PAR_EXPIRY"]
