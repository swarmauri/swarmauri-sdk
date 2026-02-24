# tigrbl/v3/bindings/model.py
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Optional, Set, Tuple

from ..op import OpSpec

# Sub-binders (implemented elsewhere)
from . import (
    schemas as _schemas_binding,
)  # build_and_attach(model, specs, only_keys=None) -> None
from . import (
    hooks as _hooks_binding,
)  # normalize_and_attach(model, specs, only_keys=None) -> None
from . import (
    handlers as _handlers_binding,
)  # build_and_attach(model, specs, only_keys=None) -> None
from . import (
    rpc as _rpc_binding,
)  # register_and_attach(model, specs, only_keys=None) -> None
from . import (
    rest as _rest_binding,
)  # build_router_and_attach(model, specs, router=None, only_keys=None) -> None
from . import columns as _columns_binding
from .model_helpers import (
    _Key,
    _drop_old_entries,
    _ensure_model_namespaces,
    build_binding_plan,
)
from .model_registry import _ensure_op_ctx_attach_hook, _ensure_registry_listener

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/model")


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def bind(
    model: type, *, router: Any | None = None, only_keys: Optional[Set[_Key]] = None
) -> Tuple[OpSpec, ...]:
    """
    Build (or refresh) all Tigrbl namespaces on the model class.

    Steps:
      1) Ensure model namespaces exist.
      2) Resolve canonical OpSpecs and merge ctx-only ops (@op_ctx). If both define
         the same (alias,target), the ctx-only op overrides.
      3) Optionally drop old entries for targeted (alias,target) keys.
      4) Merge ctx-only hooks (@hook_ctx) into model.__tigrbl_hooks__ (alias-aware),
         filtering to known PHASES.
      5) Rebuild & attach (scoped by only_keys when provided):
         • schemas (in_/out)
         • hooks (phase chains, with START_TX/END_TX or mark_skip_persist defaults)
         • handlers (raw & handler entrypoint for HANDLER)
         • rpc (model.rpc.<alias>)
         • rest (model.rest.router)
      6) Index ops under model.ops.{all, by_key, by_alias}
      7) Install a registry listener (once) so imperative updates rebind automatically.

    Returns:
      tuple of OpSpec (the effective set).
    """
    _ensure_model_namespaces(model)

    # 0) Columns first
    _columns_binding.build_and_attach(model)

    # 1) Build one universal binding plan/context for this pass
    plan = build_binding_plan(model, router=router, changed_keys=only_keys)

    # 2) Targeted rebuild support: drop old entries and restrict working set if requested
    _drop_old_entries(model, keys=only_keys)
    setattr(model, "__tigrbl_hooks__", plan.context.merged_hooks)

    # 3) Attach schemas, hooks, handlers, rpc, router (sub-binders honor only_keys)
    specs = list(plan.visible_specs)
    _schemas_binding.build_and_attach(model, specs, only_keys=only_keys)
    _hooks_binding.normalize_and_attach(model, specs, only_keys=only_keys)
    _handlers_binding.build_and_attach(model, specs, only_keys=only_keys)
    _rpc_binding.register_and_attach(model, specs, only_keys=only_keys)
    _rest_binding.build_router_and_attach(
        model, specs, router=router, only_keys=only_keys
    )

    # 4) Index on the model (always overwrite with fresh views)
    model.ops = SimpleNamespace(
        all=plan.all_specs,
        by_key=plan.by_key,
        by_alias=plan.by_alias,
    )
    # Maintain `.opspecs` alias for backward compatibility
    model.opspecs = model.ops

    model.alias_map = plan.context.alias_map

    # 5) Ensure we have a registry listener to refresh on changes
    _ensure_registry_listener(model)
    _ensure_op_ctx_attach_hook(model)
    setattr(model, "__tigrbl_op_ctx_watch__", True)

    logger.debug(
        "tigrbl.bindings.model.bind(%s): %d ops bound (visible=%d)",
        model.__name__,
        len(plan.all_specs),
        len(specs),
    )
    return plan.all_specs


def rebind(
    model: type,
    *,
    router: Any | None = None,
    changed_keys: Optional[Set[_Key]] = None,
) -> Tuple[OpSpec, ...]:
    """
    Public helper to trigger a rebind for the model. If `changed_keys` is provided,
    we attempt a targeted refresh; otherwise we rebuild everything.
    """
    return bind(model, router=router, only_keys=changed_keys)


__all__ = ["bind", "rebind"]
