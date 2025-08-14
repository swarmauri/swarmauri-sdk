# autoapi/v3/bindings/__init__.py
"""
AutoAPI v3 – Bindings package.

This package wires OpSpec-derived artifacts onto models and an API facade.

Public surface (re-exports):

Model binding:
  - bind(model, *, only_keys=None)           → builds/refreshes model namespaces
  - rebind(model, *, changed_keys=None)      → targeted refresh

Per-concern builders:
  - build_schemas(model, specs, *, only_keys=None)
  - build_hooks(model, specs, *, only_keys=None)
  - build_handlers(model, specs, *, only_keys=None)
  - register_rpc(model, specs, *, only_keys=None)
  - build_rest(model, specs, *, only_keys=None)

API integration:
  - include_model(api, model, *, app=None, prefix=None, mount_router=True)
  - include_models(api, models, *, app=None, base_prefix=None, mount_router=True)
  - rpc_call(api, model_or_name, method, payload=None, *, db, request=None, ctx=None)
"""

from __future__ import annotations

# Core model orchestrator
from .model import bind, rebind

# Per-concern builders (aliased for a clean public API)
from .schemas import build_and_attach as build_schemas
from .hooks import normalize_and_attach as build_hooks
from .handlers import build_and_attach as build_handlers
from .rpc import register_and_attach as register_rpc
from .rest import build_router_and_attach as build_rest

# API facade integration
from .api import include_model, include_models, rpc_call


__all__ = [
    # model orchestrator
    "bind",
    "rebind",
    # per-concern builders
    "build_schemas",
    "build_hooks",
    "build_handlers",
    "register_rpc",
    "build_rest",
    # api integration
    "include_model",
    "include_models",
    "rpc_call",
]
