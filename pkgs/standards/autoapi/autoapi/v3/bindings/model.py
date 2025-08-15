# autoapi/v3/bindings/model.py
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import (
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
)

from ..opspec import OpSpec
from ..opspec import resolve as resolve_opspecs
from ..opspec import get_registry, OpspecRegistry
from ..config.constants import REGISTRY_LISTENER_ATTR

# These modules will be implemented next in the bindings package.
# They should expose the functions used below with the given signatures.
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
)  # build_router_and_attach(model, specs, only_keys=None) -> None

logger = logging.getLogger(__name__)


# ───────────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────────

_Key = Tuple[str, str]  # (alias, target)


def _key(sp: OpSpec) -> _Key:
    return (sp.alias, sp.target)


def _ensure_model_namespaces(model: type) -> None:
    """
    Create top-level namespaces on the model class if missing.
    """
    # opspec indexes & metadata
    if not hasattr(model, "opspecs"):
        model.opspecs = SimpleNamespace(all=(), by_key={}, by_alias={})
    # pydantic schemas: .<alias>.in / .<alias>.out / .<alias>.list
    if not hasattr(model, "schemas"):
        model.schemas = SimpleNamespace()
    # hooks: phase chains & raw hook descriptors if you want to expose them
    if not hasattr(model, "hooks"):
        model.hooks = SimpleNamespace()
    # handlers: .<alias>.raw (core/custom), .<alias>.handler (HANDLER chain entry point)
    if not hasattr(model, "handlers"):
        model.handlers = SimpleNamespace()
    # rpc: callables to be registered/mounted elsewhere as JSON-RPC methods
    if not hasattr(model, "rpc"):
        model.rpc = SimpleNamespace()
    # rest: .router (FastAPI/APIRouter or compatible) – built in rest binding
    if not hasattr(model, "rest"):
        model.rest = SimpleNamespace(router=None)
    # basic table metadata for convenience
    if not hasattr(model, "columns"):
        table = getattr(model, "__table__", None)
        cols = tuple(getattr(table, "columns", ()) or ())
        model.columns = tuple(
            getattr(c, "name", None) for c in cols if getattr(c, "name", None)
        )
    if not hasattr(model, "table_config"):
        table = getattr(model, "__table__", None)
        model.table_config = dict(getattr(table, "kwargs", {}) or {})


def _index_specs(
    specs: Sequence[OpSpec],
) -> Tuple[Tuple[OpSpec, ...], Dict[_Key, OpSpec], Dict[str, List[OpSpec]]]:
    all_specs: Tuple[OpSpec, ...] = tuple(specs)
    by_key: Dict[_Key, OpSpec] = {}
    by_alias: Dict[str, List[OpSpec]] = {}
    for sp in specs:
        k = _key(sp)
        by_key[k] = sp
        by_alias.setdefault(sp.alias, []).append(sp)
    return all_specs, by_key, by_alias


