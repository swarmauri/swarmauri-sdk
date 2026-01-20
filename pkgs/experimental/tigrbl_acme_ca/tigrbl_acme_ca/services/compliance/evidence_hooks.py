from __future__ import annotations

from datetime import datetime, timezone
from tigrbl.hook import hook_ctx


def _emit_evidence(ctx, kind: str, data: dict):
    sink = ctx.get("evidence_sink")  # runtime-injected sink (e.g., queue, http client)
    if not sink:
        return
    try:
        return sink.write(
            {"kind": kind, "at": datetime.now(timezone.utc).isoformat(), "data": data}
        )
    except Exception:
        # non-fatal
        return None


@hook_ctx(ops=("new_account",), phase="POST_COMMIT")
async def _evidence_new_account(cls, ctx):
    acct = ctx.get("result")
    if acct:
        _emit_evidence(
            ctx, "acme.new_account", {"account_id": getattr(acct, "id", None)}
        )


@hook_ctx(ops=("new_order",), phase="POST_COMMIT")
async def _evidence_new_order(cls, ctx):
    order = ctx.get("result")
    if order:
        _emit_evidence(ctx, "acme.new_order", {"order_id": getattr(order, "id", None)})


@hook_ctx(ops=("finalize",), phase="POST_COMMIT")
async def _evidence_certificate_issued(cls, ctx):
    order = ctx.get("result")
    if order:
        _emit_evidence(
            ctx,
            "acme.certificate_issued",
            {
                "order_id": getattr(order, "id", None),
                "certificate_id": getattr(order, "certificate_id", None),
            },
        )


@hook_ctx(ops=("revoke_cert",), phase="POST_COMMIT")
async def _evidence_certificate_revoked(cls, ctx):
    rev = ctx.get("result")
    if rev:
        _emit_evidence(
            ctx,
            "acme.certificate_revoked",
            {"certificate_id": getattr(rev, "certificate_id", None)},
        )
