# autoapi.py
"""
Public façade for the AutoAPI framework.

•  Keeps only lightweight glue code.
•  Delegates real work to sub-modules (impl, hooks, endpoints, gateway, …).
•  Preserves the historical surface:  AutoAPI.Phase, AutoAPI._Hook, ._crud, …
"""

# ─── std / third-party ──────────────────────────────────────────────
from collections import OrderedDict
from typing import Any, AsyncIterator, Callable, Dict, Iterator, Type
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .endpoints import attach_health_and_methodz
from .gateway import build_gateway
from .hooks import Phase, _Hook, _init_hooks, _run
from .impl import (
    _crud,
    _register_routes_and_rpcs,
    _schema,
    _wrap_rpc,
)
from .routes import _nested_prefix  # path builder
from .tables._base import Base as Base

# ─── local helpers  (thin sub-modules) ──────────────────────────────
from .types import (
    _Op,  # pure metadata
    _SchemaVerb,
    AuthNProvider,
    MethodType,
    SimpleNamespace,
)
from .schema import _SchemaNS, get_autoapi_schema as get_schema
from .transactional import transactional as _register_tx


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
        prefix: str = "",
        authorize=None,
        authn: "AuthNProvider | None" = None,
    ):
        # lightweight state
        self.base = base
        self.include = include
        self.authorize = authorize
        self.router = APIRouter(prefix=prefix)
        self.rpc: Dict[str, Callable[[dict, Session], Any]] = {}
        self._registered_tables: set[str] = set()  # ❶ guard against re-adds
        # maps "UserCreate" → <callable>; populated lazily by routes_builder
        self._method_ids: OrderedDict[str, Callable[..., Any]] = OrderedDict()
        self._schemas: OrderedDict[str, Type["BaseModel"]] = OrderedDict()
        self._allow_anon: set[str] = set()

        # attribute-style access, e.g.  api.methods.UserCreate(...)
        self.methods: SimpleNamespace = SimpleNamespace()

        # public Schemas namespace
        self.schemas: _SchemaNS = _SchemaNS(self)

        # ---------- choose providers -----------------------------
        if (get_db is None) and (get_async_db is None):
            raise ValueError("provide get_db or get_async_db")

        self.get_db = get_db
        self.get_async_db = get_async_db

        # ---------- add register_transactional---------------------
        self.transactional = MethodType(_register_tx, self)

        # ─── convenience: explicit registration ----------------------
        def _register_existing_tx(
            self, fn: Callable[..., Any], **kw
        ) -> Callable[..., Any]:
            """
            Register *fn* as a transactional handler *after* it was defined.

            Example
            -------
                def bundle_create(p, db): ...
                api.register_transactional(bundle_create,
                                           name='bundle.create')
            """
            return self.transactional(fn, **kw)

        self.register_transactional = MethodType(_register_existing_tx, self)

        # ---------- create schema once ---------------------------
        if include:
            self.tables = {cls.__table__ for cls in include}  # deduplicate via set
        else:
            raise ValueError("must declare tables to be created")
            self.tables = set(self.base.metadata.tables.values())

        # Store DDL creation for later execution
        self._ddl_executed = False

        # ---------- initialise hook subsystem ---------------------

        _init_hooks(self)

        # ---------- collect models, build routes, etc. -----------

        # ---------------- AuthN wiring -----------------
        if authn is not None:  # preferred path
            self._authn = authn
            self._authn_dep = Depends(authn.get_principal)
            # Late‑binding of the injection hook
            authn.register_inject_hook(self)
        else:
            self._authn = None
            self._authn_dep = Depends(lambda: None)

        if self.get_db:
            attach_health_and_methodz(self, get_db=self.get_db)
        else:
            attach_health_and_methodz(self, get_async_db=self.get_async_db)

        # attach JSON-RPC gateway
        self.router.include_router(build_gateway(self))

        # generate CRUD + RPC for every mapped SQLAlchemy model
        for m in base.registry.mappers:
            cls = m.class_
            if include and cls not in include:
                continue
            self._crud(cls)

    async def initialize_async(self):
        """Initialize async database schema. Call this during app startup."""
        if not self._ddl_executed and self.get_async_db:
            async for adb in self.get_async_db():
                # Get the engine from the session
                engine = adb.get_bind()
                await adb.run_sync(
                    lambda _: self.base.metadata.create_all(
                        engine,
                        checkfirst=True,
                        tables=self.tables,
                    )
                )
                break
            self._ddl_executed = True

    def initialize_sync(self):
        """Initialize sync database schema."""
        if not self._ddl_executed and self.get_db:
            with next(self.get_db()) as db:
                self.base.metadata.create_all(
                    db.get_bind(),
                    checkfirst=True,
                    tables=self.tables,
                )
            self._ddl_executed = True

    # ───────── bound helpers (delegated to sub-modules) ────────────
    # schema = staticmethod(_schema)   # <- prevents self-binding
    _schema = _schema  # keep the private alias if you still need it
    _Op = _Op
    _crud = _crud
    _wrap_rpc = _wrap_rpc
    _run = _run
    _nested_prefix = _nested_prefix
    _register_routes_and_rpcs = _register_routes_and_rpcs

    @classmethod
    def get_schema(cls, orm_cls: type, op: _SchemaVerb):
        return get_schema(orm_cls, op)


# keep __all__ tidy for `from autoapi import *` users
__all__ = [
    "AutoAPI",
    "Phase",
    "_Hook",
    "Base",
    "get_schema",
]
