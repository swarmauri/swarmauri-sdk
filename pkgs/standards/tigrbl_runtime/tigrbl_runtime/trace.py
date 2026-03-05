# tigrbl/v3/runtime/trace.py
from __future__ import annotations

import datetime as _dt
import random
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, MutableMapping, Optional, Sequence, Tuple

# Public status constants
OK = "ok"
ERROR = "error"
SKIPPED = "skipped"

# Soft caps to avoid unbounded growth
_MAX_STEPS = 5000
_MAX_EVENTS = 2000
_MAX_KV_KEYS = 16
_MAX_SCALAR_LEN = 256


@dataclass
class _TraceState:
    enabled: bool = True
    sampled: bool = True
    started_at: _dt.datetime = field(
        default_factory=lambda: _dt.datetime.now(_dt.timezone.utc)
    )
    t0: float = field(default_factory=time.perf_counter)
    seq: int = 0
    steps: list[Dict[str, Any]] = field(default_factory=list)  # closed steps
    events: list[Dict[str, Any]] = field(default_factory=list)  # loose events
    open: Dict[int, Tuple[str, float, Dict[str, Any]]] = field(
        default_factory=dict
    )  # seq -> (label, t_start, base_kv)
    plan_labels: Tuple[
        str, ...
    ] = ()  # optional: the full ordered plan (for diagnostics)


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────


def init(ctx: Any, *, plan_labels: Optional[Sequence[str]] = None) -> None:
    """
    Initialize tracing for this context. Called once by the kernel before executing the plan.
    Respects cfg.trace.enabled and cfg.trace.sample_rate (0..1).
    """
    st = _get_state(ctx, create=True)

    # Read config (tolerant to missing cfg/attrs)
    cfg = getattr(ctx, "cfg", None)
    enabled = True
    sample_rate = 1.0
    tr = getattr(cfg, "trace", None)
    if tr is not None:
        en = getattr(tr, "enabled", None)
        if isinstance(en, bool):
            enabled = en
        sr = getattr(tr, "sample_rate", None)
        if isinstance(sr, (int, float)):
            sample_rate = max(0.0, min(1.0, float(sr)))

    st.enabled = bool(enabled)
    st.sampled = (random.random() < sample_rate) if st.enabled else False

    if plan_labels:
        st.plan_labels = tuple(str(x) for x in plan_labels[:_MAX_STEPS])


def set_enabled(ctx: Any, enabled: bool) -> None:
    """Force tracing on/off for this context."""
    st = _get_state(ctx, create=True)
    st.enabled = bool(enabled)
    if not st.enabled:
        st.sampled = False


def start(ctx: Any, label: str, **kv: Any) -> int | None:
    """
    Start a trace span for a plan label. Returns a step id (seq) you should pass to end().
    If tracing is disabled or not sampled, returns None.
    """
    st = _get_state(ctx)
    if not _active(st):
        return None
    if len(st.steps) + len(st.open) >= _MAX_STEPS:
        return None  # soft drop

    seq = st.seq = st.seq + 1
    base = _base_entry(label)
    base["seq"] = seq
    base.update(_safe_kv(kv))

    t_start = time.perf_counter()
    st.open[seq] = (label, t_start, base)
    return seq


def end(
    ctx: Any, seq: int | None, status: str = OK, **kv: Any
) -> Optional[Dict[str, Any]]:
    """
    End a previously started span by its seq id. Returns the finalized step dict.
    If seq is None or tracing is inactive, this is a no-op.
    """
    st = _get_state(ctx)
    if not _active(st) or seq is None:
        return None

    opened = st.open.pop(seq, None)
    if opened is None:
        return None  # already closed or never started

    _label, t_start, base = opened
    dur_ms = max(0.0, (time.perf_counter() - t_start) * 1000.0)

    entry = dict(base)
    entry["status"] = str(status or OK)
    entry["dur_ms"] = round(dur_ms, 3)
    # merge extra kv (sanitized), without clobbering base keys unintentionally
    entry.update(_safe_kv(kv))

    if len(st.steps) < _MAX_STEPS:
        st.steps.append(entry)
    return entry


def event(ctx: Any, name: str, **kv: Any) -> None:
    """Record an ad-hoc event (not tied to a plan label)."""
    st = _get_state(ctx)
    if not _active(st) or len(st.events) >= _MAX_EVENTS:
        return
    st.events.append(
        {
            "ts": _iso_now(),
            "name": str(name),
            **_safe_kv(kv),
        }
    )


