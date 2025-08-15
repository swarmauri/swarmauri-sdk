# autoapi/v3/__init__.py
"""
AutoAPI v3 – public façade

This package exposes the OpSpec-centric building blocks for binding models,
wiring schemas/handlers/hooks, registering RPC and REST, and mounting optional
transports/diagnostics. Keep usage simple and explicit:

    from autoapi.v3 import include_model, build_jsonrpc_router, mount_diagnostics
    from autoapi.v3 import OpSpec, get_registry, op, op_alias

    # bind a model
    include_model(api, User, app=fastapi_app)

    # mount JSON-RPC & diagnostics (optional)
    app.include_router(build_jsonrpc_router(api), prefix="/rpc")
    app.include_router(mount_diagnostics(api), prefix="/system")
"""

from __future__ import annotations

# ── OpSpec core (source of truth) ──────────────────────────────────────────────
from .opspec import OpSpec, get_registry
from .opspec.decorators import op, op_alias
from .opspec.types import PHASES, HookPhase  # for introspection / advanced use

# ── Bindings orchestration (model & API surface) ───────────────────────────────
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

# ── Runtime executor (advanced/low-level) ──────────────────────────────────────
from .runtime.executor import _invoke  # advanced: run a phase pipeline directly

# ── Schema helpers (builder & info utilities) ──────────────────────────────────
from .schema import _schema, create_list_schema

# ── Transport(s) & System diagnostics (optional) ───────────────────────────────
from .transport.jsonrpc import build_jsonrpc_router
from .system import mount_diagnostics

# ── DB/bootstrap helpers (infra; optional) ─────────────────────────────────────
from .system.dbschema import ensure_schemas, register_sqlite_attach, bootstrap_dbschema

# ── Constants (HTTP method defaults, ctx keys, etc.) ───────────────────────────
from .config.constants import DEFAULT_HTTP_METHODS

from .autoapi import AutoAPI

__all__ = [
    # OpSpec
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
    # Schema
    "_schema",
    "create_list_schema",
    # Transport / System
    "build_jsonrpc_router",
    "mount_diagnostics",
    # DB/infra
    "ensure_schemas",
    "register_sqlite_attach",
    "bootstrap_dbschema",
    # Config
    "DEFAULT_HTTP_METHODS",
    # Factory"
    "AutoAPI",
]
