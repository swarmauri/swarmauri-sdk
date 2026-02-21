from __future__ import annotations

import threading
import weakref
from typing import Any, Dict, Generic, Mapping, Optional, Sequence, TypeVar

from ...column.mro_collect import mro_collect_columns

K = TypeVar("K")
V = TypeVar("V")


class _WeakMaybeDict(Generic[K, V]):
    """Dictionary that uses weak references when possible.

    Falls back to strong references when ``key`` cannot be weakly referenced.
    """

    def __init__(self) -> None:
        self._weak: "weakref.WeakKeyDictionary[Any, V]" = weakref.WeakKeyDictionary()
        self._strong: Dict[int, tuple[Any, V]] = {}

    def _use_weak(self, key: Any) -> bool:
        try:
            weakref.ref(key)
            return True
        except TypeError:
            return False

    def __setitem__(self, key: K, value: V) -> None:
        if self._use_weak(key):
            self._weak[key] = value
        else:
            self._strong[id(key)] = (key, value)

    def __getitem__(self, key: K) -> V:
        if self._use_weak(key):
            return self._weak[key]
        return self._strong[id(key)][1]

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        if self._use_weak(key):
            return self._weak.get(key, default)
        return self._strong.get(id(key), (None, default))[1]

    def setdefault(self, key: K, default: V) -> V:
        if self._use_weak(key):
            return self._weak.setdefault(key, default)
        return self._strong.setdefault(id(key), (key, default))[1]

    def pop(self, key: K, default: Optional[V] = None) -> Optional[V]:
        if self._use_weak(key):
            return self._weak.pop(key, default)
        return self._strong.pop(id(key), (None, default))[1]


class _SpecsOnceCache:
    """Thread-safe, compute-once cache of per-model column specs."""

    def __init__(self) -> None:
        self._d: Dict[type, Mapping[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, model: type) -> Mapping[str, Any]:
        try:
            return self._d[model]
        except KeyError:
            pass
        with self._lock:
            rv = self._d.get(model)
            if rv is None:
                rv = mro_collect_columns(model)
                self._d[model] = rv
        return rv

    def prime(self, models: Sequence[type]) -> None:
        for model in models:
            self.get(model)

    def invalidate(self, model: Optional[type] = None) -> None:
        with self._lock:
            if model is None:
                self._d.clear()
            else:
                self._d.pop(model, None)
