# autoapi/v2/__init__.py
"""
Public façade for the AutoAPI framework.

•  Keeps only lightweight glue code.
•  Delegates real work to sub-modules (impl, hooks, endpoints, rpcdispatch, …).
•  Preserves the historical surface: AutoAPI._crud, …
"""

# ─── std / third-party ──────────────────────────────────────────────
from collections import OrderedDict
from typing import Any, AsyncIterator, Callable, Iterator, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .endpoints import attach_health_and_methodz
from .rpcdispatch import build_rpcdispatch
from .hooks import Phase, _init_hooks, _run
from .impl import (
    _crud,
    _register_routes_and_rpcs,
    _schema,
    _wrap_rpc,
)
from .impl.routes_builder import _attach
from .routes import _nested_prefix  # path builder
from .tables._base import Base as Base

# ─── local helpers  (thin sub-modules) ──────────────────────────────
from .types import (
    _Op,  # pure metadata
    AuthNProvider,
    MethodType,
    SimpleNamespace,
    Request,
    APIRouter,
    Depends,
)
from .schema import _SchemaNS, get_autoapi_schema as get_schema
from .transactional import register_transaction, transactional
from .cfgs import (  # noqa: F401
    COL_LEVEL_CFGS,
    TAB_LEVEL_CFGS,
    ROUTING_CFGS,
    PERSISTENCE_CFGS,
    PRINCIPAL_CFGS,
    SECURITY_CFGS,
    DEPS_CFGS,
    ROUTING_VERBS,
    BULK_VERBS,
    ALL_VERBS,
    AUTH_CONTEXT_KEY,
    INJECTED_FIELDS_KEY,
    TENANT_ID_KEY,
    USER_ID_KEY,
)

from .ops import register_ops, OpSpec
# ─── db schema bootstrap (dialect-aware; no flags required) ─────────
from .bootstrap_dbschema import ensure_schemas


class _RpcNamespace(dict):
    """Mapping of ``resource.op`` → callable with attribute traversal."""

    def add(self, method_id: str, fn: Callable[[dict, Session], Any]) -> None:
        """Register *fn* under ``resource.op`` and expose as attributes."""
        self[method_id] = fn
        resource, op = method_id.split(".")
        _attach(self, resource, op, fn)


