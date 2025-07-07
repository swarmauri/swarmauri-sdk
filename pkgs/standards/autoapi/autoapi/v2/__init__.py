# autoapi.py
"""
Public façade for the AutoAPI framework.

•  Keeps only lightweight glue code.
•  Delegates real work to sub-modules (impl, hooks, endpoints, gateway, …).
•  Preserves the historical surface:  AutoAPI.Phase, AutoAPI._Hook, ._crud, …
"""


# ─── std / third-party ──────────────────────────────────────────────
from collections import OrderedDict
from typing      import Any, Callable, Dict, Optional, Type, Iterator, AsyncIterator

from fastapi                import APIRouter, Depends
from sqlalchemy.orm         import Session, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession

# ─── local helpers  (thin sub-modules) ──────────────────────────────
from .types     import _Op                                 # pure metadata
from .impl      import (
                    _schema,
                    _crud, 
                    _wrap_rpc, 
                    _commit_or_flush, 
                    _register_routes_and_rpcs,
                )
from .hooks     import Phase, _Hook, _init_hooks, _run
from .endpoints import attach_health_and_methodz
from .gateway   import build_gateway
from .routes    import _nested_prefix                      # path builder
from .tables._base    import Base
from .types     import _SchemaVerb

# ────────────────────────────────────────────────────────────────────
class AutoAPI:
    """High-level façade class exposed to user code."""

    # re-export public enums / protocols so callers retain old dotted paths
    Phase = Phase
    _Hook = _Hook

    # ───────── constructor ─────────────────────────────────────────
    def __init__(
        self,
        *,
        base,
        include: set[Type],
        get_db: Callable[..., Iterator[Session]] | None = None,
        get_async_db: Callable[..., AsyncIterator[AsyncSession]] | None = None,
        authorize: Callable[[str, Any], bool] | None = None,
        prefix: str = "",
        authn_dep: Optional[Any] = None,
    ):
        # lightweight state
        self.base        = base
        self.include     = include
        self.authorize   = authorize
        self.router      = APIRouter(prefix=prefix)
        self.rpc: Dict[str, Callable[[dict, Session], Any]] = {}
        self._registered_tables: set[str] = set()     # ❶ guard against re-adds
        self._method_ids: OrderedDict[str, None] = OrderedDict()

        # ---------- choose providers -----------------------------
        if (get_db is None) and (get_async_db is None):
            raise ValueError("provide get_db or get_async_db")

        self.get_db  = get_db
        self.get_async_db = get_async_db

        # ---------- create schema once ---------------------------
        if include:
            tables = {cls.__table__ for cls in include}     # deduplicate via set
        else:
            raise ValueError("must declare tables to be created")
            tables = set(self.base.metadata.tables.values())

        # run DDL for sync or async provider
        if self.get_db:
            with next(self.get_db()) as db:
                self.base.metadata.create_all(
                    db.get_bind(),
                    checkfirst=True,
                    tables=tables,
                )
        else:  # async path
            import asyncio

            async def _ddl():
                async with self.get_async_db() as adb:
                    await adb.run_sync(
                        self.base.metadata.create_all,
                        checkfirst=True,
                        tables=tables,
                    )

            asyncio.run(_ddl())
        # ---------- collect models, build routes, etc. -----------

        # auth dependency (e.g. OAuth2PasswordBearer() or None)
        self._authn_dep = authn_dep or Depends(lambda: None)

        # initialise hook subsystem
        _init_hooks(self)

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
    schema            = _schema = _schema
    _Op               = _Op
    _crud             = _crud
    _wrap_rpc         = _wrap_rpc
    _run              = _run
    _commit_or_flush   = _commit_or_flush
    _nested_prefix    = _nested_prefix
    _register_routes_and_rpcs = _register_routes_and_rpcs

    @classmethod
    def get_schema(orm_cls: type, tag: _SchemaVerb):
        from .get_schema import get_autoapi_schema
        return get_autoapi_schema(orm_cls, tag)

    # keep __all__ tidy for `from autoapi import *` users
    __all__ = [
        "AutoAPI",
        "Phase",
        "_Hook",
        "Base",
    ]
