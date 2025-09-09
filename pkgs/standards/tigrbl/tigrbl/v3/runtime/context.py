# tigrbl/v3/runtime/context.py
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional, Sequence


def _canon_op(op: Optional[str]) -> str:
    return (op or "").strip().lower() or "unknown"


@dataclass
class Context:
    """
    Canonical runtime context shared by the kernel and atoms.

    Minimal contract (consumed by atoms we’ve written so far):
      - op:        operation name (e.g., 'create' | 'update' | 'read' | 'list' | custom)
      - persist:   write vs. read (affects pruning of persist-tied anchors)
      - specs:     mapping of field -> ColumnSpec (frozen at bind time)
      - cfg:       read-only config view (see config.resolver.CfgView)
      - temp:      dict scratchpad used by atoms to exchange data

    Optional adapter slots:
      - model:     owning model type / class
      - obj:       hydrated ORM instance (if any)
      - session:   DB session / unit-of-work handle
      - user, tenant, now: identity/time hints
      - row/values/current_values: mapping fallbacks (for read paths)
      - in_data / payload / data / body: inbound payload staging (for build_in)
    """

    # core
    op: str
    persist: bool
    specs: Mapping[str, Any]
    cfg: Any

    # shared scratchpad
    temp: Dict[str, Any] = field(default_factory=dict)

    # optional context
    model: Any | None = None
    obj: Any | None = None
    session: Any | None = None

    # identity/time
    user: Any | None = None
    tenant: Any | None = None
    now: _dt.datetime | None = None

    # read-path fallbacks
    row: Mapping[str, Any] | None = None
    values: Mapping[str, Any] | None = None
    current_values: Mapping[str, Any] | None = None

    # inbound staging (router/adapters may set any one of these)
    in_data: Any | None = None
    payload: Any | None = None
    data: Any | None = None
    body: Any | None = None

    def __post_init__(self) -> None:
        self.op = _canon_op(self.op)
        # Normalize now to a timezone-aware UTC timestamp when not provided
        if self.now is None:
            try:
                self.now = _dt.datetime.now(_dt.timezone.utc)
            except Exception:  # pragma: no cover
                self.now = _dt.datetime.utcnow().replace(tzinfo=None)

        # Ensure temp is a dict (atoms rely on it)
        if not isinstance(self.temp, dict):
            self.temp = dict(self.temp)

    # ── convenience flags ─────────────────────────────────────────────────────

    @property
    def is_write(self) -> bool:
        """Alias for persist; reads better in some call sites."""
        return bool(self.persist)

    # ── safe read-only view for user callables (generators, default_factory) ──

    def safe_view(
        self,
        *,
        include_temp: bool = False,
        temp_keys: Optional[Sequence[str]] = None,
    ) -> Mapping[str, Any]:
        """
        Return a small, read-only mapping exposing only safe, frequently useful keys.

        By default, temp is NOT included (to avoid leaking internals like paired raw values).
        If include_temp=True, only exposes the keys listed in 'temp_keys' (if provided),
        otherwise exposes a conservative subset.

        This method is intended to be passed into author callables such as
        default_factory(ctx_view) or paired token generators.
        """
        base = {
            "op": self.op,
            "persist": self.persist,
            "model": self.model,
            "specs": self.specs,
            "user": self.user,
            "tenant": self.tenant,
            "now": self.now,
        }
        if include_temp:
            allowed = set(temp_keys or ("assembled_values", "virtual_in"))
            exposed: Dict[str, Any] = {}
            for k in allowed:
                if k in self.temp:
                    exposed[k] = self.temp[k]
            base = {**base, "temp": MappingProxy(exposed)}
        return MappingProxy(base)

    # ── tiny helpers used by atoms / kernel ───────────────────────────────────

    def mark_used_returning(self, value: bool = True) -> None:
        """Flag that DB RETURNING already hydrated values."""
        self.temp["used_returning"] = bool(value)

    def merge_hydrated_values(
        self, mapping: Mapping[str, Any], *, replace: bool = False
    ) -> None:
        """
        Save values hydrated from DB (RETURNING/refresh). If replace=False (default),
        performs a shallow merge into any existing 'hydrated_values'.
        """
        if not isinstance(mapping, Mapping):
            return
        hv = self.temp.get("hydrated_values")
        if replace or not isinstance(hv, dict):
            self.temp["hydrated_values"] = dict(mapping)
        else:
            hv.update(mapping)

    def add_response_extras(
        self, extras: Mapping[str, Any], *, overwrite: Optional[bool] = None
    ) -> Sequence[str]:
        """
        Merge alias extras into temp['response_extras'].
        Returns a tuple of conflicting keys that were skipped when overwrite=False.
        """
        if not isinstance(extras, Mapping) or not extras:
            return ()
        buf = self.temp.get("response_extras")
        if not isinstance(buf, dict):
            buf = {}
            self.temp["response_extras"] = buf
        if overwrite is None:
            # fall back to cfg; atoms call wire:dump to honor final overwrite policy
            overwrite = bool(getattr(self.cfg, "response_extras_overwrite", False))
        conflicts: list[str] = []
        for k, v in extras.items():
            if (k in buf) and not overwrite:
                conflicts.append(k)
                continue
            buf[k] = v
        return tuple(conflicts)

    def get_response_payload(self) -> Any:
        """Return the payload assembled by wire:dump (or None if not yet available)."""
        return self.temp.get("response_payload")

    # ── representation (avoid leaking large/sensitive temp contents) ──────────

    def __repr__(self) -> str:  # pragma: no cover
        model_name = getattr(self.model, "__name__", None) or str(self.model)
        return (
            f"Context(op={self.op!r}, persist={self.persist}, model={model_name!r}, "
            f"user={(getattr(self.user, 'id', None) or None)!r}, temp_keys={sorted(self.temp.keys())})"
        )


# ── tiny immutable mapping proxy (local; no external deps) ────────────────────


class MappingProxy(Mapping[str, Any]):
    """A lightweight, read-only mapping wrapper."""

    __slots__ = ("_d",)

    def __init__(self, data: Mapping[str, Any]):
        self._d = dict(data)

    def __getitem__(self, k: str) -> Any:
        return self._d[k]

    def __iter__(self):
        return iter(self._d)

    def __len__(self) -> int:
        return len(self._d)

    def get(self, key: str, default: Any = None) -> Any:
        return self._d.get(key, default)

    def __repr__(self) -> str:  # pragma: no cover
        return f"MappingProxy({self._d!r})"


__all__ = ["Context", "MappingProxy"]
