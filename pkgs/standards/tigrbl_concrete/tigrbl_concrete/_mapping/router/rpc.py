from __future__ import annotations

import logging
import inspect
from uuid import UUID
from types import SimpleNamespace
from typing import Any, Dict, Mapping, Optional, Union

from .common import RouterLike, _ensure_router_ns
from ..._concrete import engine_resolver as _resolver
from tigrbl_ops_oltp.crud.helpers.model import _coerce_pk_value, _single_pk_name
from tigrbl_ops_oltp.crud import ops as _crud_ops
from tigrbl_ops_oltp.crud import bulk as _crud_bulk
from ..._mapping.op_resolver import resolve as resolve_ops
from tigrbl_runtime.runtime.executor.invoke import invoke_op

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/mapping/router/rpc")


def _should_fallback_to_crud(
    *, target: str, pk_name: str | None, final: Any, payload: Any
) -> bool:
    if target not in {"read", "update", "replace"}:
        return False
    if pk_name is None:
        return False
    if type(final).__name__.endswith("Ctx"):
        return True
    if final is None:
        return True
    if isinstance(final, Mapping):
        if pk_name not in final:
            return True
        if target == "read":
            # ``read`` must return a materialized record, not an echo object.
            data_keys = [k for k in final.keys() if k != pk_name]
            if data_keys and all(final.get(k) is None for k in data_keys):
                return True
    if target in {"update", "replace"} and isinstance(payload, Mapping):
        return any(
            k in payload
            and isinstance(final, Mapping)
            and final.get(k) != payload.get(k)
            for k in payload
            if k != pk_name
        )
    return False


def _unwrap_runtime_result(value: Any) -> Any:
    current = value
    seen: set[int] = set()
    for _ in range(64):
        marker = id(current)
        if marker in seen:
            break
        seen.add(marker)

        if isinstance(current, Mapping):
            if "result" in current:
                current = current.get("result")
                continue
            if "item" in current:
                current = current.get("item")
                continue
            if "items" in current and isinstance(current.get("items"), list):
                return current
            break

        payload = getattr(current, "response_payload", None)
        if payload is not None:
            current = payload
            continue

        next_result = getattr(current, "result", None)
        if next_result is not None:
            current = next_result
            continue

        response = getattr(current, "response", None)
        if response is not None:
            response_result = getattr(response, "result", None)
            if response_result is not None and response_result is not current:
                current = response_result
                continue

        bag = getattr(current, "bag", None)
        if isinstance(bag, Mapping) and bag.get("result") is not None:
            nested = bag.get("result")
            if nested is not current:
                current = nested
                continue

        in_values = getattr(current, "in_values", None)
        if isinstance(in_values, Mapping) and in_values:
            return dict(in_values)

        transport = getattr(current, "transport_response", None)
        if transport is not None:
            current = transport
            continue

        break

    if isinstance(current, UUID):
        return str(current)
    if isinstance(current, (str, int, float, bool)) or current is None:
        return current
    if isinstance(current, Mapping):
        return {k: _unwrap_runtime_result(v) for k, v in current.items()}
    if isinstance(current, (list, tuple)):
        return [_unwrap_runtime_result(item) for item in current]

    model_dump = getattr(current, "model_dump", None)
    if callable(model_dump):
        try:
            return model_dump()
        except Exception:
            pass

    obj_dict = getattr(current, "__dict__", None)
    if isinstance(obj_dict, dict):
        return {
            k: _unwrap_runtime_result(v)
            for k, v in obj_dict.items()
            if not k.startswith("_")
        }

    return current


def _fallback_resolution(
    router: RouterLike, model_or_name: Union[type, str], alias: str
) -> SimpleNamespace:
    if isinstance(model_or_name, type):
        model = model_or_name
    else:
        tables = getattr(router, "tables", {}) or {}
        model = tables.get(model_or_name)
    if model is None:
        raise AttributeError(f"Unknown model '{model_or_name}'")

    specs = resolve_ops(model)
    spec = next((sp for sp in specs if sp.alias == alias), None)
    target = spec.target if spec is not None else alias
    return SimpleNamespace(model=model, target=target)


