from __future__ import annotations

import json
from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Any, Mapping

from ..atoms.egress.asgi_send import _send_json, _send_transport_response
from ..executor import _Ctx, _invoke
from ..kernel.core import Kernel
from ..status import StatusDetailError
from ...mapping.runtime_routes import invoke_runtime_route_handler
from .raw import GwRawEnvelope


def _normalize_path(path: str | None) -> str:
    if not isinstance(path, str) or not path:
        return "/"
    if path == "/":
        return "/"
    return path.rstrip("/") or "/"


def _is_jsonrpc_path(app: Any, scope: Mapping[str, Any]) -> bool:
    prefix = getattr(app, "jsonrpc_prefix", None)
    if not isinstance(prefix, str):
        return False
    return _normalize_path(str(scope.get("path", "/"))) == _normalize_path(prefix)


@asynccontextmanager
async def _request_db_session(app: Any):
    from ...mapping import engine_resolver as _resolver

    provider = _resolver.resolve_provider(router=app)
    get_db = provider.get_db if provider is not None else None
    if get_db is None:
        yield None
        return

    stream = get_db()
    if hasattr(stream, "__anext__"):
        agen = stream
        try:
            db = await agen.__anext__()
            try:
                yield db
            finally:
                await agen.aclose()
        except StopAsyncIteration:
            yield None
        return

    if hasattr(stream, "__next__"):
        gen = stream
        try:
            db = next(gen)
            try:
                yield db
            finally:
                try:
                    next(gen)
                except StopIteration:
                    pass
                close = getattr(gen, "close", None)
                if callable(close):
                    close()
        except StopIteration:
            yield None
        return

    yield stream


async def _invoke_jsonrpc_batch(ctx: _Ctx, env: GwRawEnvelope) -> bool:
    payload = getattr(ctx, "payload", None)
    if not isinstance(payload, list):
        return False

    # Distinguish true JSON-RPC batches (list of envelopes with "method")
    # from single bulk-operation params (list of record payloads).
    if not payload or not all(
        isinstance(item, Mapping) and isinstance(item.get("method"), str)
        for item in payload
    ):
        return False

    responses: list[dict[str, Any]] = []
    app = getattr(ctx, "app", None)
    for item in payload:
        if not isinstance(item, Mapping):
            responses.append(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Invalid Request"},
                    "id": None,
                }
            )
            continue

        request_id = item.get("id")
        method = item.get("method")
        params = item.get("params", {})
        if not isinstance(method, str) or "." not in method:
            responses.append(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id,
                }
            )
            continue

        model_name, op_alias = method.split(".", 1)
        if not model_name or not op_alias:
            responses.append(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id,
                }
            )
            continue

        try:
            async with _request_db_session(app) as db:
                result = await app.rpc_call(
                    model_name,
                    op_alias,
                    params if params is not None else {},
                    db=db,
                    request=SimpleNamespace(
                        headers={},
                        query_params={},
                        path_params={},
                        state=SimpleNamespace(),
                    ),
                    ctx={},
                )
            normalized_result = result
            json_body = getattr(result, "json_body", None)
            if callable(json_body):
                normalized_result = json_body()
            elif isinstance(result, str):
                try:
                    normalized_result = json.loads(result)
                except Exception:
                    normalized_result = result
            responses.append(
                {"jsonrpc": "2.0", "result": normalized_result, "id": request_id}
            )
        except AttributeError:
            responses.append(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id,
                }
            )
        except Exception as exc:
            responses.append(
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": str(exc) or "Server error"},
                    "id": request_id,
                }
            )

    transport_ctx = SimpleNamespace(
        status_code=200,
        temp={
            "egress": {
                "transport_response": {
                    "status_code": 200,
                    "headers": {"content-type": "application/json"},
                    "body": responses,
                }
            }
        },
    )
    await _send_transport_response(env, transport_ctx)
    return True


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

    if _is_jsonrpc_path(app, env.scope) and await _invoke_jsonrpc_batch(ctx, env):
        return

    opmeta_index = _resolve_op_index(ctx, plan)
    if opmeta_index is None:
        if await _fallback_runtime_route(ctx, env):
            return
        await _send_json(env, 404, {"detail": "No runtime operation matched request."})
        return

    opmeta = plan.opmeta[opmeta_index]
    ctx.model = opmeta.model
    ctx.op = opmeta.alias
    ctx.opview = kernel.get_opview(app, opmeta.model, opmeta.alias)

    phases = _without_ingress_phases(plan.phase_chains.get(opmeta_index, {}))
    try:
        await _invoke(request=None, db=None, phases=phases, ctx=ctx)
    except StatusDetailError as exc:
        detail = (
            exc.detail if getattr(exc, "detail", None) not in (None, "") else str(exc)
        )
        await _send_json(
            env, int(getattr(exc, "status_code", 500) or 500), {"detail": detail}
        )
        return
    except Exception as exc:  # pragma: no cover - defensive runtime fallback
        from ..status import create_standardized_error

        std = create_standardized_error(exc)
        detail = (
            std.detail if getattr(std, "detail", None) not in (None, "") else str(std)
        )
        await _send_json(
            env, int(getattr(std, "status_code", 500) or 500), {"detail": detail}
        )
        return

    await _send_transport_response(env, ctx)


async def _fallback_runtime_route(ctx: _Ctx, env: GwRawEnvelope) -> bool:
    route = (
        ctx.temp.get("route") if isinstance(getattr(ctx, "temp", None), dict) else None
    )
    handler = route.get("handler") if isinstance(route, dict) else None

    if not callable(handler):
        request = getattr(ctx, "request", None)
        app = getattr(ctx, "app", None)
        method = str(getattr(request, "method", "")).upper()
        path = getattr(request, "path", None) or getattr(
            getattr(request, "url", None), "path", None
        )
        if method and isinstance(path, str) and app is not None:
            for candidate in getattr(app, "routes", ()) or ():
                if method not in (getattr(candidate, "methods", ()) or ()):
                    continue
                pattern = getattr(candidate, "pattern", None)
                if pattern is None:
                    continue
                matched = pattern.match(path)
                if matched is None:
                    continue
                handler = getattr(candidate, "handler", None)
                if not callable(handler):
                    continue
                request.path_params = dict(matched.groupdict())
                break

    if not callable(handler):
        return False

    await invoke_runtime_route_handler(ctx, handler=handler)
    await _send_transport_response(env, ctx)
    return True


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
