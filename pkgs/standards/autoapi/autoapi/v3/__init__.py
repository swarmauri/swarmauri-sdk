# autoapi/v3/__init__.py
"""
AutoAPI v3 – public API

OpSpec-centric building blocks to bind models, wire schemas/handlers/hooks,
register RPC & REST, and (optionally) mount JSON-RPC and diagnostics.

Quick start:
    from autoapi.v3 import include_model, build_jsonrpc_router, mount_diagnostics
    from autoapi.v3 import OpSpec, hook_ctx, op_ctx, alias_ctx, schema_ctx, SchemaRef

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
from .opspec import (
    OpSpec,
    get_registry,
    # types and helpers re-exported from opspec
    TargetOp,
    Arity,
    PersistPolicy,
    HookPhase,
    PHASES,
    SchemaRef,
    SchemaArg,
)

# ── Ctx-only decorators (new surface; replaces legacy opspec.decorators) ───────
from .decorators import alias_ctx, op_ctx, hook_ctx, schema_ctx, alias, op_alias

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
from .system.dbschema import ensure_schemas, register_sqlite_attach, bootstrap_dbschema

# ── Config constants (defaults used by REST) ───────────────────────────────────
from .config.constants import DEFAULT_HTTP_METHODS
from .autoapi import AutoAPI

from .tables import Base
from .types import App


__all__: list[str] = []

__all__ += ["AutoAPI", "Base", "App"]

__all__ += [
    # OpSpec core
    "OpSpec",
    "get_registry",
    # types
    "TargetOp",
    "Arity",
    "PersistPolicy",
    "PHASES",
    "HookPhase",
    "SchemaRef",
    "SchemaArg",
    # Ctx-only decorators
    "alias_ctx",
    "op_ctx",
    "hook_ctx",
    "schema_ctx",
    "alias",
    "op_alias",
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
