from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Prepared, Routed

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_PROTOCOL_DETECT


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})

    env = getattr(ctx, "gw_raw", None)
    proto = None
    if env is not None:
        transport = getattr(env, "transport", None)
        kind = getattr(env, "kind", None)
        scheme = getattr(env, "scheme", None)
        if (
            transport == "http"
            and kind in {"rest", "jsonrpc"}
            and scheme in {"http", "https"}
        ):
            proto = f"{scheme}.{kind}"
        elif transport == "ws" and scheme in {"ws", "wss"}:
            proto = scheme

    if proto is None:
        raw = getattr(ctx, "raw", None)
        scope = getattr(raw, "scope", None) if raw is not None else None
        if isinstance(scope, dict) and scope.get("type") == "http":
            scheme = str(scope.get("scheme") or "http")
            if scheme in {"http", "https"}:
                proto = f"{scheme}.rest"

    if proto is None:
        request = getattr(ctx, "request", None)
        scope = getattr(request, "scope", None) if request is not None else None
        protocol = scope.get("type") if isinstance(scope, dict) else None
        if protocol is None and request is not None:
            protocol = getattr(request, "protocol", None)
        proto = protocol

    if proto is not None:
        route["protocol"] = proto
        setattr(ctx, "proto", proto)


class AtomImpl(Atom[Prepared, Routed]):
    name = "route.protocol_detect"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Prepared]) -> Ctx[Routed]:
        _run(obj, ctx)
        return cast_ctx(ctx)

INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
