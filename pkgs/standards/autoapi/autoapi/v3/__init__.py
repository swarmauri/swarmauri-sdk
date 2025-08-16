# autoapi/v3/__init__.py
"""
AutoAPI v3 – public API

OpSpec-centric building blocks to bind models, wire schemas/handlers/hooks,
register RPC & REST, and (optionally) mount JSON-RPC and diagnostics.

Quick start:
    from autoapi.v3 import include_model, build_jsonrpc_router, attach_diagnostics
    from autoapi.v3 import OpSpec, op, op_alias

    include_model(api, User, app=fastapi_app)
    app.include_router(build_jsonrpc_router(api), prefix="/rpc")
    app.include_router(attach_diagnostics(api), prefix="/system")
"""

from __future__ import annotations

# ── OpSpec (source of truth) ───────────────────────────────────────────────────
from .opspec import OpSpec, get_registry
from .opspec.decorators import op, op_alias
from .opspec.types import PHASES, HookPhase

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
from .schema import _build_schema, _build_list_params

# ── Transport & Diagnostics (optional) ─────────────────────────────────────────
from .transport.jsonrpc import build_jsonrpc_router
from .system import mount_diagnostics

# ── DB/bootstrap helpers (infra; optional) ─────────────────────────────────────
from .system.dbschema import ensure_schemas, register_sqlite_attach, bootstrap_dbschema

# ── Config constants (defaults used by REST) ───────────────────────────────────
from .config.constants import DEFAULT_HTTP_METHODS
from .autoapi import AutoAPI

from .tables import Base

__all__ = []

__all__ += ["AutoAPI", "Base"]

__all__ += [
    # OpSpec core
    "OpSpec",
    "get_registry",
    "op",
    "op_alias",
    "PHASES",
    "HookPhase",
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
