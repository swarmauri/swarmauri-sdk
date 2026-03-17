from __future__ import annotations

from typing import Any

from tigrbl_ops_oltp.crud import bulk as _bulk
from tigrbl_ops_oltp.crud import ops as _ops
from tigrbl_ops_oltp.crud.helpers.model import _coerce_pk_value

from ... import events as _ev
from ...stages import Resolved, Operated
from ...types import Atom, Ctx, OperatedCtx
from . import _oltp_context as _ctx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE


async def _run(obj: object | None, ctx: Any) -> None:
    model = obj if isinstance(obj, type) else getattr(ctx, "model", None)
    if not isinstance(model, type):
        raise TypeError("handler_persistence requires a model type")

    target = str(getattr(ctx, "target", None) or getattr(ctx, "op", None) or "").lower()
    db = _ctx.db(ctx)

    if target == "create":
        setattr(ctx, "result", await _ops.create(model, _ctx.payload(ctx), db=db))
        return
    if target == "read":
        setattr(ctx, "result", await _ops.read(model, _ctx.ident(model, ctx), db=db))
        return
    if target == "update":
        setattr(
            ctx,
            "result",
            await _ops.update(model, _ctx.ident(model, ctx), _ctx.payload(ctx), db=db),
        )
        return
    if target == "replace":
        setattr(
            ctx,
            "result",
            await _ops.replace(model, _ctx.ident(model, ctx), _ctx.payload(ctx), db=db),
        )
        return
    if target == "merge":
        setattr(
            ctx,
            "result",
            await _ops.merge(model, _ctx.ident(model, ctx), _ctx.payload(ctx), db=db),
        )
        return
    if target == "delete":
        setattr(ctx, "result", await _ops.delete(model, _ctx.ident(model, ctx), db=db))
        return
    if target == "list":
        setattr(ctx, "result", await _ops.list(model=model, db=db, **_ctx.payload(ctx)))
        return
    if target == "clear":
        setattr(ctx, "result", await _ops.clear(model, db=db))
        return

    if target == "bulk_create":
        setattr(ctx, "result", await _bulk.bulk_create(model, _ctx.payload(ctx), db=db))
        return
    if target == "bulk_update":
        setattr(ctx, "result", await _bulk.bulk_update(model, _ctx.payload(ctx), db=db))
        return
    if target == "bulk_replace":
        setattr(
            ctx,
            "result",
            await _bulk.bulk_replace(model, _ctx.payload(ctx), db=db),
        )
        return
    if target == "bulk_merge":
        setattr(ctx, "result", await _bulk.bulk_merge(model, _ctx.payload(ctx), db=db))
        return
    if target == "bulk_delete":
        payload = _ctx.payload(ctx)
        idents = payload.get("ids") if isinstance(payload, dict) else payload
        normalized = []
        for ident in idents if isinstance(idents, list) else []:
            try:
                normalized.append(_coerce_pk_value(model, ident))
            except Exception:
                continue
        setattr(ctx, "result", await _bulk.bulk_delete(model, normalized, db=db))


class AtomImpl(Atom[Resolved, Operated]):
    name = "sys.handler_persistence"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
