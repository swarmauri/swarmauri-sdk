"""
auto_authn.adapters.local_adapter
──────────────────
Concrete implementation of the ``AuthNProvider`` ABC declared by
``autoapi.v3.authn_abc``.  It merely **adapts** the public helpers that already
exist in *auto_authn* so that AutoAPI can consume them automatically.

Usage
-----
>>> from autoapi.v3 import AutoAPI
>>> from auto_authn.adapters import LocalAuthNAdapter
>>> api = AutoAPI(engine=ENGINE, authn=LocalAuthNAdapter())
"""

from __future__ import annotations

from fastapi import Request

from autoapi.v3.config import __autoapi_auth_context__
from autoapi.v3.config.constants import CTX_TENANT_ID_KEY, CTX_USER_ID_KEY
from autoapi.v3.types.authn_abc import AuthNProvider
from ..fastapi_deps import get_principal
from ..principal_ctx import principal_var  # noqa: F401  # ensure ContextVar is initialised


class LocalAuthNAdapter(AuthNProvider):
    """
    Thin wrapper that plugs existing *auto_authn* functions into
    the abstract interface expected by AutoAPI.
    """

    # ------------------------------------------------------------------ #
    # FastAPI dependency (mandatory)                                     #
    # ------------------------------------------------------------------ #
    async def get_principal(self, request: Request) -> dict:  # noqa: D401
        """
        Delegate to ``auto_authn.fastapi_deps.get_principal`` and forward
        whatever dict it returns while storing an auth context on
        ``request.state`` for AutoAPI.

        Raises
        ------
        fastapi.HTTPException(401)
            If the API‑key / bearer token is invalid or expired.
        """
        principal: dict = await get_principal(request)  # type: ignore[arg-type]

        # Normalise and expose an auth context for AutoAPI
        auth_ctx = dict(principal)
        tid = principal.get("tid")
        sub = principal.get("sub")
        if tid is not None:
            auth_ctx.setdefault(CTX_TENANT_ID_KEY, tid)
        if sub is not None:
            auth_ctx.setdefault(CTX_USER_ID_KEY, sub)
        setattr(request.state, __autoapi_auth_context__, auth_ctx)

        return principal


__all__ = ["LocalAuthNAdapter"]
