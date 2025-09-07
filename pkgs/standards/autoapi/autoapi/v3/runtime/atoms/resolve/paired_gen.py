# autoapi/v3/runtime/atoms/resolve/paired_gen.py
from __future__ import annotations

import secrets
import logging
from typing import Any, Dict, Mapping, MutableMapping, Optional

from ... import events as _ev
from ...kernel import get_cached_specs

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
    - ctx.specs : mapping field -> ColumnSpec
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
        msg = "ctx.persist is False; resolve:paired_gen cannot run"
        logger.debug(msg)
        raise RuntimeError(msg)

    logger.debug("Running resolve:paired_gen")
    model = (
        getattr(ctx, "model", None)
        or getattr(ctx, "Model", None)
        or type(getattr(ctx, "obj", None))
    )
    specs: Mapping[str, Any] = getattr(ctx, "specs", None) or (
        get_cached_specs(model) if model else {}
    )
    if not specs:
        msg = "ctx.specs is required for resolve:paired_gen"
        logger.debug(msg)
        raise RuntimeError(msg)

    temp = _ensure_temp(ctx)
    assembled = _ensure_dict(temp, "assembled_values")
    virtual_in = _ensure_dict(temp, "virtual_in")
    paired_values = _ensure_dict(temp, "paired_values")
    persist_from_paired = _ensure_dict(temp, "persist_from_paired")

    generated: list[str] = []

    for field in sorted(specs.keys()):
        col = specs[field]
        # Skip non-paired columns quickly
        if not _is_paired(col):
            logger.debug("Field %s is not paired; skipping", field)
            continue

        # If client already supplied a persisted value, don't generate.
        if field in assembled:
            logger.debug(
                "Field %s already has assembled value; skipping generation", field
            )
            continue

        # Figure out alias name to look for in virtual input and to emit later.
        alias = _infer_alias_from_spec(field, col)

        # Prefer client-supplied *virtual* raw (via alias) over generation.
        raw = None
        if alias and alias in virtual_in:
            raw = virtual_in.get(alias)
            logger.debug(
                "Using client-provided raw for field %s via alias %s", field, alias
            )

        if raw is None:
            logger.debug("Generating raw value for field %s", field)
            # Generator precedence: explicit generator on ColumnSpec/FieldSpec, else secure token
            gen = _get_generator(col)
            if callable(gen):
                try:
                    raw = gen(_ctx_view(ctx))
                except Exception:
                    logger.debug("Generator failed for field %s", field)
                    # Fall back to secure token on generator failure
                    raw = None
            if raw is None:
                raw = _secure_token(_max_len(col) or 0)

        # If we still couldn't produce a raw (very unlikely), skip safely.
        if raw is None:
            logger.debug("Failed to produce raw value for field %s", field)
            continue

        # Record paired raw (never touch assembled_values with raw).
        meta = _alias_meta(col)
        paired_values[field] = {"raw": raw, "alias": alias or field, "meta": meta}
        logger.debug("Recorded paired raw for field %s", field)

        # Hint to storage step that persisted value must be derived from this raw.
        persist_from_paired[field] = {"source": ("paired_values", field, "raw")}

        generated.append(field)

    if generated:
        temp["generated_paired"] = tuple(generated)
        logger.debug("Generated paired fields: %s", generated)


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


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
        "specs": getattr(ctx, "specs", None),
        "temp": getattr(ctx, "temp", None),
        "tenant": getattr(ctx, "tenant", None),
        "user": getattr(ctx, "user", None),
        "now": getattr(ctx, "now", None),
    }


def _is_paired(colspec: Any) -> bool:
    """Best-effort detection of secret-once/paired columns."""

    field = getattr(colspec, "field", None)
    io = getattr(colspec, "io", None)
    field_io = getattr(field, "io", None)

    for obj in (colspec, field, io, field_io):
        if obj is None:
            continue
        if getattr(obj, "_paired", None) is not None:
            return True
        if any(
            bool(getattr(obj, name, False))
            for name in ("secret_once", "paired", "paired_input", "generate_on_absent")
        ):
            return True
        if any(
            callable(getattr(obj, name, None))
            for name in ("generator", "paired_generator", "secret_generator")
        ):
            return True
        io = getattr(obj, "io", None)
        if getattr(getattr(io, "_paired", None), "gen", None) is not None:
            return True
    io = getattr(colspec, "io", None)
    if getattr(getattr(io, "_paired", None), "gen", None) is not None:
        return True
    return False


def _get_generator(colspec: Any):
    """Return the first available generator callable, if any."""
    io = getattr(colspec, "io", None)
    if getattr(getattr(io, "_paired", None), "gen", None):
        fn = io._paired.gen
        if callable(fn):
            return fn
    for obj in (colspec, getattr(colspec, "field", None)):
        if obj is None:
            continue
        paired_cfg = getattr(obj, "_paired", None)
        if paired_cfg is not None and callable(getattr(paired_cfg, "gen", None)):
            return paired_cfg.gen
        for name in ("generator", "paired_generator", "secret_generator"):
            fn = getattr(obj, name, None)
            if callable(fn):
                return fn
    return None


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
    # Optional size hint (useful if downstream wants to display max token len)
    mlen = _max_len(colspec)
    if mlen:
        meta["max_length"] = mlen
    return meta


def _max_len(colspec: Any) -> Optional[int]:
    """
    Try to detect a maximum length for the persisted column or its virtual alias.
    Used to bound generated tokens.
    """
    for obj in (
        colspec,
        getattr(colspec, "field", None),
        getattr(colspec, "storage", None),
    ):
        if obj is None:
            continue
        for name in ("max_length", "max_len", "length", "size"):
            v = getattr(obj, name, None)
            if isinstance(v, int) and v > 0:
                return v
    return None


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
