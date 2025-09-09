# tigrbl/v3/ops/model_registry.py
from __future__ import annotations

from dataclasses import replace
from threading import RLock
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
)
import weakref

from .types import OpSpec, TargetOp

# Listener signature: (registry, changed_keys) -> None
# where changed_keys is a set of (alias, target) tuples indicating what changed.
Listener = Callable[["OpspecRegistry", set[Tuple[str, TargetOp]]], None]


def _spec_key(sp: OpSpec) -> Tuple[str, TargetOp]:
    return (sp.alias, sp.target)


def _ensure_table(sp: OpSpec, table: type) -> OpSpec:
    return sp if sp.table is table else replace(sp, table=table)


def _coerce_to_specs(value: Any, table: type) -> List[OpSpec]:
    """
    Accept flexible inputs (for back-compat with v2):
      • OpSpec
      • Iterable[OpSpec]
      • Mapping[str, dict]  (alias -> kwargs for OpSpec)
      • Iterable[Mapping[str, Any]]  (each includes 'alias' & 'target')
    """
    specs: List[OpSpec] = []
    if value is None:
        return specs

    def _from_kwargs(kwargs: Mapping[str, Any]) -> Optional[OpSpec]:
        if "alias" not in kwargs or "target" not in kwargs:
            return None
        try:
            return OpSpec(table=table, **dict(kwargs))  # type: ignore[arg-type]
        except TypeError:
            return None

    if isinstance(value, OpSpec):
        specs.append(_ensure_table(value, table))
    elif isinstance(value, Mapping):
        for maybe_alias, cfg in value.items():
            if isinstance(cfg, OpSpec):
                specs.append(_ensure_table(cfg, table))
            elif isinstance(cfg, Mapping):
                kw = dict(cfg)
                kw.setdefault("alias", maybe_alias)
                sp = _from_kwargs(kw)
                if sp:
                    specs.append(sp)
    elif isinstance(value, Iterable):
        for item in value:
            if isinstance(item, OpSpec):
                specs.append(_ensure_table(item, table))
            elif isinstance(item, Mapping):
                sp = _from_kwargs(item)
                if sp:
                    specs.append(sp)
    return specs


