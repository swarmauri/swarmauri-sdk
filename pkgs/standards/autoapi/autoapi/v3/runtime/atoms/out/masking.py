# autoapi/v3/runtime/atoms/out/masking.py
from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional, Sequence
import logging

from ... import events as _ev

# Runs at the very end of the lifecycle (after wire:dump).
ANCHOR = _ev.OUT_DUMP  # "out:dump"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """
    out:masking@out:dump

    Purpose
    -------
    Mask sensitive top-level fields in the already-built response payload.
    This runs AFTER wire:dump so the payload exists and after emit:readtime_alias
    so alias extras are already present. It does NOT redact explicitly emitted
    alias extras (e.g., secret-once raw tokens) — those are intentional.

    Inputs / Conventions
    --------------------
    - ctx.specs : mapping field_name -> ColumnSpec
    - ctx.temp["response_payload"] : dict or list[dict] (produced by wire:dump)
    - ctx.temp["emit_aliases"]["post"] / ["read"] : lists of descriptors that
      include {"alias": "..."}; these alias keys are skipped (not masked).

    Effects
    -------
    - For each payload item (dict), if a key equals a ColumnSpec field name and
      that column is marked sensitive (via `sensitive`/`redact`/`redact_last`),
      replace the value with a masked hint.
    - Leaves alias extras untouched (based on the alias sets captured from
      emit_aliases.post/read).
    """
    logger.debug("Running out:masking")
    specs: Mapping[str, Any] = getattr(ctx, "specs", {}) or {}
    if not specs:
        logger.debug("No specs provided; skipping masking")
        return

    temp = _ensure_temp(ctx)
    payload = temp.get("response_payload")
    if payload is None:
        logger.debug("No response payload present; skipping masking")
        # If wire:dump hasn't produced a payload, do nothing.
        return

    # Build the set of alias keys that we should never touch here.
    emit_buf = _ensure_emit_buf(temp)
    skip_aliases = _collect_emitted_aliases(emit_buf)

    if isinstance(payload, dict):
        logger.debug("Masking single-object payload")
        _mask_one(payload, specs, skip_aliases)
    elif isinstance(payload, (list, tuple)):
        logger.debug("Masking list payload with %d items", len(payload))
        for item in payload:
            if isinstance(item, dict):
                _mask_one(item, specs, skip_aliases)
            else:
                logger.debug("Skipping non-dict item in payload: %s", item)
    else:
        logger.debug(
            "Unsupported payload type %s; leaving as-is", type(payload).__name__
        )
    # else: unsupported shape; treat as opaque


# ──────────────────────────────────────────────────────────────────────────────
# Internals
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


def _collect_emitted_aliases(
    emit_buf: Mapping[str, Sequence[Mapping[str, Any]]],
) -> set[str]:
    aliases: set[str] = set()
    for bucket in ("post", "read"):
        for d in emit_buf.get(bucket, ()) or ():
            a = d.get("alias")
            if isinstance(a, str) and a:
                aliases.add(a)
    return aliases


def _mask_one(
    item: Dict[str, Any], specs: Mapping[str, Any], skip_aliases: set[str]
) -> None:
    for field, colspec in specs.items():
        # Only touch top-level column keys; never touch known alias keys.
        if field not in item or field in skip_aliases:
            continue
        val = item.get(field, None)
        if val is None:
            continue
        sensitive, keep_last = _is_sensitive(colspec)
        if not sensitive:
            continue
        item[field] = _mask_value(val, keep_last)


def _is_sensitive(colspec: Any) -> tuple[bool, Optional[int]]:
    """
    Return (sensitive, keep_last_n). keep_last_n may come from `redact_last`
    (bool→default=4, or int N). We look on ColumnSpec and then FieldSpec.
    """
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
        return "••••"
    s = str(value) if value is not None else ""
    if not s:
        return ""
    n = keep_last if (isinstance(keep_last, int) and keep_last >= 0) else 4
    n = min(n, len(s))
    return "•" * (len(s) - n) + s[-n:]


__all__ = ["ANCHOR", "run"]
