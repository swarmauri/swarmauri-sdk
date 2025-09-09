# tigrbl/v3/runtime/atoms/resolve/paired_gen.py
from __future__ import annotations

import secrets
import logging
from typing import Any, Dict, MutableMapping, Optional

from ... import events as _ev
from ...opview import opview_from_ctx, _ensure_temp

# Runs in HANDLER phase, before pre:flush (and before storage transforms).
ANCHOR = _ev.RESOLVE_VALUES  # "resolve:values"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """
    resolve:paired_gen@resolve:values

    Purpose
    -------
    Prepare *paired* raw values for columns marked as secret-once/paired.
    The raw value is:
      - taken from inbound virtual input (if provided), or
      - generated securely (e.g., URL-safe token) when inbound is ABSENT.

    Contracts / Conventions
    -----------------------
    - ctx.temp:
        - "virtual_in"         : dict of inbound virtual values (from resolve:assemble)
        - "paired_values"      : dict[field -> {"raw": <str>, "alias": <str>, "meta": {...}}]
        - "persist_from_paired": dict[field -> {"source": ("paired_values", field, "raw")}]
        - "assembled_values"   : dict used for persistence (we DO NOT put raw into it)
        - "generated_paired"   : tuple of fields generated here (diagnostics)
    - Secret-once guarantee is enforced later by emit atoms (post-refresh + readtime).

    Policy
    ------
    - We treat a column as "paired" if any of these flags exist (ColumnSpec or FieldSpec):
        secret_once=True | paired=True | paired_input=True | generate_on_absent=True
      OR if a generator callable is present on the spec (generator/paired_generator/secret_generator).
    - If inbound virtual value for the alias exists, we adopt it as the raw.
    - Otherwise we call the generator if provided, else generate a token.
    - We place a *pointer* into ctx.temp["persist_from_paired"] for storage:to_stored
      to derive the persisted representation right before flush.
    """
    # Non-persisting ops should have pruned this anchor; keep guard for safety.
    if getattr(ctx, "persist", True) is False:
        logger.debug("Skipping resolve:paired_gen; ctx.persist is False")
        return

    logger.debug("Running resolve:paired_gen")
    ov = opview_from_ctx(ctx)
    temp = _ensure_temp(ctx)
    assembled = _ensure_dict(temp, "assembled_values")
    virtual_in = _ensure_dict(temp, "virtual_in")
    paired_values = _ensure_dict(temp, "paired_values")
    persist_from_paired = _ensure_dict(temp, "persist_from_paired")

    generated: list[str] = []

    for field, desc in ov.paired_index.items():
        if field in assembled:
            logger.debug(
                "Field %s already has assembled value; skipping generation", field
            )
            continue

        alias_name = desc.get("alias") or field
        raw = None
        if alias_name in virtual_in:
            raw = virtual_in.get(alias_name)
            logger.debug(
                "Using client-provided raw for field %s via alias %s", field, alias_name
            )

        if raw is None:
            logger.debug("Generating raw value for field %s", field)
            gen = desc.get("gen")
            if callable(gen):
                try:
                    raw = gen(_ctx_view(ctx))
                except Exception:
                    logger.debug("Generator failed for field %s", field)
                    raw = None
            if raw is None:
                raw = _secure_token(desc.get("max_length", 0) or 0)

        if raw is None:
            raise RuntimeError(f"paired_raw_missing:{field}")

        meta = {}
        if "mask_last" in desc:
            meta["mask_last"] = desc["mask_last"]

        paired_values[field] = {"raw": raw, "alias": alias_name, "meta": meta}
        logger.debug("Recorded paired raw for field %s", field)

        persist_from_paired[field] = {"source": ("paired_values", field, "raw")}

        generated.append(field)

    if generated:
        temp["generated_paired"] = tuple(generated)
        logger.debug("Generated paired fields: %s", generated)


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_dict(temp: MutableMapping[str, Any], key: str) -> Dict[str, Any]:
    d = temp.get(key)
    if not isinstance(d, dict):
        d = {}
        temp[key] = d
    return d  # type: ignore[return-value]


def _ctx_view(ctx: Any) -> Dict[str, Any]:
    """Small read-only view for generator callables."""
    return {
        "op": getattr(ctx, "op", None),
        "persist": getattr(ctx, "persist", True),
        "temp": getattr(ctx, "temp", None),
        "tenant": getattr(ctx, "tenant", None),
        "user": getattr(ctx, "user", None),
        "now": getattr(ctx, "now", None),
    }


def _secure_token(max_len: int) -> str:
    """
    Generate a URL-safe token. If max_len > 0, keep within that bound.
    We aim for ~32 bytes entropy by default.
    """
    # 32 bytes → ~43 chars base64-url
    token = secrets.token_urlsafe(32)
    if max_len and max_len > 0 and len(token) > max_len:
        # Trim conservatively; if extremely small, ensure we still return something.
        token = token[: max(8, max_len)]
    return token


__all__ = ["ANCHOR", "run"]
