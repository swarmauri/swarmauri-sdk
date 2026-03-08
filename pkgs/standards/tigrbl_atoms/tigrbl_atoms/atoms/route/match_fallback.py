from __future__ import annotations

from typing import Any, Mapping

from ... import events as _ev
from ...stages import Routed, Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = getattr(_ev, "ROUTE_MATCH_FALLBACK", "route.match.fallback")


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


def _http_method_path(ctx: Any) -> tuple[str, str] | None:
    method = getattr(ctx, "method", None)
    path = getattr(ctx, "path", None)

    request = getattr(ctx, "request", None)
    if not isinstance(method, str) and request is not None:
        maybe = getattr(request, "method", None)
        if isinstance(maybe, str):
            method = maybe

    if not isinstance(path, str) and request is not None:
        maybe = getattr(request, "path", None)
        if isinstance(maybe, str):
            path = maybe
        else:
            url = getattr(request, "url", None)
            maybe = getattr(url, "path", None) if url is not None else None
            if isinstance(maybe, str):
                path = maybe

    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None) if raw is not None else None
    if isinstance(scope, Mapping):
        if not isinstance(method, str):
            maybe = scope.get("method")
            if isinstance(maybe, str):
                method = maybe
        if not isinstance(path, str):
            maybe = scope.get("path")
            if isinstance(maybe, str):
                path = maybe

    if isinstance(method, str) and isinstance(path, str):
        return method.upper(), path
    return None


def _resolve_runtime_route_handler(ctx: Any, route: dict[str, object]) -> None:
    app = getattr(ctx, "app", None)
    method_path = _http_method_path(ctx)
    if app is None or method_path is None:
        return

    method, path = method_path
    method_not_allowed = False

    for candidate in getattr(app, "routes", ()) or ():
        pattern = getattr(candidate, "pattern", None)
        if pattern is None:
            continue

        matched = pattern.match(path)
        if matched is None:
            continue

        allowed = getattr(candidate, "methods", ()) or ()
        if method not in allowed:
            method_not_allowed = True
            continue

        handler = getattr(candidate, "handler", None)
        if not callable(handler):
            continue

        route["handler"] = handler
        route["matched"] = False
        route["binding"] = None
        route["path_params"] = dict(matched.groupdict())
        return

    if method_not_allowed:
        route["method_not_allowed"] = True


def _run(obj: object | None, ctx: Any) -> None:
    del obj

    route = _route_dict(ctx)
    if bool(route.get("matched")):
        return

    route.setdefault("binding", None)
    route.setdefault("opmeta_index", None)
    route.setdefault("selector", "")
    route.setdefault("path_params", {})

    _resolve_runtime_route_handler(ctx, route)


class AtomImpl(Atom[Routed, Bound]):
    name = "route.match_fallback"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Routed]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(
            BoundCtx,
            protocol=str(ctx.temp.get("route", {}).get("protocol", "") or ""),
            path_params=dict(ctx.temp.get("route", {}).get("path_params", {}) or {}),
            binding=ctx.temp.get("route", {}).get("binding"),
        )


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
