from __future__ import annotations

from typing import Any, Mapping

from ... import events as _ev
from ...stages import Routed, Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = _ev.ROUTE_SELECTOR_RESOLVE


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


def _scope_from_ctx(ctx: Any) -> Mapping[str, object]:
    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None) if raw is not None else None
    if isinstance(scope, Mapping):
        return scope
    request = getattr(ctx, "request", None)
    scope = getattr(request, "scope", None) if request is not None else None
    return scope if isinstance(scope, Mapping) else {}


def _path(ctx: Any) -> str:
    p = getattr(ctx, "path", None)
    if isinstance(p, str) and p:
        return p
    scope = _scope_from_ctx(ctx)
    value = scope.get("path", "/")
    return str(value) if isinstance(value, str) else "/"


def _method(ctx: Any) -> str:
    m = getattr(ctx, "method", None)
    if isinstance(m, str) and m:
        return m.upper()
    scope = _scope_from_ctx(ctx)
    value = scope.get("method", "")
    return str(value).upper() if isinstance(value, str) else ""


def _rpc_method(route: Mapping[str, object], ctx: Any) -> str | None:
    value = route.get("rpc_method")
    if isinstance(value, str) and value:
        return value
    rpc = route.get("rpc")
    if isinstance(rpc, Mapping):
        value = rpc.get("method")
        if isinstance(value, str) and value:
            return value
    body = getattr(ctx, "body", None)
    if isinstance(body, Mapping):
        value = body.get("method")
        if isinstance(value, str) and value:
            return value
    return None


def _selector_ids(plan: Any):
    packed = getattr(plan, "packed", None)
    return getattr(packed, "selector_to_id", {}) if packed is not None else {}


def _proto_ids(plan: Any):
    packed = getattr(plan, "packed", None)
    return getattr(packed, "proto_to_id", {}) if packed is not None else {}


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    route = _route_dict(ctx)
    plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
    proto_indices = getattr(plan, "proto_indices", {}) if plan is not None else {}
    candidates = route.get("protocol_candidates")
    protocols = [p for p in candidates if isinstance(p, str)] if isinstance(candidates, list) else []
    if not protocols:
        p = route.get("protocol")
        if isinstance(p, str) and p:
            protocols = [p]

    matched_proto: str | None = None
    matched_selector: str | None = None
    matched_path_params: dict[str, object] = {}
    method = _method(ctx)
    path = _path(ctx)

    for proto in protocols:
        bucket = proto_indices.get(proto) if isinstance(proto_indices, Mapping) else None
        if proto.endswith('.jsonrpc'):
            rpc_method = _rpc_method(route, ctx)
            if isinstance(bucket, Mapping) and isinstance(rpc_method, str) and rpc_method in bucket:
                matched_proto = proto
                matched_selector = rpc_method
                break
        elif proto.endswith('.rest'):
            if isinstance(bucket, Mapping):
                exact = bucket.get('exact')
                selector = f"{method} {path}"
                if isinstance(exact, Mapping) and selector in exact:
                    matched_proto = proto
                    matched_selector = selector
                    break
                templated = bucket.get('templated')
                if isinstance(templated, list):
                    allowed_same_path = False
                    for entry in templated:
                        if not isinstance(entry, Mapping):
                            continue
                        pattern = entry.get('pattern')
                        names = entry.get('names')
                        entry_method = str(entry.get('method', '') or '').upper()
                        if entry_method and entry_method != method:
                            candidate_pattern = pattern
                            if candidate_pattern is not None and hasattr(candidate_pattern, 'match') and candidate_pattern.match(path):
                                allowed_same_path = True
                            continue
                        if pattern is None or not hasattr(pattern, 'match'):
                            continue
                        m = pattern.match(path)
                        if m is None:
                            continue
                        matched_proto = proto
                        matched_selector = str(entry.get('selector') or selector)
                        if isinstance(names, (list, tuple)):
                            matched_path_params = {str(name): value for name, value in zip(names, m.groups())}
                        break
                    if matched_selector is not None:
                        break
                    if allowed_same_path:
                        route['method_not_allowed'] = True
        else:
            if isinstance(bucket, Mapping):
                exact = bucket.get('exact')
                if isinstance(exact, Mapping) and path in exact:
                    matched_proto = proto
                    matched_selector = path
                    break
                templated = bucket.get('templated')
                if isinstance(templated, list):
                    for entry in templated:
                        if not isinstance(entry, Mapping):
                            continue
                        pattern = entry.get('pattern')
                        names = entry.get('names')
                        if pattern is None or not hasattr(pattern, 'match'):
                            continue
                        m = pattern.match(path)
                        if m is None:
                            continue
                        matched_proto = proto
                        matched_selector = str(entry.get('selector') or path)
                        if isinstance(names, (list, tuple)):
                            matched_path_params = {str(name): value for name, value in zip(names, m.groups())}
                        break
                    if matched_selector is not None:
                        break

    if matched_proto is not None:
        route['protocol'] = matched_proto
        route['matched'] = True
        setattr(ctx, 'proto', matched_proto)
        setattr(ctx, 'protocol', matched_proto)
        temp = getattr(ctx, 'temp', {})
        if isinstance(temp, dict):
            temp['proto'] = matched_proto
        proto_to_id = _proto_ids(plan)
        if isinstance(proto_to_id, Mapping) and matched_proto in proto_to_id:
            route['proto_id'] = int(proto_to_id[matched_proto])
            temp['proto_id'] = int(proto_to_id[matched_proto])

    if matched_selector is not None:
        route['selector'] = matched_selector
        setattr(ctx, 'selector', matched_selector)
        temp = getattr(ctx, 'temp', {})
        if isinstance(temp, dict):
            temp['selector'] = matched_selector
        selector_to_id = _selector_ids(plan)
        if isinstance(selector_to_id, Mapping) and matched_selector in selector_to_id:
            route['selector_id'] = int(selector_to_id[matched_selector])
            temp['selector_id'] = int(selector_to_id[matched_selector])

    if matched_path_params:
        route['path_params'] = matched_path_params
        setattr(ctx, 'path_params', matched_path_params)


class AtomImpl(Atom[Routed, Bound]):
    name = "route.selector_resolve"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Routed]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(
            BoundCtx,
            protocol=str(ctx.temp.get('route', {}).get('protocol', '') or ''),
            path_params=dict(ctx.temp.get('route', {}).get('path_params', {}) or {}),
            binding=ctx.temp.get('route', {}).get('binding'),
        )


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
