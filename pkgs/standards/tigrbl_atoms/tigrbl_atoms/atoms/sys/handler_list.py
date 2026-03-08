from __future__ import annotations

import inspect
from typing import Any, Mapping, Optional

import tigrbl_ops_oltp as _core

from ... import events as _ev
from ...stages import Operated, Resolved
from ...types import Atom, Ctx, OperatedCtx
from . import _oltp_context as _ctx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE


async def _call_list_core(
    fn: Any,
    model: type,
    payload: Mapping[str, Any],
    ctx: Mapping[str, Any],
):
    filters = dict(payload) if isinstance(payload, Mapping) else {}
    skip = filters.pop("skip", None)
    limit = filters.pop("limit", None)
    filters_arg = filters if filters else None

    db = _ctx.db(ctx)
    req = _ctx.request(ctx)

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
        except TypeError as exc:
            last_err = exc
            continue
    if last_err:
        raise last_err
    raise RuntimeError("list() call resolution failed unexpectedly")


async def _run(obj: object | None, ctx: Any) -> None:
    model = obj if isinstance(obj, type) else getattr(ctx, "model", None)
    if not isinstance(model, type):
        raise TypeError("handler_list requires a model type")
    payload = _ctx.payload(ctx)
    setattr(ctx, "result", await _call_list_core(_core.list, model, payload, ctx))


class AtomImpl(Atom[Resolved, Operated]):
    name = "sys.handler_list"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
