from __future__ import annotations

from typing import Any

import tigrbl_ops_oltp as _core
from tigrbl_ops_oltp.crud.helpers.model import _coerce_pk_value

from ... import events as _ev
from ...stages import Resolved, Operated
from ...types import Atom, Ctx, OperatedCtx
from . import _oltp_context as _ctx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE


async def _run(obj: object | None, ctx: Any) -> None:
    # Some compiled plans include both verb-specific persistence atoms
    # (e.g. ``handler_create``) and this generic fallback atom anchored at the
    # same stage. If a prior atom already produced a result, do not execute
    # persistence again.
    if getattr(ctx, "result", None) is not None:
        return

    target = str(getattr(ctx, "target", None) or getattr(ctx, "op", None) or "").lower()

    model = obj if isinstance(obj, type) else getattr(ctx, "model", None)
    if not isinstance(model, type):
        if target:
            raise TypeError("handler_persistence requires a model type")
        return

    db = _ctx.db(ctx)

    if target == "create":
        setattr(ctx, "result", await _core.create(model, _ctx.payload(ctx), db=db))
        return
    if target == "read":
        setattr(ctx, "result", await _core.read(model, _ctx.ident(model, ctx), db=db))
        return
    if target == "update":
        setattr(
            ctx,
            "result",
            await _core.update(model, _ctx.ident(model, ctx), _ctx.payload(ctx), db=db),
        )
        return
    if target == "replace":
        setattr(
            ctx,
            "result",
            await _core.replace(
                model, _ctx.ident(model, ctx), _ctx.payload(ctx), db=db
            ),
        )
        return
    if target == "merge":
        setattr(
            ctx,
            "result",
            await _core.merge(model, _ctx.ident(model, ctx), _ctx.payload(ctx), db=db),
        )
        return
    if target == "delete":
        setattr(ctx, "result", await _core.delete(model, _ctx.ident(model, ctx), db=db))
        return
    if target == "list":
        setattr(
            ctx, "result", await _core.list(model=model, db=db, **_ctx.payload(ctx))
        )
        return
    if target == "clear":
        setattr(ctx, "result", await _core.clear(model, db=db))
        return

    if target == "bulk_create":
        setattr(ctx, "result", await _core.bulk_create(model, _ctx.payload(ctx), db=db))
        return
    if target == "bulk_update":
        setattr(ctx, "result", await _core.bulk_update(model, _ctx.payload(ctx), db=db))
        return
    if target == "bulk_replace":
        setattr(
            ctx,
            "result",
            await _core.bulk_replace(model, _ctx.payload(ctx), db=db),
        )
        return
    if target == "bulk_merge":
        setattr(ctx, "result", await _core.bulk_merge(model, _ctx.payload(ctx), db=db))
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
        setattr(ctx, "result", await _core.bulk_delete(model, normalized, db=db))


class AtomImpl(Atom[Resolved, Operated]):
    name = "sys.handler_persistence"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
