from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from ... import events as _ev
from ...opview import ensure_schema_in, opview_from_ctx
from ...stages import Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = _ev.ROUTE_PAYLOAD_SELECT


def _is_valid_rpc_params(payload: Any) -> bool:
    if payload is None:
        return True
    if isinstance(payload, Mapping):
        return True
    return isinstance(payload, Sequence) and not isinstance(
        payload, (str, bytes, bytearray)
    )


def _set_invalid_rpc_params_error(temp: Any, payload: Any) -> None:
    if not isinstance(temp, dict):
        return
    temp["rpc_error"] = {
        "code": -32602,
        "message": "Invalid params",
        "data": {
            "reason": "JSON-RPC params must be an object or array.",
            "value_type": type(payload).__name__,
        },
    }


def _header_name_to_lookup(header_name: str) -> tuple[str, str]:
    raw = str(header_name)
    return raw, raw.lower()


def _merge_header_in_payload(ctx: Any, payload: Any) -> Any:
    if not isinstance(payload, Mapping):
        return payload

    temp = getattr(ctx, "temp", None)
    ingress = temp.get("ingress") if isinstance(temp, dict) else None
    headers = ingress.get("headers") if isinstance(ingress, dict) else None
    if not isinstance(headers, Mapping):
        return payload

    schema_in = temp.get("schema_in") if isinstance(temp, dict) else None
    if not isinstance(schema_in, Mapping):
        try:
            schema_in = ensure_schema_in(ctx, opview_from_ctx(ctx))
        except Exception:
            schema_in = None
    by_field = schema_in.get("by_field") if isinstance(schema_in, Mapping) else {}
    if not isinstance(by_field, Mapping):
        return payload

    merged = dict(payload)
    for field, meta in by_field.items():
        if not isinstance(meta, Mapping):
            continue
        header_name = meta.get("header_in")
        if not isinstance(header_name, str) or not header_name:
            continue
        exact, lowered = _header_name_to_lookup(header_name)
        value = headers.get(exact)
        if value is None:
            value = headers.get(lowered)
        if value is None:
            if bool(meta.get("header_required_in", False)) and field not in merged:
                merged[field] = None
            continue
        merged[field] = value
    return merged


def _apply_route_params(payload: Any, params: Mapping[str, Any]) -> Any:
    if not params:
        return payload
    if isinstance(payload, Mapping):
        return {**dict(payload), **dict(params)}
    if isinstance(payload, Sequence) and not isinstance(
        payload, (str, bytes, bytearray)
    ):
        out: list[Any] = []
        for item in payload:
            if isinstance(item, Mapping):
                out.append({**dict(item), **dict(params)})
            else:
                out.append(item)
        return out
    return payload


def _decode_body(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)):
        try:
            return json.loads(bytes(value).decode("utf-8"))
        except Exception:
            return None
    return value


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    route = temp.setdefault("route", {})
    route_params = (
        route.get("params") if isinstance(route.get("params"), Mapping) else {}
    )

    protocol = str(route.get("protocol") or getattr(ctx, "protocol", "") or "")
    payload_source = "empty"
    payload: Any = None

    rpc = route.get("rpc")
    if isinstance(rpc, Mapping) and protocol.endswith(".jsonrpc"):
        payload = rpc.get("params")
        if not _is_valid_rpc_params(payload):
            _set_invalid_rpc_params_error(temp, payload)
            payload = {}
        payload_source = "jsonrpc.params"
    else:
        payload = route.get("payload")
        if payload is None:
            payload = getattr(ctx, "payload", None)
            if payload is not None:
                payload_source = "body"
        if payload is None:
            ingress = (
                temp.get("ingress") if isinstance(temp.get("ingress"), dict) else {}
            )
            payload = ingress.get("body") if isinstance(ingress, dict) else None
            if payload is not None:
                payload_source = "body"

        payload = _decode_body(payload)

        if payload is None and route_params:
            payload = dict(route_params)
            payload_source = "params"

    payload = _apply_route_params(payload, route_params)
    payload = _merge_header_in_payload(ctx, payload)

    if payload_source == "empty" and payload is not None:
        payload_source = "body"

    route["payload"] = payload
    route["payload_source"] = payload_source
    setattr(ctx, "payload", payload)


class AtomImpl(Atom[Bound, Bound]):
    name = "route.payload_select"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(BoundCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
