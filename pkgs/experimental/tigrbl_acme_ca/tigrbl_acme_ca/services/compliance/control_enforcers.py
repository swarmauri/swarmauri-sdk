from __future__ import annotations
from fastapi import HTTPException
from tigrbl.hook import hook_ctx


@hook_ctx(ops=("new_order",), phase="PRE_HANDLER")
async def _enforce_identifier_limits(cls, ctx):
    cfg = ctx.get("config", {})
    max_ids = int(cfg.get("acme.max_identifiers_per_order", 100))
    p = ctx.get("payload") or {}
    identifiers = p.get("identifiers") or []
    if len(identifiers) > max_ids:
        raise HTTPException(status_code=400, detail="too_many_identifiers")


@hook_ctx(ops=("new_account",), phase="PRE_HANDLER")
async def _require_eab_if_configured(cls, ctx):
    cfg = ctx.get("config", {})
    eab_required = bool(cfg.get("acme.external_account_required", False))
    if not eab_required:
        return
    p = ctx.get("payload") or {}
    if not p.get("external_binding"):
        raise HTTPException(status_code=400, detail="external_account_required")
