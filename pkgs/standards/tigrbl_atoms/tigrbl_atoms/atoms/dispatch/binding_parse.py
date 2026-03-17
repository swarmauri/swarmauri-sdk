from __future__ import annotations

import json
from typing import Any, Mapping

from ... import events as _ev
from ...stages import Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = _ev.DISPATCH_BINDING_PARSE


def _dispatch_dict(ctx: Any) -> dict[str, object]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    obj = temp.setdefault("dispatch", {})
    if isinstance(obj, dict):
        return obj
    temp["dispatch"] = {}
    return temp["dispatch"]


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    dispatch = _dispatch_dict(ctx)
    temp = getattr(ctx, "temp", None)
    route = temp.setdefault("route", {}) if isinstance(temp, dict) else {}
    protocol = str(dispatch.get("binding_protocol", "") or "")
    body = getattr(ctx, "body", None)

    if not protocol and isinstance(body, (bytes, bytearray)):
        try:
            body = json.loads(bytes(body).decode("utf-8"))
        except Exception:
            pass

    if not protocol and isinstance(body, Mapping) and body.get("jsonrpc"):
        dispatch["rpc"] = dict(body)
        dispatch["rpc_method"] = body.get("method")
        dispatch["parsed_payload"] = body.get("params", {})
        if isinstance(route, dict):
            route["rpc_envelope"] = dict(body)
            route["payload"] = dispatch["parsed_payload"]
        return

    if protocol.endswith(".jsonrpc"):
        if isinstance(body, (bytes, bytearray)):
            try:
                body = json.loads(bytes(body).decode("utf-8"))
            except Exception:
                body = None
        if isinstance(body, Mapping):
            dispatch["rpc"] = dict(body)
            dispatch["rpc_method"] = body.get("method")
            dispatch["parsed_payload"] = body.get("params", {})
            if isinstance(route, dict):
                route["rpc_envelope"] = dict(body)
        elif isinstance(body, list):
            dispatch["rpc_batch"] = body
            dispatch["parsed_payload"] = body
        if isinstance(route, dict):
            route["payload"] = body
    elif protocol.endswith(".rest"):
        payload: dict[str, object] = {}
        query = getattr(ctx, "query", None)
        if isinstance(query, Mapping):
            payload.update({str(k): v for k, v in query.items()})
        path_params = dispatch.get("path_params")
        if isinstance(path_params, Mapping):
            payload.update({str(k): v for k, v in path_params.items()})

        rest_body = body
        if isinstance(rest_body, (bytes, bytearray)):
            try:
                rest_body = json.loads(bytes(rest_body).decode("utf-8"))
            except Exception:
                rest_body = None

        if rest_body is None:
            ingress = temp.get("ingress") if isinstance(temp, dict) else None
            if isinstance(ingress, Mapping):
                candidate = ingress.get("body_json")
                if isinstance(candidate, Mapping):
                    rest_body = candidate

        if isinstance(rest_body, Mapping):
            payload.update({str(k): v for k, v in rest_body.items()})
        dispatch["parsed_payload"] = payload
        if isinstance(route, dict):
            route["payload"] = payload
    else:
        dispatch["parsed_payload"] = body
        if isinstance(route, dict):
            route["payload"] = body


class AtomImpl(Atom[Bound, Bound]):
    name = "dispatch.binding_parse"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(BoundCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