async def rpc_call(
    router: RouterLike,
    model_or_name: Union[type, str],
    method: str,
    payload: Any = None,
    *,
    db: Any | None = None,
    request: Any = None,
    ctx: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Call a registered RPC method by (model, method) pair.
    `model_or_name` may be a model class or its name.
    """
    logger.debug("rpc_call invoked for model=%s method=%s", model_or_name, method)
    _ensure_router_ns(router)

    resolution = _fallback_resolution(router, model_or_name, method)
    mdl = resolution.model
    logger.debug(
        "Resolved operation model=%s alias=%s target=%s",
        getattr(mdl, "__name__", mdl),
        method,
        resolution.target,
    )

    fn = getattr(getattr(mdl, "rpc", SimpleNamespace()), method, None)
    if fn is None:
        logger.debug(
            "RPC method '%s' not found on %s", method, getattr(mdl, "__name__", mdl)
        )
        raise AttributeError(
            f"{getattr(mdl, '__name__', mdl)} has no RPC method '{method}'"
        )

    # Acquire DB if not explicitly provided (op > model > router > app)
    _release_db = None
    if db is None:
        try:
            logger.debug(
                "Acquiring DB for rpc_call %s.%s", getattr(mdl, "__name__", mdl), method
            )
            db, _release_db = _resolver.acquire(
                router=router, model=mdl, op_alias=method
            )
        except Exception:
            logger.exception(
                "DB acquire failed for rpc_call %s.%s; no default configured?",
                getattr(mdl, "__name__", mdl),
                method,
            )
            raise
    else:
        logger.debug(
            "Using provided DB for rpc_call %s.%s",
            getattr(mdl, "__name__", mdl),
            method,
        )

    # Ensure execution context contains basic runtime metadata. In tests or
    # other direct calls there may be no ``request`` object to supply an app
    # reference, which the runtime uses to resolve the opview. When absent, the
    # kernel falls back to cached specs for the given model and alias.
    ctx_dict: Dict[str, Any] = dict(ctx or {})
    # Opportunistically derive path params from the payload when the caller
    # supplies the primary key in the body. Many RPC handlers expect the
    # identifier via ``ctx['path_params']`` (mirroring REST semantics), but
    # test code invokes ``rpc_call`` directly with the id embedded in the
    # payload.  Normalizing here preserves backwards compatibility and keeps
    # default CRUD handlers happy.
    try:
        pk_name = _single_pk_name(mdl)
    except Exception:  # model may not be bound to a table
        pk_name = None

    if pk_name and isinstance(payload, Mapping) and pk_name in payload:
        payload = dict(payload)
        payload[pk_name] = _coerce_pk_value(mdl, payload[pk_name])

    if pk_name and isinstance(payload, (list, tuple)):
        normalized_payload: list[Any] = []
        changed = False
        for item in payload:
            if isinstance(item, Mapping) and pk_name in item:
                row = dict(item)
                row[pk_name] = _coerce_pk_value(mdl, row[pk_name])
                normalized_payload.append(row)
                changed = True
            else:
                normalized_payload.append(item)
        if changed:
            payload = normalized_payload

    if pk_name and isinstance(payload, Mapping) and pk_name in payload:
        coerced_pk = _coerce_pk_value(mdl, payload[pk_name])
        pp = dict(ctx_dict.get("path_params", {}))
        pp.setdefault(pk_name, coerced_pk)
        ctx_dict["path_params"] = pp

    if pk_name and isinstance(ctx_dict.get("path_params"), Mapping):
        pp = dict(ctx_dict.get("path_params", {}))
        if pk_name in pp:
            pp[pk_name] = _coerce_pk_value(mdl, pp[pk_name])
            ctx_dict["path_params"] = pp

    if method == "bulk_delete" and pk_name and isinstance(payload, (list, tuple)):
        payload = [_coerce_pk_value(mdl, ident) for ident in payload]

    try:
        logger.debug("Executing rpc_call %s.%s", getattr(mdl, "__name__", mdl), method)
        result = await fn(payload, db=db, request=request, ctx=ctx_dict)
        is_ctx_result = type(result).__name__.endswith("Ctx")
        if isinstance(result, Mapping) and {
            "model",
            "alias",
            "ctx",
            "serialize",
            "request",
            "db",
        }.issubset(result.keys()):
            invoke_ctx: Dict[str, Any] = dict(result["ctx"])
            invoke_ctx["response_serializer"] = result["serialize"]
            final = await invoke_op(
                request=result["request"],
                db=result["db"],
                model=result["model"],
                alias=result["alias"],
                ctx=invoke_ctx,
            )
        elif is_ctx_result:
            invoke_ctx = dict(ctx_dict)
            invoke_ctx.setdefault("payload", payload)
            invoke_ctx.setdefault("db", db)
            invoke_ctx.setdefault("model", mdl)
            invoke_ctx.setdefault("op", method)
            invoke_ctx.setdefault("method", method)
            invoke_ctx.setdefault("target", getattr(resolution, "target", method))
            serializer = getattr(result, "response_serializer", None)
            if callable(serializer):
                invoke_ctx["response_serializer"] = serializer
            final = await invoke_op(
                request=request,
                db=db,
                model=mdl,
                alias=method,
                ctx=invoke_ctx,
            )
        else:
            final = result

        if _should_fallback_to_crud(
            target=getattr(resolution, "target", method),
            pk_name=pk_name,
            final=final,
            payload=payload,
        ):
            path_params = ctx_dict.get("path_params", {})
            ident = None
            if isinstance(path_params, Mapping):
                ident = path_params.get(pk_name)
            if ident is None and isinstance(payload, Mapping):
                ident = payload.get(pk_name)
            if ident is not None:
                ident = _coerce_pk_value(mdl, ident)
                if resolution.target == "read":
                    fallback = _crud_ops.read(mdl, ident, db)
                elif resolution.target == "update":
                    fallback = _crud_ops.update(mdl, ident, dict(payload or {}), db)
                else:
                    fallback = _crud_ops.replace(mdl, ident, dict(payload or {}), db)
                final = await fallback if inspect.isawaitable(fallback) else fallback

        final = _unwrap_runtime_result(final)

        target = getattr(resolution, "target", method)
        if pk_name:
            path_params = ctx_dict.get("path_params", {})
            ident = None
            if isinstance(path_params, Mapping):
                ident = path_params.get(pk_name)
            if ident is None and isinstance(payload, Mapping):
                ident = payload.get(pk_name)
            if ident is not None:
                ident = _coerce_pk_value(mdl, ident)

            if target == "read":
                needs_read = final is None
                if isinstance(final, Mapping):
                    if pk_name not in final:
                        needs_read = True
                    else:
                        data_keys = [k for k in final.keys() if k != pk_name]
                        if data_keys and all(final.get(k) is None for k in data_keys):
                            needs_read = True
                if needs_read and ident is not None:
                    fetched = _crud_ops.read(mdl, ident, db)
                    final = await fetched if inspect.isawaitable(fetched) else fetched

            if target in {"update", "replace", "merge"} and ident is not None:
                if final is None and isinstance(payload, Mapping):
                    if target == "update":
                        next_result = _crud_ops.update(mdl, ident, dict(payload), db)
                    elif target == "replace":
                        next_result = _crud_ops.replace(mdl, ident, dict(payload), db)
                    else:
                        next_result = _crud_ops.merge(mdl, ident, dict(payload), db)
                    final = (
                        await next_result
                        if inspect.isawaitable(next_result)
                        else next_result
                    )
                if isinstance(final, Mapping) and pk_name not in final:
                    final = {pk_name: ident, **dict(final)}

        if target == "delete" and not (
            isinstance(final, Mapping) and isinstance(final.get("deleted"), int)
        ):
            if pk_name:
                ident = None
                if isinstance(ctx_dict.get("path_params"), Mapping):
                    ident = ctx_dict["path_params"].get(pk_name)
                if ident is None and isinstance(payload, Mapping):
                    ident = payload.get(pk_name)
                if ident is not None:
                    ident = _coerce_pk_value(mdl, ident)
                    deleted = _crud_ops.delete(mdl, ident, db)
                    final = await deleted if inspect.isawaitable(deleted) else deleted

        if target.startswith("bulk_") and isinstance(payload, list):
            if final is None:
                op = getattr(_crud_bulk, target, None)
                if callable(op):
                    recalculated = op(mdl, payload, db)
                    final = (
                        await recalculated
                        if inspect.isawaitable(recalculated)
                        else recalculated
                    )
            if isinstance(final, list):
                enriched: list[Any] = []
                for idx, row in enumerate(final):
                    if not isinstance(row, Mapping):
                        enriched.append(row)
                        continue
                    if pk_name and pk_name not in row and idx < len(payload):
                        source = payload[idx]
                        if isinstance(source, Mapping) and pk_name in source:
                            enriched.append({pk_name: source[pk_name], **dict(row)})
                            continue
                    enriched.append(dict(row))
                final = enriched

        if getattr(resolution, "target", None) == "list" and isinstance(final, Mapping):
            items = final.get("items")
            if isinstance(items, list):
                return items
        return final
    finally:
        if _release_db is not None:
            try:
                _release_db()
                logger.debug(
                    "Released DB for rpc_call %s.%s",
                    getattr(mdl, "__name__", mdl),
                    method,
                )
            except Exception:
                logger.debug(
                    "Non-fatal: error releasing acquired DB session (rpc_call)",
                    exc_info=True,
                )