def attach_error(ctx: Any, seq: int | None, exc: BaseException) -> None:
    """
    Attach a compact, non-sensitive error summary to an open/closed step.
    If `seq` is None or cannot be found, emits a free-standing 'error' event instead.
    """
    info = {
        "err_type": exc.__class__.__name__,
        "err_msg": _safe_scalar(getattr(exc, "detail", None)) or _safe_scalar(str(exc)),
    }

    st = _get_state(ctx)
    if not _active(st):
        return

    # Try to update an open step first
    if seq is not None and seq in st.open:
        label, t_start, base = st.open[seq]
        base.setdefault("error", info)
        return

    # Try to update the last closed step with matching seq
    found = None
    if seq is not None:
        for step in reversed(st.steps):
            if step.get("seq") == seq:
                found = step
                break
    if found is not None:
        found.setdefault("error", info)
        return

    # Fallback: emit an event
    event(ctx, "error", **info)


def snapshot(ctx: Any) -> Dict[str, Any]:
    """
    Return a structured snapshot of the trace suitable for diagnostics endpoints.
    """
    st = _get_state(ctx)
    total_ms = max(0.0, (time.perf_counter() - st.t0) * 1000.0)
    return {
        "enabled": st.enabled,
        "sampled": st.sampled,
        "started_at": st.started_at.isoformat(),
        "duration_ms": round(total_ms, 3),
        "counts": {
            "steps": len(st.steps),
            "open": len(st.open),
            "events": len(st.events),
        },
        "plan": st.plan_labels,
        "steps": tuple(st.steps),  # immutable copy for consumers
        "events": tuple(st.events),
    }


def clear(ctx: Any) -> None:
    """Erase all trace data for this context."""
    tmp = _ensure_temp(ctx)
    tmp.pop("__trace__", None)


@contextmanager
def span(ctx: Any, label: str, **kv: Any):
    """
    Context-manager convenience for start()/end(). On exception, marks status=error
    and attaches a compact error summary; then re-raises.
    """
    seq = start(ctx, label, **kv)
    try:
        yield seq
        end(ctx, seq, status=OK)
    except Exception as e:  # pragma: no cover (kernel normally handles)
        attach_error(ctx, seq, e)
        end(ctx, seq, status=ERROR)
        raise


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def _get_state(ctx: Any, *, create: bool = False) -> _TraceState:
    tmp = _ensure_temp(ctx)
    st = tmp.get("__trace__")
    if isinstance(st, _TraceState):
        return st
    if create or st is None:
        st = _TraceState()
        tmp["__trace__"] = st
        return st
    # If someone stuffed a dict there, replace with a fresh state.
    st = _TraceState()
    tmp["__trace__"] = st
    return st


def _active(st: _TraceState) -> bool:
    return bool(st.enabled and st.sampled)


def _iso_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _parse_label(label: str) -> Dict[str, Any]:
    """
    Parse step_kind:domain:subject@anchor#field into parts.
    Tolerant: any segment may be missing.
    """
    out = {"label": str(label)}
    left, anchor = (label.split("@", 1) + [""])[:2]
    field = None
    if "#" in anchor:
        anchor, field = anchor.split("#", 1)
    parts = left.split(":")
    if parts:
        out["step_kind"] = parts[0] or None
    if len(parts) > 1:
        out["domain"] = parts[1] or None
    if len(parts) > 2:
        out["subject"] = ":".join(parts[2:]) or None  # tolerate extra colons
    out["anchor"] = anchor or None
    out["field"] = field or None
    return out


def _base_entry(label: str) -> Dict[str, Any]:
    entry = _parse_label(label)
    entry["ts"] = _iso_now()
    return entry


def _safe_kv(kv: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Sanitize and cap key/values:
      - keep at most _MAX_KV_KEYS keys
      - value → scalar (bool/int/float/str<=N) or a short type tag
    """
    out: Dict[str, Any] = {}
    for i, (k, v) in enumerate(kv.items()):
        if i >= _MAX_KV_KEYS:
            out["_kv_truncated"] = True
            break
        out[str(k)] = _safe_scalar(v)
    return out


def _safe_scalar(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, (bool, int, float)):
        return v
    if isinstance(v, (bytes, bytearray, memoryview)):
        return f"<{type(v).__name__}:{len(v)}B>"
    s = str(v)
    if len(s) > _MAX_SCALAR_LEN:
        s = s[: _MAX_SCALAR_LEN - 1] + "…"
    return s


__all__ = [
    "OK",
    "ERROR",
    "SKIPPED",
    "init",
    "set_enabled",
    "start",
    "end",
    "event",
    "attach_error",
    "snapshot",
    "clear",
    "span",
]
