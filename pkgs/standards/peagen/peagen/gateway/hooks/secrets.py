"""
gateway.hooks.secrets  – AutoAPI-native implementation
──────────────────────────────────────────────────────────
* POST-commit on Secrets.create  → {"ok": true}
* POST-handler on Secrets.read   → {"secret": "<cipher>"}  (or error)
* POST-commit on Secrets.delete  → {"ok": true}
"""

from __future__ import annotations

from typing import Any, Dict

from autoapi.v2 import AutoAPI, Phase

from peagen.orm import RepoSecret
# Activate if UserSecret, OrgSecret are enabled
# from peagen.orm import OrgSecret, UserSecret

from peagen.gateway import api, log

# Activate if UserSecret, OrgSecret are enabled
# UserSecretRead = AutoAPI.get_schema(UserSecret, "read")
# OrgSecretRead = AutoAPI.get_schema(OrgSecret, "read")

RepoSecretRead = AutoAPI.get_schema(RepoSecret, "read")


# ─────────────────────────── hooks ───────────────────────────────────
# Activate if UserSecret, OrgSecret are enabled
# @api.hook(Phase.POST_COMMIT, method="UserSecrets.create")
# @api.hook(Phase.POST_COMMIT, method="OrgSecrets.create")
@api.hook(Phase.POST_COMMIT, model="RepoSecret", op="create")
async def post_secret_add(ctx: Dict[str, Any]) -> None:
    """Return a simple OK dict after the secret is persisted."""
    log.info("entering post_secret_add")

    params = ctx["env"].params
    log.info("Secret stored successfully: %s", params.name)
    ctx["result"] = {"ok": True}  # ← no ad-hoc model


# Activate if UserSecret, OrgSecret are enabled
# @api.hook(Phase.POST_COMMIT, method="UserSecrets.delete")
# @api.hook(Phase.POST_COMMIT, method="OrgSecrets.delete")
@api.hook(Phase.POST_COMMIT, model="RepoSecret", op="delete")
async def post_secret_delete(ctx: Dict[str, Any]) -> None:
    """Confirm deletion with a flat OK payload."""
    log.info("entering post_secret_delete")

    params = ctx["env"].params
    log.info("Secret deleted: %s", params.name)
