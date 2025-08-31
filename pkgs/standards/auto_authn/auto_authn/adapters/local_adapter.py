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
>>> api = AutoAPI(get_async_db=get_db, authn=LocalAuthNAdapter())
"""

from __future__ import annotations

from fastapi import Request

from autoapi.v3.types.authn_abc import AuthNProvider
from ..hooks import register_inject_hook  # injects tenant_id / owner_id
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
        whatever dict it returns.

        Raises
        ------
        fastapi.HTTPException(401)
            If the API‑key / bearer token is invalid or expired.
        """
        return await get_principal(request)  # type: ignore[arg-type]

    # ------------------------------------------------------------------ #
    # Hook registration (mandatory)                                      #
    # ------------------------------------------------------------------ #
    def register_inject_hook(self, api) -> None:  # noqa: D401
        """
        Forward to ``auto_authn.hooks.register_inject_hook`` so that
        tenant / owner fields are injected during *Phase.PRE_TX_BEGIN*.

        The helper is idempotent; calling it twice is safe.
        """
        register_inject_hook(api)


__all__ = ["LocalAuthNAdapter"]