# ────────────────────────────────────────────────────────────────────
class AutoAPI:
    """High-level façade class exposed to user code."""

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
        self._base = base
        self._include = include
        self._authorize = authorize
        self.router = APIRouter(prefix=prefix)
        self.rpc: _RpcNamespace = _RpcNamespace()
        self._registered_tables: set[str] = set()  # ❶ guard against re-adds

        # Cores
        self.core: SimpleNamespace = SimpleNamespace(name="core")
        self.core_raw: SimpleNamespace = SimpleNamespace(name="core_raw")

        # maps "UserCreate" → <callable>; populated lazily by routes_builder
        self._method_ids: OrderedDict[str, Callable[..., Any]] = OrderedDict()
        self._schemas: OrderedDict[str, Type["BaseModel"]] = OrderedDict()

        # attribute-style access, e.g.  api.methods.UserCreate(...)
        self.methods: SimpleNamespace = SimpleNamespace()

        # public Schemas namespace
        self.schemas: _SchemaNS = _SchemaNS(self)

        # Anonymous Routes
        self._allow_anon: set[str] = set()

        # ---------- choose providers -----------------------------
        if (get_db is None) and (get_async_db is None):
            raise ValueError("provide get_db or get_async_db")

        self.get_db = get_db
        self.get_async_db = get_async_db

        # ---------- register transactions ------------------------
        self.register_transaction = MethodType(register_transaction, self)
        self.transactional = MethodType(transactional, self)

        # ---------- create schema once ---------------------------
        if self._include:
            self._tables = {
                cls.__table__ for cls in self._include
            }  # deduplicate via set
        else:
            raise ValueError("must declare tables to be created")
            self._tables = set(self._base.metadata.tables.values())

        # expose included model classes (by class name)
        self.models = SimpleNamespace(**{cls.__name__: cls for cls in self._include})

        # tables namespace is populated with actual SQLAlchemy Table objects
        # AFTER initialize_sync()/initialize_async() applies DDL.
        self.tables: SimpleNamespace = SimpleNamespace()

        # Store DDL creation for later execution
        self._ddl_executed = False

        # ---------- initialise hook subsystem ---------------------
        _init_hooks(self)

        # ---------- collect models, build routes, etc. -----------

        # ---------------- AuthN wiring -----------------
        if authn is not None:
            self._authn = authn

            # Strict auth: provider dep embeds the security scheme via Security(<scheme auto_error=True>)
            async def _strict_auth_dep(
                request: Request,
                principal=Depends(authn.get_principal),
            ):
                # ensure a ctx dict exists for downstream hooks / cores
                ctx = getattr(request.state, "ctx", None)
                if ctx is None or not isinstance(ctx, dict):
                    request.state.ctx = ctx = {}
                # stash principal into the standardized auth context slot
                if isinstance(principal, dict):
                    ac = ctx.setdefault(AUTH_CONTEXT_KEY, {})
                    ac.update(principal)
                # keep legacy attribute too
                request.state.principal = principal
                # best-effort: propagate to contextvar if available
                try:
                    from auto_authn.v2.principal_ctx import principal_var  # optional

                    principal_var.set(principal)
                except Exception:
                    pass
                return principal

            # Optional auth: provider dep embeds the SAME scheme but with auto_error=False
            if hasattr(authn, "get_principal_optional"):

                async def _optional_auth_dep(
                    request: Request,
                    principal=Depends(authn.get_principal_optional),
                ):
                    if not principal:
                        return None
                    return await _strict_auth_dep(request, principal=principal)
            else:
                # Fallback: if optional dep not provided, reuse strict dep
                _optional_auth_dep = _strict_auth_dep

            # expose dependency callables for use in routes & rpc
            self._authn_dep = Depends(_strict_auth_dep)
            self._optional_authn_dep = Depends(_optional_auth_dep)
        else:
            self._authn = None
            # NOOP dependencies
            self._authn_dep = Depends(lambda: None)
            self._optional_authn_dep = Depends(lambda: None)

        if self.get_db:
            attach_health_and_methodz(self, get_db=self.get_db)
        else:
            attach_health_and_methodz(self, get_async_db=self.get_async_db)

        # attach JSON-RPC dispatch
        self.router.include_router(build_rpcdispatch(self))

        # generate CRUD + RPC for every mapped SQLAlchemy model
        for m in base.registry.mappers:
            cls = m.class_
            if self._include and cls not in self._include:
                continue
            self._crud(cls)

    async def initialize_async(self):
        """Initialize async database schema. Call this during app startup."""
        if not self._ddl_executed and self.get_async_db:
            async for adb in self.get_async_db():  # adb is an AsyncSession

                def _sync_bootstrap(arg):
                    # arg is a sync Session (AsyncSession.run_sync) or a Connection (AsyncConnection.run_sync)
                    bind = (
                        arg.get_bind() if hasattr(arg, "get_bind") else arg
                    )  # Session -> (Connection/Engine), else Connection
                    engine = getattr(
                        bind, "engine", bind
                    )  # Connection -> Engine, Engine -> Engine

                    # 1) ensure schemas (handles Postgres + SQLite attach)
                    ensure_schemas(engine)

                    # 2) create tables using the same bind/connection
                    self._base.metadata.create_all(
                        bind=bind,
                        checkfirst=True,
                        tables=self._tables,
                    )

                await adb.run_sync(_sync_bootstrap)
                # now that DDL is applied, expose table objects by class name
                self.tables = SimpleNamespace(
                    **{cls.__name__: cls.__table__ for cls in self._include}
                )
                break
            self._ddl_executed = True

    def initialize_sync(self):
        """Initialize sync database schema."""
        if not self._ddl_executed and self.get_db:
            with next(self.get_db()) as db:  # db is a sync Session
                bind = db.get_bind()  # -> Connection or Engine
                engine = getattr(bind, "engine", bind)  # -> Engine

                # 1) ensure schemas (Postgres + SQLite attach)
                ensure_schemas(engine)

                # 2) create tables on the same bind/connection
                self._base.metadata.create_all(
                    bind=bind,
                    checkfirst=True,
                    tables=self._tables,
                )
            # now that DDL is applied, expose table objects by class name
            self.tables = SimpleNamespace(
                **{cls.__name__: cls.__table__ for cls in self._include}
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


# keep __all__ tidy for `from autoapi import *` users
__all__ = [
    "AutoAPI",
    "Phase",
    "Base",
    "get_schema",
    "register_ops",
    "OpSpec",
]
