"""
tigrbl_auth.adapters.local_adapter
──────────────────
Concrete implementation of the ``AuthNProvider`` ABC declared by
``tigrbl.authn_abc``.  It merely **adapts** the public helpers that already
exist in *tigrbl_auth* so that Tigrbl can consume them automatically.

Usage
-----
>>> from tigrbl import TigrblApi
>>> from tigrbl_auth.adapters import LocalAuthNAdapter
>>> api = TigrblApi(engine=ENGINE, authn=LocalAuthNAdapter())
"""

from __future__ import annotations

from tigrbl_auth.deps import AuthNProvider, Request
from ..fastapi_deps import get_principal
from ..principal_ctx import principal_var  # noqa: F401  # ensure ContextVar is initialised
from .auth_context import set_auth_context


class LocalAuthNAdapter(AuthNProvider):
    """
    Thin wrapper that plugs existing *tigrbl_auth* functions into
    the abstract interface expected by Tigrbl.
    """

    # ------------------------------------------------------------------ #
    # FastAPI dependency (mandatory)                                     #
    # ------------------------------------------------------------------ #
    async def get_principal(self, request: Request) -> dict:  # noqa: D401
        """
        Delegate to ``tigrbl_auth.fastapi_deps.get_principal`` and forward
        whatever dict it returns.

        Raises
        ------
        fastapi.HTTPException(401)
            If the API‑key / bearer token is invalid or expired.
        """
        principal = await get_principal(request)  # type: ignore[arg-type]
        set_auth_context(request, principal)
        return principal


__all__ = ["LocalAuthNAdapter"]
