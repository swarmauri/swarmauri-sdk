from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_OP_RESOLVE


def _default_status_for_target(target: Any) -> int:
    return 201 if target == "create" else 200


def _resolve_opmeta_index(ctx: Any, route: dict[str, Any]) -> int | None:
    plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
    opmeta = getattr(plan, "opmeta", ()) if plan is not None else ()

    if isinstance(route.get("opmeta_index"), int):
        idx = int(route["opmeta_index"])
        if 0 <= idx < len(opmeta):
            return idx

    if isinstance(getattr(ctx, "op_index", None), int):
        idx = int(ctx.op_index)
        if 0 <= idx < len(opmeta):
            return idx

    proto = getattr(ctx, "proto", None)
    selector = getattr(ctx, "selector", None)
    opkey_to_meta = getattr(plan, "opkey_to_meta", None)
    if (
        isinstance(proto, str)
        and isinstance(selector, str)
        and isinstance(opkey_to_meta, dict)
    ):
        key = (proto, selector)
        for opkey, idx in opkey_to_meta.items():
            if (getattr(opkey, "proto", None), getattr(opkey, "selector", None)) != key:
                continue
            if isinstance(idx, int) and 0 <= idx < len(opmeta):
                return idx

    maybe_index = route.get("binding")
    if isinstance(maybe_index, int) and 0 <= maybe_index < len(opmeta):
        return maybe_index
    return None


def _resolve_runtime_route_handler(ctx: Any, route: dict[str, Any]) -> None:
    request = getattr(ctx, "request", None)
    app = getattr(ctx, "app", None)
    method = str(getattr(request, "method", "")).upper()
    path = getattr(request, "path", None) or getattr(
        getattr(request, "url", None), "path", None
    )
    if not method or not isinstance(path, str) or app is None:
        return

    method_not_allowed = False
    for candidate in getattr(app, "routes", ()) or ():
        pattern = getattr(candidate, "pattern", None)
        if pattern is None:
            continue
        matched = pattern.match(path)
        if matched is None:
            continue
        if method not in (getattr(candidate, "methods", ()) or ()):
            method_not_allowed = True
            continue

        handler = getattr(candidate, "handler", None)
        if not callable(handler):
            continue

        route["handler"] = handler
        route["path_params"] = dict(matched.groupdict())
        return

    if method_not_allowed:
        route["method_not_allowed"] = True


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})

    maybe_index = _resolve_opmeta_index(ctx, route)
    if isinstance(maybe_index, int):
        plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
        opmeta = getattr(plan, "opmeta", ()) if plan is not None else ()
        if 0 <= maybe_index < len(opmeta):
            meta = opmeta[maybe_index]
            route["opmeta_index"] = maybe_index
            op_alias = getattr(meta, "alias", None)
            route["op"] = op_alias
            setattr(ctx, "op", op_alias)
            setattr(ctx, "model", getattr(meta, "model", None))
            env = getattr(ctx, "env", None)
            if env is None:
                payload = route.get("payload") if isinstance(route, dict) else None
                if payload is None:
                    payload = getattr(ctx, "payload", None)
                setattr(
                    ctx,
                    "env",
                    SimpleNamespace(
                        method=op_alias,
                        params=payload,
                        target=getattr(meta, "target", None),
                        model=getattr(meta, "model", None),
                    ),
                )
            else:
                # Keep pre-seeded environment objects but ensure routing metadata
                # is always available to downstream hooks.
                if getattr(env, "method", None) is None:
                    setattr(env, "method", op_alias)
                if getattr(env, "target", None) is None:
                    setattr(env, "target", getattr(meta, "target", None))
                if getattr(env, "model", None) is None:
                    setattr(env, "model", getattr(meta, "model", None))
            if getattr(ctx, "status_code", None) is None:
                setattr(
                    ctx,
                    "status_code",
                    _default_status_for_target(getattr(meta, "target", None)),
                )
            return

    if "op" not in route:
        route["op"] = getattr(ctx, "op", None)

    if route.get("opmeta_index") is None and not callable(route.get("handler")):
        _resolve_runtime_route_handler(ctx, route)
