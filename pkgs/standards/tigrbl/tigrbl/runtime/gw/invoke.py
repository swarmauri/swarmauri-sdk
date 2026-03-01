from __future__ import annotations

import json
from typing import Any, Mapping

from ..executor import _Ctx, _invoke
from ..kernel.core import Kernel
from .raw import GwRawEnvelope


async def invoke(env: GwRawEnvelope, *, app: Any | None = None) -> None:
    app = app if app is not None else _resolve_app(env)
    if app is None:
        return

    scope_type = env.scope.get("type")
    if scope_type == "lifespan":
        await _handle_lifespan(app, env)
        return
    if scope_type != "http":
        return

    kernel = Kernel()
    plan = kernel.kernel_plan(app)
    ctx = _Ctx.ensure(request=None, db=None)
    ctx.app = app
    ctx.router = app
    ctx.raw = env
    ctx.kernel_plan = plan

    await _run_phase_chain(ctx, plan.ingress_chain)

    opmeta_index = _resolve_op_index(ctx, plan)
    if opmeta_index is None:
        await _send_json(env, 404, {"detail": "No runtime operation matched request."})
        return

    opmeta = plan.opmeta[opmeta_index]
    ctx.model = opmeta.model
    ctx.op = opmeta.alias
    ctx.opview = kernel.get_opview(app, opmeta.model, opmeta.alias)

    phases = _without_ingress_phases(plan.phase_chains.get(opmeta_index, {}))
    await _invoke(request=None, db=None, phases=phases, ctx=ctx)

    egress = ctx.temp.get("egress", {}) if isinstance(ctx.temp, dict) else {}
    response = egress.get("transport_response") if isinstance(egress, dict) else None
    if isinstance(response, dict):
        await _send_transport_response(env, response)
        return

    status = int(getattr(ctx, "status_code", 200) or 200)
    await _send_json(env, status, getattr(ctx, "result", None))


def _resolve_app(env: GwRawEnvelope) -> Any | None:
    app = env.scope.get("app")
    if app is None:
        app = env.scope.get("tigrbl.app")
    return app


def _resolve_op_index(ctx: _Ctx, plan: Any) -> int | None:
    if isinstance(getattr(ctx, "op_index", None), int):
        idx = int(ctx.op_index)
        if 0 <= idx < len(plan.opmeta):
            return idx

    proto = getattr(ctx, "proto", None)
    selector = getattr(ctx, "selector", None)
    if isinstance(proto, str) and isinstance(selector, str):
        key = (proto, selector)
        for opkey, idx in plan.opkey_to_meta.items():
            if (opkey.proto, opkey.selector) == key:
                return idx

    route = ctx.temp.get("route", {}) if isinstance(ctx.temp, dict) else {}
    idx = route.get("opmeta_index") if isinstance(route, dict) else None
    if isinstance(idx, int) and 0 <= idx < len(plan.opmeta):
        return idx
    return None


async def _run_phase_chain(ctx: _Ctx, phases: Any) -> None:
    for _phase, steps in (phases or {}).items():
        for step in steps or ():
            rv = step(ctx)
            if hasattr(rv, "__await__"):
                await rv


def _without_ingress_phases(phases: Mapping[str, Any] | None) -> dict[str, Any]:
    if not phases:
        return {}
    ingress = {"INGRESS_BEGIN", "INGRESS_PARSE", "INGRESS_ROUTE"}
    return {phase: steps for phase, steps in phases.items() if phase not in ingress}


async def _send_transport_response(
    env: GwRawEnvelope, response: dict[str, Any]
) -> None:
    status = int(response.get("status_code", 200) or 200)
    headers_obj = response.get("headers")
    headers: list[tuple[bytes, bytes]] = []
    if isinstance(headers_obj, dict):
        headers = [
            (str(k).encode("latin-1"), str(v).encode("latin-1"))
            for k, v in headers_obj.items()
        ]
    body = response.get("body", b"")
    if isinstance(body, str):
        body = body.encode("utf-8")
    elif body is None:
        body = b""
    elif not isinstance(body, (bytes, bytearray)):
        body = json.dumps(body).encode("utf-8")

    await env.send(
        {"type": "http.response.start", "status": status, "headers": headers}
    )
    await env.send(
        {"type": "http.response.body", "body": bytes(body), "more_body": False}
    )


async def _send_json(env: GwRawEnvelope, status: int, payload: Any) -> None:
    await env.send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await env.send(
        {
            "type": "http.response.body",
            "body": json.dumps(payload).encode("utf-8"),
            "more_body": False,
        }
    )


async def _handle_lifespan(app: Any, env: GwRawEnvelope) -> None:
    while True:
        message = await env.receive()
        message_type = message.get("type")
        if message_type == "lifespan.startup":
            await app.run_event_handlers("startup")
            await env.send({"type": "lifespan.startup.complete"})
            continue
        if message_type == "lifespan.shutdown":
            await app.run_event_handlers("shutdown")
            await env.send({"type": "lifespan.shutdown.complete"})
        return
