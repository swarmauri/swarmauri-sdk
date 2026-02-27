# tigrbl/__init__.py
"""
Tigrbl – public API

OpSpec-centric building blocks to bind models, wire schemas/handlers/hooks,
register RPC & REST, and (optionally) mount JSON-RPC and diagnostics.

"""

from __future__ import annotations

from ._concrete import Router
from .dispatch import dispatch_operation, resolve_operation

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
from .decorators.engine import engine_ctx
from .decorators.schema import schema_ctx
from .decorators.response import response_ctx
from .specs.response_spec import ResponseSpec

# ── Bindings (model + Router orchestration) ───────────────────────────────────────
from .mapping import (
    bind,
    rebind,
    build_schemas,
    build_hooks,
    build_handlers,
    register_rpc,
    build_rest,
    include_table,
    include_tables,
    rpc_call,
)

# ── Runtime (advanced: run a phase pipeline directly) ──────────────────────────
from .runtime.executor import _invoke

# ── Schemas ────────────────────────────────────────────────────────────────────
from .schema import _build_schema, _build_list_params, get_schema

# ── Transport & Diagnostics (optional) ─────────────────────────────────────────
from .requests import Request
from ._concrete._response import Response
from .system import mount_diagnostics

# ── DB/bootstrap helpers (infra; optional) ─────────────────────────────────────
from .ddl import ensure_schemas, register_sqlite_attach, bootstrap_dbschema

# ── Config constants (defaults used by REST) ───────────────────────────────────
from .config.constants import DEFAULT_HTTP_METHODS
from .concrete.tigrbl_app import TigrblApp
from .router import TigrblRouter, route_ctx
from .table import Base
from .op import Op
from .security import APIKey, HTTPBearer, MutualTLS, OAuth2, OpenIdConnect

__all__: list[str] = []

__all__ += [
    "TigrblApp",
    "TigrblRouter",
    "Router",
    "Base",
    "Op",
    "HTTPBearer",
    "APIKey",
    "OAuth2",
    "OpenIdConnect",
    "MutualTLS",
]

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
    "route_ctx",
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
    "include_table",
    "include_tables",
    "rpc_call",
    # Runtime
    "_invoke",
    # Schemas
    "_build_schema",
    "_build_list_params",
    "get_schema",
    # Transport / Diagnostics
    "mount_diagnostics",
    # DB/infra
    "ensure_schemas",
    "register_sqlite_attach",
    "bootstrap_dbschema",
    # Config
    "DEFAULT_HTTP_METHODS",
    "Request",
    "Response",
    "dispatch_operation",
    "resolve_operation",
]
