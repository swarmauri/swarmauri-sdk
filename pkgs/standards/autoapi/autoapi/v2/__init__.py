# autoapi.py
"""
Public façade for the AutoAPI framework.

•  Keeps only lightweight glue code.
•  Delegates real work to sub-modules (impl, hooks, endpoints, gateway, …).
•  Preserves the historical surface:  AutoAPI.Phase, AutoAPI._Hook, ._crud, …
"""

from __future__ import annotations

# ─── std / third-party ──────────────────────────────────────────────
from collections import OrderedDict
from typing      import Any, Callable, Dict, Optional, Type

from fastapi           import APIRouter, Depends
from sqlalchemy.orm    import Session, declarative_base

# ─── local helpers  (thin sub-modules) ──────────────────────────────
from .types     import _Op                                 # pure metadata
from .impl      import _schema, _crud, _wrap_rpc, commit_or_flush, _register_routes_and_rpcs
from .hooks     import Phase, _Hook, _init_hooks, _run
from .endpoints import attach_health_and_methodz
from .gateway   import build_gateway
from .routes    import _nested_prefix                      # path builder
from .tables    import Base, metadata

# ────────────────────────────────────────────────────────────────────
class AutoAPI:
    """High-level façade class exposed to user code."""

    # re-export public enums / protocols so callers retain old dotted paths
    Phase = Phase
    _Hook = _Hook

    # ───────── constructor ─────────────────────────────────────────
    def __init__(
        self,
        base: declarative_base,
        get_db: Callable[[], Session],
        *,
        include: set[Type] | None = None,
        authorize: Callable[[str, Any], bool] | None = None,
        prefix: str = "",
        authn_dep: Optional[Any] = None,
    ):
        # lightweight state
        self.base        = base
        self.get_db      = get_db
        self.include     = include
        self.authorize   = authorize
        self.router      = APIRouter(prefix=prefix)
        self.rpc: Dict[str, Callable[[dict, Session], Any]] = {}
        self._method_ids: OrderedDict[str, None] = OrderedDict()

        # auth dependency (e.g. OAuth2PasswordBearer() or None)
        self._authn_dep = authn_dep or Depends(lambda: None)

        # initialise hook subsystem
        _init_hooks(self)

        with next(get_db()) as _db:
            base.metadata.create_all(_db.get_bind(), checkfirst=True)
        attach_health_and_methodz(self, self.get_db)


        # attach JSON-RPC gateway
        self.router.include_router(build_gateway(self))

        # generate CRUD + RPC for every mapped SQLAlchemy model
        for m in base.registry.mappers:
            cls = m.class_
            if include and cls not in include:
                continue
            self._crud(cls)

    # ───────── bound helpers (delegated to sub-modules) ────────────
    _Op               = _Op
    _schema           = _schema
    _crud             = _crud
    _wrap_rpc         = _wrap_rpc
    _run              = _run
    commit_or_flush   = commit_or_flush
    _nested_prefix    = _nested_prefix
    _register_routes_and_rpcs = _register_routes_and_rpcs

    # keep __all__ tidy for `from autoapi import *` users
    __all__ = [
        "AutoAPI",
        "Phase",
        "_Hook",
        "Base",
        "MetaData"
    ]