def _drop_old_entries(model: type, *, keys: Set[_Key] | None) -> None:
    """
    Remove per-op artifacts for the provided keys before a targeted rebuild.
    Safe no-ops if keys are None (full rebuild happens cleanly by overwrite).
    """
    if not keys:
        return
    # schemas
    for alias, target in keys:
        ns = getattr(model.schemas, alias, None)
        if ns:
            for attr in ("in_", "out", "list"):
                try:
                    delattr(ns, attr)
                except Exception:
                    pass
            # if empty, optionally remove the alias namespace
            if not ns.__dict__:
                try:
                    delattr(model.schemas, alias)
                except Exception:
                    pass
    # handlers
    for alias, target in keys:
        if hasattr(model.handlers, alias):
            try:
                delattr(model.handlers, alias)
            except Exception:
                pass
    # hooks
    for alias, target in keys:
        if hasattr(model.hooks, alias):
            try:
                delattr(model.hooks, alias)
            except Exception:
                pass
    # rpc
    for alias, target in keys:
        if hasattr(model.rpc, alias):
            try:
                delattr(model.rpc, alias)
            except Exception:
                pass
    # REST endpoints will be refreshed wholesale by rest binding as needed


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def bind(model: type, *, only_keys: Optional[Set[_Key]] = None) -> Tuple[OpSpec, ...]:
    """
    Build (or refresh) all AutoAPI namespaces on the model class.

    Steps:
      1) Resolve effective OpSpecs (opspec.resolve).
      2) Ensure model namespaces exist.
      3) Optionally drop old entries for a targeted set of (alias,target) keys.
      4) Rebuild & attach:
         • schemas (in/out/list)
         • hooks (phase chains, with auto START_TX/END_TX defaults)
         • handlers (raw & handler entrypoint for HANDLER)
         • rpc (register callables under model.rpc.<alias>)
         • rest (attach/refresh model.rest.router)
      5) Index opspecs under model.opspecs.{all, by_key, by_alias}
      6) Install a registry listener (once) so imperative updates rebind automatically.

    Returns:
      tuple of OpSpec (the effective set).
    """
    _ensure_model_namespaces(model)

    # 1) Resolve opspecs (source of truth)
    specs: List[OpSpec] = list(resolve_opspecs(model))
    all_specs, by_key, by_alias = _index_specs(specs)

    # 2) Drop per-op artifacts for targeted keys (if any)
    _drop_old_entries(model, keys=only_keys)

    # 3) Attach schemas, hooks, handlers, rpc, router
    #    The submodules should handle `only_keys` and rebuild only what's needed.
    _schemas_binding.build_and_attach(model, specs, only_keys=only_keys)
    _hooks_binding.normalize_and_attach(model, specs, only_keys=only_keys)
    _handlers_binding.build_and_attach(model, specs, only_keys=only_keys)
    _rpc_binding.register_and_attach(model, specs, only_keys=only_keys)
    _rest_binding.build_router_and_attach(model, specs, only_keys=only_keys)

    # 4) Index on the model (always overwrite with fresh views)
    model.opspecs = SimpleNamespace(
        all=all_specs,
        by_key=by_key,
        by_alias=by_alias,
    )

    # 5) Ensure we have a registry listener to refresh on changes
    _ensure_registry_listener(model)

    logger.debug(
        "autoapi.bindings.model.bind(%s): %d ops bound", model.__name__, len(all_specs)
    )
    return all_specs


def rebind(
    model: type, *, changed_keys: Optional[Set[_Key]] = None
) -> Tuple[OpSpec, ...]:
    """
    Public helper to trigger a rebind for the model. If `changed_keys` is provided,
    we attempt a targeted refresh; otherwise we rebuild everything.
    """
    return bind(model, only_keys=changed_keys)


# ───────────────────────────────────────────────────────────────────────────────
# Registry integration
# ───────────────────────────────────────────────────────────────────────────────


def _ensure_registry_listener(model: type) -> None:
    """
    Subscribe (once) to the per-model OpspecRegistry so future register_ops/add/remove/set
    calls automatically refresh the model namespaces.
    """
    reg: OpspecRegistry = get_registry(model)

    # If we already subscribed, skip
    if getattr(model, REGISTRY_LISTENER_ATTR, None):
        return

    def _on_registry_change(registry: OpspecRegistry, changed: Set[_Key]) -> None:
        try:
            # Targeted rebind using changed keys
            rebind(model, changed_keys=changed)
        except Exception as e:  # pragma: no cover
            logger.exception(
                "autoapi: rebind failed for %s on ops %s: %s",
                model.__name__,
                changed,
                e,
            )

    reg.subscribe(_on_registry_change)
    # Keep a reference to avoid GC of the closure and to prevent double-subscribe
    setattr(model, REGISTRY_LISTENER_ATTR, _on_registry_change)


__all__ = ["bind", "rebind"]
