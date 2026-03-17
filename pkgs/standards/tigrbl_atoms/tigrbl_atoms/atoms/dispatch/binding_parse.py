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

    if isinstance(body, (bytes, bytearray)):
        try:
            body = json.loads(bytes(body).decode("utf-8"))
        except Exception:
            body = None

    if not protocol and isinstance(body, Mapping) and body.get("jsonrpc") == "2.0":
        dispatch.setdefault("binding_protocol", "http.jsonrpc")
        dispatch["binding_selector"] = body.get("method")
        dispatch["rpc"] = dict(body)
        dispatch["rpc_method"] = body.get("method")
        dispatch["parsed_payload"] = body.get("params", {})
        if isinstance(route, dict):
            route["protocol"] = dispatch.get("binding_protocol")
            route["selector"] = dispatch.get("binding_selector")
            route["rpc_envelope"] = dict(body)
            route["payload"] = dispatch["parsed_payload"]
        return

    if not protocol and isinstance(body, list):
        is_jsonrpc_batch = all(
            isinstance(item, Mapping) and item.get("jsonrpc") == "2.0" for item in body
        )
        if is_jsonrpc_batch:
            dispatch["rpc_batch"] = [dict(item) for item in body]
            dispatch["parsed_payload"] = dispatch["rpc_batch"]
            if isinstance(route, dict):
                route["payload"] = dispatch["rpc_batch"]
            return

    if protocol.endswith(".jsonrpc"):
        if isinstance(body, Mapping):
            dispatch.setdefault("binding_selector", body.get("method"))
            dispatch["rpc"] = dict(body)
            dispatch["rpc_method"] = body.get("method")
            dispatch["parsed_payload"] = body.get("params", {})
            if isinstance(route, dict):
                route["selector"] = dispatch.get("binding_selector")
                route["rpc_envelope"] = dict(body)
        elif isinstance(body, list):
            dispatch["rpc_batch"] = [
                dict(item) if isinstance(item, Mapping) else item for item in body
            ]
            dispatch["parsed_payload"] = dispatch["rpc_batch"]
        if isinstance(route, dict):
            route["payload"] = body
    elif protocol.endswith(".rest"):
        if isinstance(body, (bytes, bytearray)):
            try:
                body = json.loads(bytes(body).decode("utf-8"))
            except Exception:
                body = None
        payload: dict[str, object] = {}
        query = getattr(ctx, "query", None)
        if isinstance(query, Mapping):
            payload.update({str(k): v for k, v in query.items()})
        path_params = dispatch.get("path_params")
        if isinstance(path_params, Mapping):
            payload.update({str(k): v for k, v in path_params.items()})
        if isinstance(body, Mapping):
            payload.update({str(k): v for k, v in body.items()})
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

    @staticmethod
    async def _execute_rpc_batch(
        ctx: Any, batch_payload: list[Any]
    ) -> list[dict[str, Any]]:
        router_or_app = getattr(ctx, "router", None) or getattr(ctx, "app", None)
        request = getattr(ctx, "request", None)
        rpc_call = getattr(router_or_app, "rpc_call", None)
        responses: list[dict[str, Any]] = []

        for item in batch_payload:
            if not isinstance(item, Mapping):
                responses.append(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32600, "message": "Invalid Request"},
                        "id": None,
                    }
                )
                continue

            rpc_id = item.get("id")
            method = item.get("method")
            if not isinstance(method, str) or "." not in method:
                responses.append(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": "Method not found"},
                        "id": rpc_id,
                    }
                )
                continue

            if not callable(rpc_call):
                responses.append(
                    {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": {"detail": "RPC invoker unavailable."},
                        },
                        "id": rpc_id,
                    }
                )
                continue

            model_name, op_alias = method.split(".", 1)
            params = item.get("params", {})
            if params is None:
                params = {}

            try:
                result = await rpc_call(
                    model_name,
                    op_alias,
                    params,
                    request=request,
                    ctx={},
                )
            except AttributeError:
                responses.append(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": "Method not found"},
                        "id": rpc_id,
                    }
                )
                continue
            except Exception as exc:
                responses.append(
                    {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": {"detail": str(exc)},
                        },
                        "id": rpc_id,
                    }
                )
                continue

            responses.append({"jsonrpc": "2.0", "result": result, "id": rpc_id})

        return responses

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Bound]:
        _run(obj, ctx)
        temp = getattr(ctx, "temp", None)
        dispatch = temp.get("dispatch") if isinstance(temp, dict) else None
        rpc_batch = dispatch.get("rpc_batch") if isinstance(dispatch, dict) else None
        if isinstance(rpc_batch, list):
            egress = temp.setdefault("egress", {}) if isinstance(temp, dict) else {}
            if isinstance(egress, dict):
                egress["transport_response"] = {
                    "status_code": 200,
                    "body": await self._execute_rpc_batch(ctx, rpc_batch),
                }
        return ctx.promote(BoundCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
