from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Mapping, MutableMapping, Optional, Union

SessionCfg = Union["SessionSpec", Mapping[str, Any], None]


@dataclass(frozen=True)
class SessionSpec:
    """
    Per-session policy for Tigrbl sessions.

    These fields are backend-agnostic hints and constraints. Adapters should
    validate and apply them where supported; critical ones (like isolation and
    read_only) SHOULD be validated and enforced.
    """

    # Transaction policy
    isolation: Optional[str] = (
        None  # "read_committed" | "repeatable_read" | "snapshot" | "serializable"
    )
    read_only: Optional[bool] = None
    autobegin: Optional[bool] = True
    expire_on_commit: Optional[bool] = None

    # Retries & backoff
    retry_on_conflict: Optional[bool] = None
    max_retries: int = 0
    backoff_ms: int = 0
    backoff_jitter: bool = True

    # Timeouts / resources
    statement_timeout_ms: Optional[int] = None
    lock_timeout_ms: Optional[int] = None
    fetch_rows: Optional[int] = None
    stream_chunk_rows: Optional[int] = None

    # Consistency coordinates
    min_lsn: Optional[str] = None
    as_of_ts: Optional[str] = None
    consistency: Optional[str] = None  # "strong" | "bounded_staleness" | "eventual"
    staleness_ms: Optional[int] = None

    # Tenancy & security
    tenant_id: Optional[str] = None
    role: Optional[str] = None
    rls_context: Mapping[str, str] = None

    # Observability
    trace_id: Optional[str] = None
    query_tag: Optional[str] = None
    tag: Optional[str] = None
    tracing_sample: Optional[float] = None

    # Cache / index hints
    cache_read: Optional[bool] = None
    cache_write: Optional[bool] = None
    namespace: Optional[str] = None

    # Data protection / compliance
    kms_key_alias: Optional[str] = None
    classification: Optional[str] = None
    audit: Optional[bool] = None

    # Idempotency & pagination
    idempotency_key: Optional[str] = None
    page_snapshot: Optional[str] = None

    def merge(self, higher: "SessionSpec | Mapping[str, Any] | None") -> "SessionSpec":
        """
        Overlay another spec on top of this one (non-None fields take precedence).
        Use to implement op > model > api > app precedence.
        """
        if higher is None:
            return self
        h = higher if isinstance(higher, SessionSpec) else SessionSpec.from_any(higher)
        if h is None:
            return self
        vals: MutableMapping[str, Any] = {
            f.name: getattr(self, f.name) for f in fields(SessionSpec)
        }
        for f in fields(SessionSpec):
            hv = getattr(h, f.name)
            if hv is not None:
                vals[f.name] = hv
        return SessionSpec(**vals)  # type: ignore[arg-type]

    def to_kwargs(self) -> dict[str, Any]:
        """Return only non-None items as a plain dict (adapters can **kwargs this)."""
        return {
            f.name: getattr(self, f.name)
            for f in fields(SessionSpec)
            if getattr(self, f.name) is not None
        }

    @staticmethod
    def from_any(x: SessionCfg) -> Optional["SessionSpec"]:
        if x is None:
            return None
        if isinstance(x, SessionSpec):
            return x
        if isinstance(x, Mapping):
            m = dict(x)
            # aliases
            if "readonly" in m and "read_only" not in m:
                m["read_only"] = bool(m.pop("readonly"))
            if "iso" in m and "isolation" not in m:
                m["isolation"] = str(m.pop("iso"))
            allowed = {f.name for f in fields(SessionSpec)}
            return SessionSpec(**{k: v for k, v in m.items() if k in allowed})
        raise TypeError(f"Unsupported SessionSpec input: {type(x)}")
