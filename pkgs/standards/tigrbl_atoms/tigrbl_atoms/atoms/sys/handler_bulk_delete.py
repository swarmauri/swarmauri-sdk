from __future__ import annotations

from typing import Any, Mapping

import tigrbl_ops_oltp as _core
from tigrbl_ops_oltp.crud.helpers.model import _coerce_pk_value

from ... import events as _ev
from ...stages import Operated, Resolved
from ...types import Atom, Ctx, OperatedCtx
from . import _oltp_context as _ctx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE


async def _run(obj: object | None, ctx: Any) -> None:
    model = obj if isinstance(obj, type) else getattr(ctx, "model", None)
    if not isinstance(model, type):
        raise TypeError("handler_bulk_delete requires a model type")
    payload = _ctx.payload(ctx)
    raw_ids = payload
    if isinstance(payload, Mapping):
        raw_ids = payload.get("ids")
        if raw_ids is None and payload:
            first_value = next(iter(payload.values()))
            raw_ids = first_value if isinstance(first_value, list) else []
    ids: list[Any] = []
    if isinstance(raw_ids, list):
        for ident in raw_ids:
            try:
                ids.append(_coerce_pk_value(model, ident))
            except Exception:
                continue
    setattr(ctx, "result", await _core.bulk_delete(model, ids, db=_ctx.db(ctx)))


class AtomImpl(Atom[Resolved, Operated]):
    name = "sys.handler_bulk_delete"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
