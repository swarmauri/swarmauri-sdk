from __future__ import annotations

import json
from typing import Any, Mapping

from ... import events as _ev
from ...stages import Routed, Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = getattr(_ev, "ROUTE_MATCH_JSONRPC", "route.match.jsonrpc")


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


def _candidate_protocols(route: Mapping[str, object]) -> list[str]:
    value = route.get("protocol_candidates")
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        if isinstance(item, str):
            out.append(item)
    return out


def _jsonrpc_index_for(plan: Any, proto: str) -> Any:
    proto_indices = getattr(plan, "proto_indices", None)
    if isinstance(proto_indices, dict):
        return proto_indices.get(proto)

    route_data = getattr(plan, "route_data", None)
    if isinstance(route_data, dict):
        return route_data.get(proto)

    return None


def _extract_jsonrpc_envelope(route: dict[str, object], ctx: Any) -> dict[str, object] | None:
    rpc = route.get("rpc")
    if isinstance(rpc, dict):
        return rpc

    gw_raw = getattr(ctx, "gw_raw", None)
    maybe = getattr(gw_raw, "rpc", None) if gw_raw is not None else None
    if isinstance(maybe, dict):
        return maybe

    body = getattr(ctx, "body", None)
    if isinstance(body, dict):
        return body

    payload = getattr(ctx, "payload", None)
    if isinstance(payload, dict):
        return payload

    raw_body = None
    if isinstance(body, (bytes, bytearray)):
        raw_body = bytes(body)
    elif gw_raw is not None:
        maybe_body = getattr(gw_raw, "body", None)
        if isinstance(maybe_body, (bytes, bytearray)):
            raw_body = bytes(maybe_body)

    if raw_body is not None:
        try:
            parsed = json.loads(raw_body.decode("utf-8"))
        except Exception:
            return None
        if isinstance(parsed, dict):
            return parsed

    return None


def _is_jsonrpc_request(envelope: Mapping[str, object] | None) -> bool:
    if not isinstance(envelope, Mapping):
        return False
    return envelope.get("jsonrpc") == "2.0" and isinstance(envelope.get("method"), str)


def _run(obj: object | None, ctx: Any) -> None:
    del obj

    route = _route_dict(ctx)
    if bool(route.get("matched")):
        return

    candidates = _candidate_protocols(route)
    rpc_candidates = [p for p in candidates if p.endswith(".jsonrpc")]
    if not rpc_candidates:
        return

    envelope = _extract_jsonrpc_envelope(route, ctx)
    if not _is_jsonrpc_request(envelope):
        return

    rpc_method = envelope.get("method")
    if not isinstance(rpc_method, str) or not rpc_method:
        return

    plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
    if plan is None:
        return

    for proto in rpc_candidates:
        index = _jsonrpc_index_for(plan, proto)
        if not isinstance(index, Mapping):
            continue

        meta_index = index.get(rpc_method)
        if not isinstance(meta_index, int):
            continue

        route["matched"] = True
        route["protocol"] = proto
        route["binding"] = meta_index
        route["opmeta_index"] = meta_index
        route["rpc_method"] = rpc_method
        route["selector"] = rpc_method
        route["rpc"] = dict(envelope)

        setattr(ctx, "proto", proto)
        setattr(ctx, "protocol", proto)
        setattr(ctx, "binding", meta_index)
        setattr(ctx, "selector", rpc_method)
        return


class AtomImpl(Atom[Routed, Bound]):
    name = "route.match_jsonrpc"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Routed]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(
            BoundCtx,
            protocol=str(ctx.temp.get("route", {}).get("protocol", "") or ""),
            binding=ctx.temp.get("route", {}).get("binding"),
        )


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]