# tigrbl/__init__.py
"""
Tigrbl – public API

OpSpec-centric building blocks to bind models, wire schemas/handlers/hooks,
register RPC & REST, and (optionally) mount JSON-RPC and diagnostics.

Quick start:
    from tigrbl import include_model, build_jsonrpc_router, mount_diagnostics
    from tigrbl import OpSpec, hook_ctx, op_ctx, alias_ctx, schema_ctx, SchemaRef

    include_model(api, User, app=fastapi_app)
    app.include_router(build_jsonrpc_router(api), prefix="/rpc")
    app.include_router(mount_diagnostics(api), prefix="/system")

    # Example: custom op using an existing schema
    @op_ctx(alias="search", target="custom", arity="collection",
            request_schema=SchemaRef("Search", "in"),
            response_schema=SchemaRef("Search", "out"))
    def search(cls, ctx):
        ...
"""

from __future__ import annotations

# ── OpSpec (source of truth) ───────────────────────────────────────────────────
from .op import (
    OpSpec,
    get_registry,
    # types and helpers re-exported from ops
    TargetOp,
    Arity,
    PersistPolicy,
    PHASE,
    HookPhase,
    PHASES,
)
from .schema.types import SchemaRef, SchemaArg

# ── Ctx-only decorators (new surface; replaces legacy ops.decorators) ─────────

from .op import alias_ctx, op_ctx, alias, op_alias
from .hook import hook_ctx
from .engine.decorators import engine_ctx
from .schema.decorators import schema_ctx
from .response.decorators import response_ctx
from .response.types import ResponseSpec

# ── Bindings (model + API orchestration) ───────────────────────────────────────
from .bindings import (
    bind,
    rebind,
    build_schemas,
    build_hooks,
    build_handlers,
    register_rpc,
    build_rest,
    include_model,
    include_models,
    rpc_call,
)

# ── Runtime (advanced: run a phase pipeline directly) ──────────────────────────
from .runtime.executor import _invoke

# ── Schemas ────────────────────────────────────────────────────────────────────
from .schema import _build_schema, _build_list_params, get_schema

# ── Transport & Diagnostics (optional) ─────────────────────────────────────────
from .transport.jsonrpc import build_jsonrpc_router
from .system import mount_diagnostics

# ── DB/bootstrap helpers (infra; optional) ─────────────────────────────────────
from .ddl import ensure_schemas, register_sqlite_attach, bootstrap_dbschema

# ── Config constants (defaults used by REST) ───────────────────────────────────
from .config.constants import DEFAULT_HTTP_METHODS
from .app.tigrbl_app import TigrblApp
from .api import Api, TigrblApi

from .table import Base
from .op import Op
from .app._app import App


__all__: list[str] = []

__all__ += ["TigrblApp", "TigrblApi", "Api", "Base", "App", "Op"]

__all__ += [
    # OpSpec core
    "OpSpec",
    "get_registry",
    # types
    "TargetOp",
    "Arity",
    "PersistPolicy",
    "PHASE",
    "PHASES",
    "HookPhase",
    "SchemaRef",
    "SchemaArg",
    # Ctx-only decorators
    "alias_ctx",
    "op_ctx",
    "hook_ctx",
    "schema_ctx",
    "response_ctx",
    "alias",
    "op_alias",
    "engine_ctx",
    "ResponseSpec",
    # Bindings
    "bind",
    "rebind",
    "build_schemas",
    "build_hooks",
    "build_handlers",
    "register_rpc",
    "build_rest",
    "include_model",
    "include_models",
    "rpc_call",
    # Runtime
    "_invoke",
    # Schemas
    "_build_schema",
    "_build_list_params",
    "get_schema",
    # Transport / Diagnostics
    "build_jsonrpc_router",
    "mount_diagnostics",
    # DB/infra
    "ensure_schemas",
    "register_sqlite_attach",
    "bootstrap_dbschema",
    # Config
    "DEFAULT_HTTP_METHODS",
]
