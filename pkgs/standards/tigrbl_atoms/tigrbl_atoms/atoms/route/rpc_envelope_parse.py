from __future__ import annotations

import json
from typing import Any, Mapping

from ... import events as _ev
from ...stages import Routed
from ...types import Atom, Ctx, RoutedCtx

ANCHOR = _ev.ROUTE_RPC_ENVELOPE_PARSE


def _route_dict(ctx: Any) -> dict[str, object]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    route_obj = temp.setdefault("route", {})
    if isinstance(route_obj, dict):
        return route_obj

    route: dict[str, object] = {}
    temp["route"] = route
    return route


def _body_from_ctx(ctx: Any) -> object | None:
    body = getattr(ctx, "body", None)
    if body is not None:
        return body

    gw_raw = getattr(ctx, "gw_raw", None)
    if gw_raw is not None:
        maybe = getattr(gw_raw, "body", None)
        if maybe is not None:
            return maybe

    return None


def _parse_json_bytes(raw: bytes) -> object | None:
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


def _normalize_rpc_dict(body: Mapping[str, object]) -> dict[str, object] | None:
    method = body.get("method")
    if not isinstance(method, str) or not method:
        return None

    out: dict[str, object] = {
        "jsonrpc": "2.0" if body.get("jsonrpc") == "2.0" else body.get("jsonrpc", "2.0"),
        "method": method,
    }

    if "params" in body:
        out["params"] = body.get("params")
    if "id" in body:
        out["id"] = body.get("id")

    return out


def _run(obj: object | None, ctx: Any) -> None:
    del obj

    route = _route_dict(ctx)
    body = _body_from_ctx(ctx)

    normalized: dict[str, object] | None = None

    if isinstance(body, Mapping):
        normalized = _normalize_rpc_dict(body)
    elif isinstance(body, (bytes, bytearray)):
        parsed = _parse_json_bytes(bytes(body))
        if isinstance(parsed, Mapping):
            normalized = _normalize_rpc_dict(parsed)

    if normalized is None:
        return

    route["rpc"] = normalized
    route["rpc_method"] = normalized.get("method")


class AtomImpl(Atom[Routed, Routed]):
    name = "route.rpc_envelope_parse"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Routed]) -> Ctx[Routed]:
        _run(obj, ctx)
        return ctx.promote(
            RoutedCtx,
            protocol=str(ctx.temp.get("route", {}).get("protocol", "") or ""),
        )


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]