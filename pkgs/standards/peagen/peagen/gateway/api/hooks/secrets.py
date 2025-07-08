"""
gateway.api.hooks.secrets  – AutoAPI-native implementation
──────────────────────────────────────────────────────────
* POST-commit on secrets.create  → {"ok": true}
* POST-handler on secrets.read   → {"secret": "<cipher>"}  (or error)
* POST-commit on secrets.delete  → {"ok": true}
"""
from __future__ import annotations

from typing import Any, Dict

from autoapi.v2 import Phase, AutoAPI
from peagen.orm import Secret

from .. import log, api

# Generated schemas (if you need field names etc.)
SecretRead = AutoAPI.get_schema(Secret, "read")

# ─────────────────────────── hooks ───────────────────────────────────
@api.hook(Phase.POST_COMMIT, method="secrets.create")
async def post_secret_add(ctx: Dict[str, Any]) -> None:
    """Return a simple OK dict after the secret is persisted."""
    params = ctx["env"].params
    log.info("Secret stored successfully: %s", params.name)
    ctx["result"] = {"ok": True}                      # ← no ad-hoc model

@api.hook(Phase.POST_COMMIT, method="secrets.delete")
async def post_secret_delete(ctx: Dict[str, Any]) -> None:
    """Confirm deletion with a flat OK payload."""
    params = ctx["env"].params
    log.info("Secret deleted: %s", params.name)
    ctx["result"] = {"ok": True}
