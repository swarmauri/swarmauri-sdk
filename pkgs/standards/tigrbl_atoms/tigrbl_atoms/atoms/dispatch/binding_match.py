from __future__ import annotations

from typing import Any, Mapping

from ... import events as _ev
from ...stages import Ingress, Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = _ev.DISPATCH_BINDING_MATCH


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


def _method(ctx: Any) -> str:
    return str(getattr(ctx, "method", "") or "").upper()


def _path(ctx: Any) -> str:
    return str(getattr(ctx, "path", "/") or "/")


def _rpc_method(dispatch: Mapping[str, object], ctx: Any) -> str | None:
    rpc = dispatch.get("rpc")
    if isinstance(rpc, Mapping):
        method = rpc.get("method")
        if isinstance(method, str):
            return method
    body_json = dispatch.get("body_json")
    if isinstance(body_json, Mapping):
        method = body_json.get("method")
        if isinstance(method, str):
            return method
    body = getattr(ctx, "body", None)
    if isinstance(body, (bytes, bytearray)):
        try:
            import json

            decoded = json.loads(bytes(body).decode("utf-8"))
        except Exception:
            decoded = None
        if isinstance(decoded, Mapping):
            method = decoded.get("method")
            if isinstance(method, str):
                return method
    if isinstance(body, Mapping):
        method = body.get("method")
        if isinstance(method, str):
            return method
    return None


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    dispatch = _dispatch_dict(ctx)
    temp = getattr(ctx, "temp", None)
    route = temp.setdefault("route", {}) if isinstance(temp, dict) else {}
    plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
    proto_indices = getattr(plan, "proto_indices", {}) if plan is not None else {}

    method = _method(ctx)
    path = _path(ctx)
    rpc_method = _rpc_method(dispatch, ctx)

    matched_proto: str | None = None
    matched_selector: str | None = None
    matched_path_params: dict[str, object] = {}

    if isinstance(proto_indices, Mapping):
        for proto, bucket in proto_indices.items():
            if not isinstance(proto, str) or not isinstance(bucket, Mapping):
                continue
            if (
                proto.endswith(".jsonrpc")
                and isinstance(rpc_method, str)
                and rpc_method in bucket
            ):
                matched_proto = proto
                matched_selector = rpc_method
                break
            if proto.endswith(".rest"):
                exact = bucket.get("exact")
                selector = f"{method} {path}"
                if isinstance(exact, Mapping) and selector in exact:
                    matched_proto = proto
                    matched_selector = selector
                    break
                templated = bucket.get("templated")
                if isinstance(templated, list):
                    for entry in templated:
                        if not isinstance(entry, Mapping):
                            continue
                        pattern = entry.get("pattern")
                        if pattern is None or not hasattr(pattern, "match"):
                            continue
                        m = pattern.match(path)
                        if m is None:
                            continue
                        entry_method = str(entry.get("method", "") or "").upper()
                        if entry_method and entry_method != method:
                            continue
                        matched_proto = proto
                        matched_selector = str(entry.get("selector") or selector)
                        names = entry.get("names")
                        if isinstance(names, (list, tuple)):
                            matched_path_params = {
                                str(name): value
                                for name, value in zip(names, m.groups())
                            }
                        break
                    if matched_selector is not None:
                        break
            if proto in {"ws", "wss"}:
                exact = bucket.get("exact")
                if isinstance(exact, Mapping) and path in exact:
                    matched_proto = proto
                    matched_selector = path
                    break

    if matched_proto is not None:
        dispatch["binding_protocol"] = matched_proto
        if isinstance(route, dict):
            route["protocol"] = matched_proto
        setattr(ctx, "protocol", matched_proto)
    if matched_selector is not None:
        dispatch["binding_selector"] = matched_selector
        if isinstance(route, dict):
            route["selector"] = matched_selector
        setattr(ctx, "selector", matched_selector)
    if matched_path_params:
        dispatch["path_params"] = matched_path_params
        if isinstance(route, dict):
            route["path_params"] = matched_path_params
        setattr(ctx, "path_params", matched_path_params)


class AtomImpl(Atom[Ingress, Bound]):
    name = "dispatch.binding_match"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(BoundCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
