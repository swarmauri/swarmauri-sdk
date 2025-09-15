"""Pushed authorization request model and helpers."""

from __future__ import annotations

import datetime as dt
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
            io=IO(in_verbs=("create",)),
        )
    )
    params: Mapped[dict] = acol(
        spec=ColumnSpec(
            storage=S(JSON, nullable=False),
            field=F(),
            io=IO(in_verbs=("create",)),
        )
    )
    expires_in: Mapped[int] = acol(
        spec=ColumnSpec(
            storage=S(Integer, nullable=False, default=_default_expires_in),
            field=F(),
            io=IO(in_verbs=("create",)),
        )
    )
    expires_at: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(TZDateTime, nullable=False, default=_default_expires_at),
            field=F(),
            io=IO(in_verbs=("create",)),
        )
    )

    @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
    async def _extract_form_params(cls, ctx):
        from ..runtime_cfg import settings

        if not settings.enable_rfc9126:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "PAR disabled")
        payload = ctx.get("payload") or {}
        if payload.get("params"):
            ctx["payload"] = payload
            return
        request = ctx.get("request")
        if not request:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "missing request body")
        form = await request.form()
        if form:
            payload["params"] = dict(form)
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "missing params")
        ctx["payload"] = payload

    @hook_ctx(ops=("read", "list"), phase="POST_HANDLER")
    async def _expire_on_read(cls, ctx):
        now = datetime.now(tz=timezone.utc)
        result = ctx.get("result")

        def _is_expired(obj) -> bool:
            exp = obj.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            return now > exp

        if result is None:
            return
        if getattr(result, "items", None) is not None:
            for obj in list(result.items):
                if _is_expired(obj):
                    await cls.handlers.delete.core({"obj": obj})
                    result.items.remove(obj)
        elif isinstance(result, list):
            for obj in list(result):
                if _is_expired(obj):
                    await cls.handlers.delete.core({"obj": obj})
                    result.remove(obj)
        else:
            if _is_expired(result):
                await cls.handlers.delete.core({"obj": result})
                ctx["result"] = None


__all__ = ["PushedAuthorizationRequest", "DEFAULT_PAR_EXPIRY"]
