from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from ... import events as _ev
from ...stages import Bound, Planned
from ...types import Atom, Ctx, PlannedCtx

ANCHOR = _ev.ROUTE_OP_RESOLVE


def _default_status_for_target(target: Any) -> int:
    return 201 if target == "create" else 200


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
        if method not in (getattr(candidate, "methods", ()) or ()):  # pragma: no cover
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


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})

    plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
    opmeta = getattr(plan, "opmeta", ()) if plan is not None else ()

    bound_index = route.get("opmeta_index")
    if not isinstance(bound_index, int):
        bound_index = route.get("binding")

    if isinstance(bound_index, int) and 0 <= bound_index < len(opmeta):
        meta = opmeta[bound_index]
        route["opmeta_index"] = bound_index
        route["binding"] = bound_index
        route["resolved"] = True

        op_alias = getattr(meta, "alias", None)
        target = getattr(meta, "target", None)
        model = getattr(meta, "model", None)

        route["op"] = op_alias
        setattr(ctx, "op", op_alias)
        setattr(ctx, "target", target)
        setattr(ctx, "model", model)

        if getattr(ctx, "selector", None) is None:
            setattr(ctx, "selector", route.get("selector"))

        if getattr(ctx, "status_code", None) is None:
            setattr(ctx, "status_code", _default_status_for_target(target))

        env = getattr(ctx, "env", None)
        payload = route.get("payload")
        if env is None:
            setattr(
                ctx,
                "env",
                SimpleNamespace(
                    method=op_alias, params=payload, target=target, model=model
                ),
            )
        else:
            if getattr(env, "method", None) is None:
                setattr(env, "method", op_alias)
            if getattr(env, "params", None) is None:
                setattr(env, "params", payload)
            if getattr(env, "target", None) is None:
                setattr(env, "target", target)
            if getattr(env, "model", None) is None:
                setattr(env, "model", model)
        return

    route["resolved"] = False
    if route.get("binding") is None and not callable(route.get("handler")):
        _resolve_runtime_route_handler(ctx, route)


class AtomImpl(Atom[Bound, Planned]):
    name = "route.op_resolve"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Planned]:
        _run(obj, ctx)
        return ctx.promote(PlannedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