class OpspecRegistry:
    """
    Per-model OpSpec registry with change notifications.

    - Stores specs keyed by (alias, target).
    - Adds/sets/removes specs and notifies listeners with the changed keys.
    - Binder should call `subscribe(...)` to rebuild a model's namespaces when the
      registry changes (partial rebuild is possible based on changed keys).

    Thread-safe via an instance-level RLock.
    """

    __slots__ = ("_table", "_items", "_lock", "_listeners", "_version")

    def __init__(self, table: type) -> None:
        self._table: type = table
        self._items: Dict[Tuple[str, TargetOp], OpSpec] = {}
        self._lock = RLock()
        # store weakrefs to listener callables where possible; fallback to strong refs
        self._listeners: List[
            Callable[[OpspecRegistry, set[Tuple[str, TargetOp]]], None]
        ] = []
        self._version: int = 0

    # ---------------------------- Introspection ---------------------------- #

    @property
    def table(self) -> type:
        return self._table

    @property
    def version(self) -> int:
        return self._version

    def keys(self) -> Iterator[Tuple[str, TargetOp]]:
        with self._lock:
            return iter(tuple(self._items.keys()))

    def items(self) -> Iterator[Tuple[Tuple[str, TargetOp], OpSpec]]:
        with self._lock:
            return iter(tuple(self._items.items()))

    def values(self) -> Iterator[OpSpec]:
        with self._lock:
            return iter(tuple(self._items.values()))

    def get_all(self) -> Tuple[OpSpec, ...]:
        """Stable snapshot of all specs."""
        with self._lock:
            return tuple(self._items.values())

    # ------------------------------ Listeners ------------------------------ #

    def subscribe(self, fn: Listener) -> None:
        """
        Register a listener to be called on changes.
        NOTE: The listener should be idempotent. It receives (registry, changed_keys).
        """
        with self._lock:
            # Avoid duplicate subscriptions
            if fn not in self._listeners:
                self._listeners.append(fn)

    def unsubscribe(self, fn: Listener) -> None:
        with self._lock:
            try:
                self._listeners.remove(fn)
            except ValueError:
                pass

    def _notify(self, changed: set[Tuple[str, TargetOp]]) -> None:
        # Snapshot listeners to avoid mutation issues during callbacks
        listeners: Tuple[Listener, ...]
        with self._lock:
            listeners = tuple(self._listeners)
        for fn in listeners:
            try:
                fn(self, changed)
            except Exception:
                # Never let a listener error break the registry
                pass

    # ------------------------------- Mutators ------------------------------ #

    def add(self, specs: Iterable[OpSpec] | OpSpec) -> set[Tuple[str, TargetOp]]:
        """
        Add or overwrite one or more specs.
        Returns the set of changed keys.
        """
        if isinstance(specs, OpSpec):
            specs = (specs,)

        changed: set[Tuple[str, TargetOp]] = set()
        with self._lock:
            for sp in specs:
                sp = _ensure_table(sp, self._table)
                k = _spec_key(sp)
                if self._items.get(k) is sp:
                    continue  # exact object already present
                self._items[k] = sp
                changed.add(k)
            if changed:
                self._version += 1
        if changed:
            self._notify(changed)
        return changed

    def set(self, specs: Iterable[OpSpec]) -> set[Tuple[str, TargetOp]]:
        """
        Replace all specs with the provided iterable.
        Returns the set of changed keys (union of removed + added/updated).
        """
        new_map: Dict[Tuple[str, TargetOp], OpSpec] = {}
        for sp in specs:
            sp = _ensure_table(sp, self._table)
            new_map[_spec_key(sp)] = sp

        with self._lock:
            old_keys = set(self._items.keys())
            new_keys = set(new_map.keys())

            removed = old_keys - new_keys
            added_or_updated = {
                k for k in new_keys if self._items.get(k) is not new_map[k]
            }

            changed = removed | added_or_updated
            self._items = new_map
            if changed:
                self._version += 1

        if changed:
            self._notify(changed)
        return changed

    def remove(
        self, alias: str, target: TargetOp | None = None
    ) -> set[Tuple[str, TargetOp]]:
        """
        Remove specs by alias (optionally constrain to a specific target).
        Returns the set of removed keys.
        """
        removed: set[Tuple[str, TargetOp]] = set()
        with self._lock:
            if target is None:
                # remove all targets under this alias
                for k in list(self._items.keys()):
                    if k[0] == alias:
                        self._items.pop(k, None)
                        removed.add(k)
            else:
                k = (alias, target)
                if k in self._items:
                    self._items.pop(k, None)
                    removed.add(k)

            if removed:
                self._version += 1

        if removed:
            self._notify(removed)
        return removed

    def clear(self) -> None:
        with self._lock:
            if not self._items:
                return
            self._items.clear()
            self._version += 1
        self._notify(set())


# ------------------------------------------------------------------------------
# Per-model registry storage (weak keys so classes can be GC'd)
# ------------------------------------------------------------------------------

_REGISTRIES: "weakref.WeakKeyDictionary[type, OpspecRegistry]" = (
    weakref.WeakKeyDictionary()
)
_REG_LOCK = RLock()


def get_registry(table: type) -> OpspecRegistry:
    with _REG_LOCK:
        reg = _REGISTRIES.get(table)
        if reg is None:
            reg = OpspecRegistry(table)
            _REGISTRIES[table] = reg
        return reg


# ------------------------------------------------------------------------------
# Back-compat helpers (v2-style imperative API)
# ------------------------------------------------------------------------------


def register_ops(table: type, specs: Any) -> set[Tuple[str, TargetOp]]:
    """
    Imperative registration (back-compat).
    Accepts OpSpec, iterable of OpSpec, mapping forms, etc.
    Triggers listeners (i.e., binder refresh) on change.
    """
    reg = get_registry(table)
    coerced = _coerce_to_specs(specs, table)
    return reg.add(coerced)


def get_registered_ops(table: type) -> Tuple[OpSpec, ...]:
    """
    Back-compat reader used by the collector.
    """
    return get_registry(table).get_all()


def clear_registry(table: type) -> None:
    get_registry(table).clear()


__all__ = [
    "OpspecRegistry",
    "get_registry",
    "register_ops",
    "get_registered_ops",
    "clear_registry",
]
