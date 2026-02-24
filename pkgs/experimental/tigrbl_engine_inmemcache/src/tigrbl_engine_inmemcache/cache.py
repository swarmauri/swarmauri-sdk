from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Any


@dataclass(frozen=True)
class _Entry:
    value: Any
    expires_at: float | None


class InMemCache:
    def __init__(
        self,
        *,
        namespace: str = "default",
        max_items: int = 100_000,
        default_ttl_s: float | None = None,
    ) -> None:
        if max_items <= 0:
            raise ValueError("max_items must be > 0")
        self.namespace = namespace
        self.max_items = max_items
        self.default_ttl_s = default_ttl_s
        self._lock = RLock()
        self._od: OrderedDict[str, _Entry] = OrderedDict()

    def _now(self) -> float:
        return monotonic()

    def _expired(self, entry: _Entry, now: float) -> bool:
        return entry.expires_at is not None and entry.expires_at <= now

    def _evict_expired_front(self, now: float) -> None:
        for _ in range(16):
            if not self._od:
                return
            key, entry = next(iter(self._od.items()))
            if self._expired(entry, now):
                self._od.pop(key, None)
            else:
                return

    def get(self, key: str, default: Any = None) -> Any:
        now = self._now()
        with self._lock:
            self._evict_expired_front(now)
            entry = self._od.get(key)
            if entry is None:
                return default
            if self._expired(entry, now):
                self._od.pop(key, None)
                return default
            self._od.move_to_end(key, last=True)
            return entry.value

    def set(self, key: str, value: Any, *, ttl_s: float | None = None) -> None:
        now = self._now()
        with self._lock:
            self._evict_expired_front(now)
            local_ttl = self.default_ttl_s if ttl_s is None else ttl_s
            expires_at = (
                (now + local_ttl) if (local_ttl is not None and local_ttl > 0) else None
            )
            self._od[key] = _Entry(value=value, expires_at=expires_at)
            self._od.move_to_end(key, last=True)
            while len(self._od) > self.max_items:
                self._od.popitem(last=False)

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._od.pop(key, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._od.clear()
