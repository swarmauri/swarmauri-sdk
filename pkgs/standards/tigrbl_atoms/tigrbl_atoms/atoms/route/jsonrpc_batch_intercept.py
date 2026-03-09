from __future__ import annotations

from ...types import Atom, Ctx, PlannedCtx
from ...stages import Planned

import json
from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Any, Mapping

from ... import events as _ev

ANCHOR = _ev.ROUTE_CTX_FINALIZE


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


def _resolve_get_db(app: Any) -> Any:
    provider = getattr(app, "dependency_overrides_provider", None)
    if provider is None:
        provider = getattr(app, "provider", None)
    if provider is not None:
        get_db = getattr(provider, "get_db", None)
        if callable(get_db):
            return get_db
    get_db = getattr(app, "get_db", None)
    if callable(get_db):
        return get_db
    return None


@asynccontextmanager
async def _request_db_session(app: Any):
    get_db = _resolve_get_db(app)
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


async def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})

    payload = getattr(ctx, "payload", None)
    app = getattr(ctx, "app", None)
    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", {}) if raw is not None else {}
    if not (
        isinstance(payload, list) and isinstance(scope, Mapping) and app is not None
    ):
        return

    if not _is_jsonrpc_path(app, scope):
        return

    if not payload or not all(
        isinstance(item, Mapping) and isinstance(item.get("method"), str)
        for item in payload
    ):
        return

    responses: list[dict[str, Any]] = []
    for item in payload:
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

    egress = temp.setdefault("egress", {}) if isinstance(temp, dict) else {}
    egress["transport_response"] = {
        "status_code": 200,
        "headers": {"content-type": "application/json"},
        "body": responses,
    }
    route["short_circuit"] = True


class AtomImpl(Atom[Planned, Planned]):
    name = "route.jsonrpc_batch_intercept"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Planned]) -> Ctx[Planned]:
        await _run(obj, ctx)
        return ctx.promote(PlannedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
