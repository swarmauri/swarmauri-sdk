# autoapi/v3/runtime/atoms/out/masking.py
from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional, Sequence
import logging

from ... import events as _ev
from ...kernel import _default_kernel as K

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
    app = getattr(ctx, "app", None)
    model = getattr(ctx, "model", None) or type(getattr(ctx, "obj", None))
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if app and model and alias:
        ov = K.get_opview(app, model, alias)
    else:
        if not (model and alias):
            logger.debug("out:masking: missing ctx.app/model/op and no specs; skipping")
            return
        specs = getattr(ctx, "specs", None) or K.get_specs(model)
        ov = K._compile_opview_from_specs(specs, None)

    temp = _ensure_temp(ctx)
    payload = temp.get("response_payload")
    if payload is None:
        raise RuntimeError("response_payload_missing")

    emit_buf = _ensure_emit_buf(temp)
    skip_aliases = _collect_emitted_aliases(emit_buf)

    if isinstance(payload, dict):
        logger.debug("Masking single-object payload")
        _mask_one(payload, ov.schema_out.by_field, skip_aliases)
    elif isinstance(payload, (list, tuple)):
        logger.debug("Masking list payload with %d items", len(payload))
        for item in payload:
            if isinstance(item, dict):
                _mask_one(item, ov.schema_out.by_field, skip_aliases)
            else:
                logger.debug("Skipping non-dict item in payload: %s", item)
    else:
        logger.debug(
            "Unsupported payload type %s; leaving as-is", type(payload).__name__
        )


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
    item: Dict[str, Any],
    by_field: Mapping[str, Mapping[str, Any]],
    skip_aliases: set[str],
) -> None:
    for field, desc in by_field.items():
        if field not in item or field in skip_aliases:
            continue
        val = item.get(field, None)
        if val is None:
            continue
        if not (desc.get("sensitive") or desc.get("mask_last") is not None):
            continue
        item[field] = _mask_value(val, desc.get("mask_last"))


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
