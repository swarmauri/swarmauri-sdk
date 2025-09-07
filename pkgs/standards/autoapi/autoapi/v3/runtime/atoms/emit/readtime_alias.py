# autoapi/v3/runtime/atoms/emit/readtime_alias.py
from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional
import logging

from ... import events as _ev
from ...kernel import get_cached_specs

# Runs near the end of the lifecycle, before wire:dump/out:masking.
ANCHOR = _ev.EMIT_ALIASES_READ  # "emit:aliases:readtime"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """
    emit:readtime_alias@emit:aliases:readtime

    Purpose
    -------
    Emit *safe*, read-time aliases into the response extras. This is for values that:
      - can be derived from the hydrated object *without* needing create-time "raw" material, and
      - are safe to expose (masked/truncated if sensitive).

    Examples: key hints (****1234), masked phone/email, display-only IDs, etc.

    Inputs / Conventions
    --------------------
    - ctx.specs : mapping field_name -> ColumnSpec
    - ctx.temp["response_extras"] : dict (filled/extended here)
    - ctx.temp["emit_aliases"]["read"] : audit trail (redacted; no raw)
    - obj : the hydrated ORM object (preferred source of current values)
    - Optional fallbacks for reading values (if provided by the executor):
        ctx.row / ctx.values / ctx.temp["hydrated_values"] : dict-like

    Effects
    -------
    - Computes alias values per configured field and writes them to response_extras[alias]
      (does not overwrite keys that already exist, e.g., from paired_post).
    - Records a minimal descriptor in emit_aliases["read"] (no raw).
    - Never reads or emits any "raw" secret (paired_post already scrubbed).
    """
    logger.debug("Running emit:readtime_alias")
    temp = _ensure_temp(ctx)
    emit_buf = _ensure_emit_buf(temp)
    extras = _ensure_response_extras(temp)

    model = (
        getattr(ctx, "model", None)
        or getattr(ctx, "Model", None)
        or type(getattr(ctx, "obj", None))
    )
    specs: Mapping[str, Any] = getattr(ctx, "specs", None) or (
        get_cached_specs(model) if model else {}
    )
    if not specs:
        logger.debug("No specs available; skipping read-time alias emission")
        return

    for field, colspec in specs.items():
        alias = _infer_alias_from_spec(field, colspec)
        if not alias:
            logger.debug("No alias inferred for field %s", field)
            continue
        # Don't clobber values that were explicitly emitted post-flush
        if alias in extras:
            logger.debug("Alias %s already present in extras; skipping", alias)
            continue

        value = _read_current_value(obj, ctx, field)
        if value is None:
            logger.debug("No current value available for field %s", field)
            continue

        safe_val = _safe_readtime_value(value, colspec)

        # Record into response extras
        extras[alias] = safe_val
        logger.debug("Emitted read-time alias '%s' for field '%s'", alias, field)

        # Minimal audit descriptor (no sensitive content)
        emit_buf["read"].append(
            {
                "field": field,
                "alias": alias,
                "emitted": True,
                "meta": _alias_meta(colspec),
            }
        )


# ──────────────────────────────────────────────────────────────────────────────
# Internals (kept lenient to avoid hard coupling to specs structure)
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def _ensure_emit_buf(temp: MutableMapping[str, Any]) -> Dict[str, list]:
    buf = temp.get("emit_aliases")
    if not isinstance(buf, dict):
        buf = {"pre": [], "post": [], "read": []}
        temp["emit_aliases"] = buf
    else:
        buf.setdefault("pre", [])
        buf.setdefault("post", [])
        buf.setdefault("read", [])
    return buf  # type: ignore[return-value]


def _ensure_response_extras(temp: MutableMapping[str, Any]) -> Dict[str, Any]:
    extras = temp.get("response_extras")
    if not isinstance(extras, dict):
        extras = {}
        temp["response_extras"] = extras
    return extras  # type: ignore[return-value]


def _infer_alias_from_spec(field: str, colspec: Any) -> Optional[str]:
    """
    Best-effort alias inference from ColumnSpec / IOSpec / FieldSpec.
    Accepts common attribute names; returns None when absent.
    """
    if colspec is None:
        return None
    # Column-level direct hints
    for name in ("emit_alias", "response_alias", "alias_out", "out_alias", "alias"):
        val = getattr(colspec, name, None)
        if isinstance(val, str) and val:
            return val

    # IO-level hints
    io = getattr(colspec, "io", None)
    if io is not None:
        paired = getattr(io, "_paired", None)
        if paired is not None and isinstance(getattr(paired, "alias", None), str):
            if paired.alias:
                return paired.alias
        for name in ("emit_alias", "response_alias", "alias_out", "out_alias", "alias"):
            val = getattr(io, name, None)
            if isinstance(val, str) and val:
                return val

    # Field-level hints
    fld = getattr(colspec, "field", None)
    if fld is not None:
        for name in ("emit_alias", "response_alias", "alias_out", "out_alias", "alias"):
            val = getattr(fld, name, None)
            if isinstance(val, str) and val:
                return val

    return None


def _alias_meta(colspec: Any) -> Dict[str, Any]:
    """Return small, non-sensitive meta about the alias (e.g., masking policy flags)."""
    meta: Dict[str, Any] = {}
    for attr in ("sensitive", "redact", "redact_last"):
        v = getattr(colspec, attr, None)
        if v is None:
            v = getattr(getattr(colspec, "field", None), attr, None)
        if v is not None:
            meta[attr] = bool(v) if isinstance(v, bool) else v
    return meta


def _read_current_value(obj: Optional[object], ctx: Any, field: str) -> Optional[Any]:
    """
    Pull the current value for `field` from the most reliable source we have.
    Preference: object attribute → ctx.row/values → ctx.temp["hydrated_values"].
    """
    if obj is not None and hasattr(obj, field):
        try:
            return getattr(obj, field)
        except Exception:
            pass

    for name in ("row", "values", "current_values"):
        src = getattr(ctx, name, None)
        if isinstance(src, Mapping) and field in src:
            return src.get(field)

    hv = getattr(getattr(ctx, "temp", {}), "get", lambda *a, **k: None)(
        "hydrated_values"
    )  # type: ignore
    if isinstance(hv, Mapping):
        return hv.get(field)

    return None


def _is_sensitive(colspec: Any) -> tuple[bool, Optional[int]]:
    """
    Return (sensitive, keep_last_n) where keep_last_n may be provided via
    'redact_last' on the column or field; True/None means use default N=4.
    """
    # Column-level or Field-level flags
    sensitive = False
    keep_last: Optional[int] = None

    def _probe(obj: Any) -> None:
        nonlocal sensitive, keep_last
        if obj is None:
            return
        if getattr(obj, "sensitive", False) or getattr(obj, "redact", False):
            sensitive = True
        rl = getattr(obj, "redact_last", None)
        if isinstance(rl, bool) and rl:
            sensitive = True
            keep_last = keep_last or 4
        elif isinstance(rl, int) and rl > 0:
            sensitive = True
            keep_last = rl

    _probe(colspec)
    _probe(getattr(colspec, "field", None))

    return sensitive, keep_last


def _mask_value(value: Any, keep_last: Optional[int]) -> str:
    """
    Generic masking for strings/bytes; falls back to a fixed token when unknown.
    """
    if isinstance(value, (bytes, bytearray, memoryview)):
        return "••••"  # do not attempt partial byte disclosure
    s = str(value) if value is not None else ""
    if not s:
        return ""
    n = keep_last if (isinstance(keep_last, int) and keep_last >= 0) else 4
    n = min(n, len(s))
    return "•" * (len(s) - n) + s[-n:]


def _safe_readtime_value(value: Any, colspec: Any) -> Any:
    """
    If the column is sensitive, return a masked 'hint' string; otherwise, echo value.
    Never attempts to reconstruct or emit any original raw secret material.
    """
    sensitive, keep_last = _is_sensitive(colspec)
    if sensitive:
        return _mask_value(value, keep_last)
    return value


__all__ = ["ANCHOR", "run"]
