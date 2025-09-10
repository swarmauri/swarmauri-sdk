# tigrbl/v3/runtime/atoms/wire/build_in.py
from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional
import logging

from ... import events as _ev

# Runs in PRE_HANDLER just before validation.
ANCHOR = _ev.IN_VALIDATE  # "in:validate"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """
    wire:build_in@in:validate

    Purpose
    -------
    Normalize the inbound request payload into canonical field names based on
    the schema collected by schema:collect_in. This prepares a dict that
    downstream atoms (resolve:assemble, validate_in, etc.) can use.

    What it does
    ------------
    - Reads ctx.temp["schema_in"] (built by schema:collect_in).
    - Extracts a dict-like payload from ctx (ctx.in_data/payload/data/body or Pydantic model).
    - Maps known *aliases* (alias_in) → canonical field names.
    - Keeps only fields enabled for inbound IO; unknown keys captured to diagnostics.
    - Distinguishes **ABSENT** (missing) from present(None) by *not* inserting missing keys.
    - Stores results in ctx.temp["in_values"] and supporting diagnostics.

    Notes
    -----
    - This atom does *not* perform validation—that belongs to wire:validate_in.
    - For bulk inputs, adapters may pre-split and invoke the executor per-item.
    """
    schema_in = _schema_in(ctx)
    if not schema_in:
        logger.debug("No schema_in available; skipping wire:build_in")
        return  # nothing to do

    logger.debug("Running wire:build_in")
    temp = _ensure_temp(ctx)

    payload = _coerce_payload(ctx)
    if not isinstance(payload, Mapping):
        logger.debug("Payload is not a mapping; skipping normalization")
        # Non-mapping payloads are ignored here; adapters can pre-normalize.
        return

    by_field: Mapping[str, Mapping[str, Any]] = schema_in.get("by_field", {})  # type: ignore[assignment]
    # Build alias→field and ingress whitelist (field and alias forms)
    alias_to_field: Dict[str, str] = {}
    ingress_keys: set[str] = set()

    for fname, entry in by_field.items():
        alias = _safe_str(entry.get("alias_in"))
        ingress_keys.add(fname)
        if alias:
            alias_to_field[alias] = fname
            ingress_keys.add(alias)

    # Normalize
    in_values: Dict[str, Any] = {}
    present_fields: set[str] = set()
    unknown_keys: Dict[str, Any] = {}

    # First pass: direct field-name matches win
    for key, val in payload.items():
        if key in by_field:
            in_values[key] = val
            present_fields.add(key)
        else:
            # Track unknowns for now; we may reclassify as alias below
            unknown_keys[key] = val

    # Second pass: alias matches for anything not already set
    for key, val in list(unknown_keys.items()):
        target = alias_to_field.get(key)
        if target and target not in in_values:
            logger.debug("Resolved alias %s -> %s", key, target)
            in_values[target] = val
            present_fields.add(target)
            unknown_keys.pop(key, None)

    # Keep minimal diagnostics
    temp["in_values"] = in_values
    temp["in_present"] = tuple(sorted(present_fields))
    if unknown_keys:
        temp["in_unknown"] = tuple(sorted(unknown_keys.keys()))
        logger.debug("Unknown inbound keys: %s", list(unknown_keys.keys()))
        # optionally stash raw unknowns for tooling (avoid huge payloads)
        if len(unknown_keys) <= 16:  # small guard
            temp["in_unknown_samples"] = {
                k: unknown_keys[k] for k in list(unknown_keys)[:16]
            }
    logger.debug("Normalized inbound values: %s", in_values)


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def _schema_in(ctx: Any) -> Mapping[str, Any]:
    tmp = getattr(ctx, "temp", {})
    sch = getattr(tmp, "get", lambda *_a, **_k: None)("schema_in")  # type: ignore
    if isinstance(sch, Mapping):
        return sch
    # allow adapters to stuff schema_in directly on ctx
    sch2 = getattr(ctx, "schema_in", None)
    return sch2 if isinstance(sch2, Mapping) else {}


def _coerce_payload(ctx: Any) -> Mapping[str, Any] | Any:
    """
    Try to obtain a dict-like payload from common places on the context.
    Accepts Pydantic v1/v2 models and simple dataclasses.
    """
    # Preferred explicit staging from router/adapters
    for name in ("in_data", "payload", "data", "body"):
        val = getattr(ctx, name, None)
        if val is None:
            continue
        # Mapping already?
        if isinstance(val, Mapping):
            return val
        # Pydantic v2
        if hasattr(val, "model_dump") and callable(getattr(val, "model_dump")):
            try:
                return dict(val.model_dump())
            except Exception:
                pass
        # Pydantic v1
        if hasattr(val, "dict") and callable(getattr(val, "dict")):
            try:
                return dict(val.dict())
            except Exception:
                pass
        # Dataclass?
        try:
            import dataclasses as _dc  # local import; safe if missing

            if _dc.is_dataclass(val):
                return _dc.asdict(val)
        except Exception:
            pass
        return val  # give back as-is; validator can complain later
    return {}


def _safe_str(v: Any) -> Optional[str]:
    return v if isinstance(v, str) and v else None


__all__ = ["ANCHOR", "run"]
