"""
auto_authn.adapters.local_adapter
──────────────────
Concrete implementation of the ``AuthNProvider`` ABC declared by
``tigrbl.v3.authn_abc``.  It merely **adapts** the public helpers that already
exist in *auto_authn* so that Tigrbl can consume them automatically.

Usage
-----
>>> from tigrbl.v3 import Tigrbl
>>> from auto_authn.adapters import LocalAuthNAdapter
>>> api = Tigrbl(engine=ENGINE, authn=LocalAuthNAdapter())
"""

from __future__ import annotations

from fastapi import Request

from tigrbl.v3.config.constants import TIGRBL_AUTH_CONTEXT_ATTR
from tigrbl.v3.types.authn_abc import AuthNProvider
from ..fastapi_deps import get_principal
from ..principal_ctx import principal_var  # noqa: F401  # ensure ContextVar is initialised


def _set_auth_context(request: Request, principal: dict) -> None:
    """Populate request.state with the auth context expected by Tigrbl."""
    ctx: dict[str, str] = {}
    tid = principal.get("tid") or principal.get("tenant_id")
    uid = principal.get("sub") or principal.get("user_id")
    if tid is not None:
        ctx["tenant_id"] = tid
    if uid is not None:
        ctx["user_id"] = uid
    setattr(request.state, TIGRBL_AUTH_CONTEXT_ATTR, ctx)


class LocalAuthNAdapter(AuthNProvider):
    """
    Thin wrapper that plugs existing *auto_authn* functions into
    the abstract interface expected by Tigrbl.
    """

    # ------------------------------------------------------------------ #
    # FastAPI dependency (mandatory)                                     #
    # ------------------------------------------------------------------ #
    async def get_principal(self, request: Request) -> dict:  # noqa: D401
        """
        Delegate to ``auto_authn.fastapi_deps.get_principal`` and forward
        whatever dict it returns.

        Raises
        ------
        fastapi.HTTPException(401)
            If the API‑key / bearer token is invalid or expired.
        """
        principal = await get_principal(request)  # type: ignore[arg-type]
        _set_auth_context(request, principal)
        return principal


__all__ = ["LocalAuthNAdapter"]
