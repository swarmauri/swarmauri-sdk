# tigrbl/v3/bindings/__init__.py
"""
Tigrbl v3 – Bindings package.

This package wires OpSpec-derived artifacts onto models and an API facade.
Concerns are kept strictly separated:
  • Security deps & extra deps → transport/router only (REST/RPC)
  • System steps → injected by runtime lifecycle (Kernel), not by bindings
  • Atoms → discovered/injected by runtime, not by bindings
  • Hooks → bindable at API / model / op levels (no imperative hooks)

Public surface (re-exports)

Model binding:
  - bind(model, *, only_keys=None)           → builds/refreshes model namespaces
  - rebind(model, *, changed_keys=None)      → targeted refresh

Per-concern builders:
  - build_schemas(model, specs, *, only_keys=None)
      • Seeds schemas declared via @schema_ctx before computing defaults.
      • Supports overrides via SchemaRef("alias","in|out"), "alias.in"/"alias.out", or "raw".
  - build_hooks(model, specs, *, only_keys=None)
      • Merges API → MODEL → OP for pre-like phases; OP → MODEL → API for post/error.
      • No imperative hook source.
  - build_handlers(model, specs, *, only_keys=None)
      • Inserts the core/raw step into the HANDLER phase (other phases handled by runtime).
  - register_rpc(model, specs, *, only_keys=None)
  - build_rest(model, specs, *, only_keys=None)
      • Router-level only; serializes responses iff a response schema exists.

API integration:
  - include_model(api, model, *, app=None, prefix=None, mount_router=True)
  - include_models(api, models, *, app=None, base_prefix=None, mount_router=True)
  - rpc_call(api, model_or_name, method, payload=None, *, db, request=None, ctx=None)
"""

from __future__ import annotations
import logging

# Core model orchestrator
from .model import bind, rebind

# Per-concern builders (aliased for a clean public API)
from .schemas import build_and_attach as build_schemas
from .hooks import normalize_and_attach as build_hooks
from .handlers import build_and_attach as build_handlers
from .rpc import register_and_attach as register_rpc
from .rest import build_router_and_attach as build_rest
from ..response.bind import bind as bind_response

# API facade integration
from .api import include_model, include_models, rpc_call

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/__init__")


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
    "bind_response",
    # api integration
    "include_model",
    "include_models",
    "rpc_call",
]
