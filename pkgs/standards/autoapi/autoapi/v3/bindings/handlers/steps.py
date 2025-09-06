# autoapi/v3/bindings/handlers/steps.py
from __future__ import annotations
import logging

import inspect
from typing import Any, Callable, Mapping, Optional

from ... import core as _core
from ...op import OpSpec
from ...op.types import StepFn
from ...runtime.executor import _Ctx
from ...runtime.atoms.storage import to_stored as _to_stored
from .ctx import _ctx_db, _ctx_payload, _ctx_request
from .identifiers import _resolve_ident

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/handlers/steps")


async def _call_list_core(
    fn: Callable[..., Any],
    model: type,
    payload: Mapping[str, Any],
    ctx: Mapping[str, Any],
):
    filters = dict(payload) if isinstance(payload, Mapping) else {}
    skip = filters.pop("skip", None)
    limit = filters.pop("limit", None)
    filters_arg = filters if filters else None

    db = _ctx_db(ctx)
    req = _ctx_request(ctx)

    candidates: list[tuple[tuple, dict]] = []

    def add_candidate(
        use_pos_filters: bool, use_pos_db: bool, with_req: bool, with_pag: bool
    ):
        args: tuple = ()
        kwargs: dict = {}
        if use_pos_filters:
            args += (filters_arg,)
        else:
            kwargs["filters"] = filters_arg
        if use_pos_db:
            args += (db,)
        else:
            kwargs["db"] = db
        if with_req and req is not None:
            kwargs["request"] = req
        if with_pag:
            if skip is not None:
                kwargs["skip"] = skip
            if limit is not None:
                kwargs["limit"] = limit
        candidates.append((args, kwargs))

    add_candidate(False, False, True, True)
    add_candidate(True, False, True, True)
    add_candidate(True, True, True, True)

    add_candidate(False, False, False, True)
    add_candidate(True, False, False, True)
    add_candidate(True, True, False, True)

    add_candidate(False, False, True, False)
    add_candidate(True, False, True, False)
    add_candidate(True, True, True, False)

    add_candidate(False, False, False, False)
    add_candidate(True, False, False, False)
    add_candidate(True, True, False, False)

    last_err: Optional[BaseException] = None
    for args, kwargs in candidates:
        try:
            rv = fn(model, *args, **kwargs)
            if inspect.isawaitable(rv):
                return await rv
            return rv
        except TypeError as e:
            last_err = e
            continue
    if last_err:
        raise last_err
    raise RuntimeError("list() call resolution failed unexpectedly")


def _accepted_kw(handler: Callable[..., Any]) -> set[str]:
    try:
        sig = inspect.signature(handler)
    except Exception:
        return {"ctx"}

    names: set[str] = set()
    for p in sig.parameters.values():
        if p.kind in (p.VAR_KEYWORD, p.VAR_POSITIONAL):
            return {"ctx", "db", "payload", "request", "model", "op", "spec", "alias"}
        names.add(p.name)
    return names


def _wrap_custom(model: type, sp: OpSpec, user_handler: Callable[..., Any]) -> StepFn:
    async def step(ctx: Any) -> Any:
        db = _ctx_db(ctx)
        payload = _ctx_payload(ctx)
        request = _ctx_request(ctx)
        isolated = _Ctx.ensure(request=request, db=db, seed=ctx)
        bound = getattr(model, getattr(user_handler, "__name__", ""), user_handler)
        wanted = _accepted_kw(bound)

        kw = {}
        if "ctx" in wanted:
            kw["ctx"] = isolated
        if "db" in wanted:
            kw["db"] = db
        if "payload" in wanted:
            kw["payload"] = payload
        if "request" in wanted:
            kw["request"] = request
        if "model" in wanted:
            kw["model"] = model
        if "op" in wanted:
            kw["op"] = sp
        if "spec" in wanted:
            kw["spec"] = sp
        if "alias" in wanted:
            kw["alias"] = sp.alias

        rv = bound(**kw)  # type: ignore[misc]
        if inspect.isawaitable(rv):
            return await rv
        return rv

    step.__name__ = getattr(user_handler, "__name__", step.__name__)
    step.__qualname__ = getattr(user_handler, "__qualname__", step.__name__)
    step.__module__ = getattr(user_handler, "__module__", step.__module__)
    return step


def _wrap_core(model: type, target: str) -> StepFn:
    async def step(ctx: Any) -> Any:
        db = _ctx_db(ctx)
        assembled = getattr(ctx, "temp", {}).get("assembled_values")
        if isinstance(assembled, Mapping):
            ctx.payload = dict(assembled)
            _to_stored.run(None, ctx)
            payload = ctx.temp.get("assembled_values", {})
        else:
            payload = _ctx_payload(ctx)

        if target == "create":
            return await _core.create(model, payload, db=db)
        if target == "read":
            ident = _resolve_ident(model, ctx)
            return await _core.read(model, ident, db=db)
        if target == "update":
            ident = _resolve_ident(model, ctx)
            return await _core.update(model, ident, payload, db=db)
        if target == "replace":
            ident = _resolve_ident(model, ctx)
            return await _core.replace(model, ident, payload, db=db)
        if target == "merge":
            ident = _resolve_ident(model, ctx)
            return await _core.merge(model, ident, payload, db=db)
        if target == "delete":
            ident = _resolve_ident(model, ctx)
            return await _core.delete(model, ident, db=db)
        if target == "list":
            return await _call_list_core(_core.list, model, payload, ctx)
        if target == "clear":
            return await _core.clear(model, {}, db=db)
        if target == "bulk_create":
            if not isinstance(payload, list):
                raise TypeError("bulk_create expects a list payload")
            return await _core.bulk_create(model, payload, db=db)
        if target == "bulk_update":
            if not isinstance(payload, list):
                raise TypeError("bulk_update expects a list payload")
            return await _core.bulk_update(model, payload, db=db)
        if target == "bulk_replace":
            if not isinstance(payload, list):
                raise TypeError("bulk_replace expects a list payload")
            return await _core.bulk_replace(model, payload, db=db)
        if target == "bulk_merge":
            if not isinstance(payload, list):
                raise TypeError("bulk_merge expects a list payload")
            return await _core.bulk_merge(model, payload, db=db)
        if target == "bulk_delete":
            ids = payload.get("ids") if isinstance(payload, Mapping) else None
            if ids is None:
                ids = []
            return await _core.bulk_delete(model, ids, db=db)
        return payload

    fn = getattr(_core, target, None)
    step.__name__ = getattr(fn, "__name__", step.__name__)
    step.__qualname__ = getattr(fn, "__qualname__", step.__name__)
    step.__module__ = getattr(fn, "__module__", step.__module__)
    return step


__all__ = [
    "_call_list_core",
    "_accepted_kw",
    "_wrap_custom",
    "_wrap_core",
]
