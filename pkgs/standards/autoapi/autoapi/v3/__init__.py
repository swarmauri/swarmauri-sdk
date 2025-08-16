# autoapi/v3/__init__.py
"""
AutoAPI v3 – public API

OpSpec-centric building blocks to bind models, wire schemas/handlers/hooks,
register RPC & REST, and (optionally) mount JSON-RPC and diagnostics.

Quick start:
    from autoapi.v3 import include_model, build_jsonrpc_router, mount_diagnostics
    from autoapi.v3 import OpSpec, hook_ctx, op_ctx, alias_ctx

    include_model(api, User, app=fastapi_app)
    app.include_router(build_jsonrpc_router(api), prefix="/rpc")
    app.include_router(mount_diagnostics(api), prefix="/system")
"""

from __future__ import annotations

# ── OpSpec (source of truth) ───────────────────────────────────────────────────
from .opspec import OpSpec, get_registry
from .opspec.types import PHASES, HookPhase

# ── Ctx-only decorators (new surface; replaces legacy opspec.decorators) ───────
from .decorators import alias_ctx, op_ctx, hook_ctx

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
from .schema import _schema, create_list_schema

# ── Transport & Diagnostics (optional) ─────────────────────────────────────────
from .transport.jsonrpc import build_jsonrpc_router
from .system import mount_diagnostics

# ── DB/bootstrap helpers (infra; optional) ─────────────────────────────────────
from .system.dbschema import ensure_schemas, register_sqlite_attach, bootstrap_dbschema

# ── Config constants (defaults used by REST) ───────────────────────────────────
from .config.constants import DEFAULT_HTTP_METHODS
from .autoapi import AutoAPI

from .tables import Base

__all__: list[str] = []

__all__ += ["AutoAPI", "Base"]

__all__ += [
    # OpSpec core
    "OpSpec",
    "get_registry",
    "PHASES",
    "HookPhase",
    # Ctx-only decorators
    "alias_ctx",
    "op_ctx",
    "hook_ctx",
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
    "_schema",
    "create_list_schema",
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
