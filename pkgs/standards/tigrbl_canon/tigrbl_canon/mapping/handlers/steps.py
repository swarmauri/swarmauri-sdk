# tigrbl/v3/mapping/handlers/steps.py
from __future__ import annotations

import inspect
import logging
from functools import lru_cache
from typing import Any, Callable

from tigrbl_atoms.atoms import get as _get_atom
from tigrbl_core._spec import OpSpec
from tigrbl_runtime.runtime.executor import _Ctx

from ...hook.types import StepFn
from .ctx import _ctx_db, _ctx_payload, _ctx_request

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/mapping/handlers/steps")


def _accepted_kw(handler: Callable[..., Any]) -> set[str]:
    try:
        sig = inspect.signature(handler)
    except Exception as exc:
        logger.debug("Failed to inspect handler %r: %s", handler, exc)
        return {"ctx"}

    names: set[str] = set()
    for p in sig.parameters.values():
        if p.kind in (p.VAR_KEYWORD, p.VAR_POSITIONAL):
            logger.debug("Handler %r accepts arbitrary params", handler)
            return {"ctx", "db", "payload", "request", "model", "op", "spec", "alias"}
        names.add(p.name)
    logger.debug("Handler %r accepts keywords %s", handler, names)
    return names


def _wrap_custom(model: type, sp: OpSpec, user_handler: Callable[..., Any]) -> StepFn:
    async def step(ctx: Any) -> Any:
        db = _ctx_db(ctx)
        payload = _ctx_payload(ctx)
        request = _ctx_request(ctx)
        isolated = _Ctx.ensure(request=request, db=db, seed=ctx)
        bound = user_handler
        wanted = _accepted_kw(bound)

        kw: dict[str, Any] = {}
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
        logger.debug("Calling custom handler %r with kw=%s", bound, kw)
        rv = bound(**kw)  # type: ignore[misc]
        if inspect.isawaitable(rv):
            logger.debug("Awaiting async custom handler")
            return await rv
        return rv

    step.__name__ = getattr(user_handler, "__name__", step.__name__)
    step.__qualname__ = getattr(user_handler, "__qualname__", step.__name__)
    step.__module__ = getattr(user_handler, "__module__", step.__module__)
    return step


@lru_cache(maxsize=None)
def _wrap_core(model: type, target: str) -> StepFn:
    logger.debug("Creating core wrapper for %s.%s", model.__name__, target)

    subject_by_target = {
        "create": "handler_create",
        "read": "handler_read",
        "update": "handler_update",
        "replace": "handler_replace",
        "merge": "handler_merge",
        "noop": "handler_noop",
        "delete": "handler_delete",
        "list": "handler_list",
        "clear": "handler_clear",
        "bulk_create": "handler_bulk_create",
        "bulk_update": "handler_bulk_update",
        "bulk_replace": "handler_bulk_replace",
        "bulk_merge": "handler_bulk_merge",
        "bulk_delete": "handler_bulk_delete",
    }

    subject = subject_by_target.get(target)

    if subject is None:

        async def default_step(ctx: Any) -> Any:
            logger.debug("No core operation matched; returning payload")
            return _ctx_payload(ctx)

        default_step.__name__ = f"{target}_default"
        return default_step

    anchor, atom_runner = _get_atom("sys", subject)

    async def step(ctx: Any) -> Any:
        await atom_runner(model, ctx)
        return getattr(ctx, "result", None)

    step.__name__ = getattr(atom_runner, "__name__", target)
    step.__qualname__ = getattr(atom_runner, "__qualname__", step.__name__)
    step.__module__ = getattr(atom_runner, "__module__", step.__module__)
    step.__tigrbl_label = f"atom:sys:{subject}@{anchor}"
    return step


__all__ = ["_accepted_kw", "_wrap_custom", "_wrap_core"]
