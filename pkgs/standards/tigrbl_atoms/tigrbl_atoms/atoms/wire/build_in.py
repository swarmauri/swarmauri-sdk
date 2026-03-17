# pkgs/standards/tigrbl_atoms/tigrbl/atoms/wire/build_in.py
from __future__ import annotations

from ...types import Atom, Ctx, ExecutingCtx
from ...stages import Executing

import uuid as _uuid
from typing import Any, Dict, Mapping, Optional
import logging

from ... import events as _ev
from ..._opview_helpers import _ensure_schema_in
from .._temp import _ensure_temp
from tigrbl_typing.status.exceptions import HTTPException
from tigrbl_typing.status.mappings import status as _status

# Runs in PRE_HANDLER just before validation.
ANCHOR = _ev.IN_VALIDATE  # "in:validate"

logger = logging.getLogger("uvicorn")

_WRAPPER_KEYS = frozenset({"data", "payload", "body", "item"})


def _is_jsonrpc(ctx: Any) -> bool:
    route = getattr(ctx, "gw_raw", None)
    if getattr(route, "kind", None) == "jsonrpc":
        return True
    temp = getattr(ctx, "temp", None)
    route_ns = temp.get("route") if isinstance(temp, dict) else None
    rpc_env = route_ns.get("rpc_envelope") if isinstance(route_ns, dict) else None
    return isinstance(rpc_env, Mapping) and rpc_env.get("jsonrpc") == "2.0"


def _stage_rpc_error(
    ctx: Any, *, code: int, message: str, data: Mapping[str, Any]
) -> None:
    temp = _ensure_temp(ctx)
    temp["rpc_error"] = {"code": code, "message": message, "data": dict(data)}


def _run(obj: Optional[object], ctx: Any) -> None:
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
    payload = _coerce_payload(ctx)
    schema_in = _ensure_schema_in(ctx)
    payload = _inject_path_params_for_bulk(payload, ctx)
    if payload is not getattr(ctx, "payload", None):
        setattr(ctx, "payload", payload)

    _reject_disallowed_wrapper_keys(payload, schema_in=schema_in or {})
    if not schema_in:
        logger.debug("No schema_in available; skipping wire:build_in")
        return  # nothing to do

    logger.debug("Running wire:build_in")
    temp = _ensure_temp(ctx)
    if not isinstance(payload, Mapping):
        logger.debug("Payload is not a mapping; skipping normalization")
        # Non-mapping payloads are ignored here; adapters can pre-normalize.
        return

    try:
        _reject_disallowed_wrapper_keys(payload, schema_in=schema_in)
    except HTTPException as exc:
        if _is_jsonrpc(ctx):
            detail = exc.detail if isinstance(exc.detail, Mapping) else {}
            _stage_rpc_error(
                ctx,
                code=-32602,
                message="Invalid params",
                data={
                    "reason": detail.get("reason", "Invalid params"),
                    "disallowed_keys": list(detail.get("disallowed_keys", [])),
                },
            )
            return
        raise

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

    _apply_header_in_requirements(
        ctx=ctx, schema_in=schema_in, in_values=in_values, present_fields=present_fields
    )

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


def _headers_lower_map(ctx: Any) -> dict[str, str]:
    headers = getattr(ctx, "headers", None)
    if isinstance(headers, Mapping):
        out: dict[str, str] = {}
        for key, value in headers.items():
            if isinstance(value, list):
                value = value[-1] if value else ""
            out[str(key).lower()] = "" if value is None else str(value)
        return out
    return {}


def _apply_header_in_requirements(
    *,
    ctx: Any,
    schema_in: Mapping[str, Any],
    in_values: Dict[str, Any],
    present_fields: set[str],
) -> None:
    by_field = schema_in.get("by_field", {})
    if not isinstance(by_field, Mapping):
        return
    headers = _headers_lower_map(ctx)
    missing: list[str] = []
    for field, entry in by_field.items():
        if not isinstance(entry, Mapping):
            continue
        header_name = entry.get("header_in")
        if not isinstance(header_name, str) or not header_name:
            continue
        has_body_value = field in present_fields
        header_value = headers.get(header_name.lower())
        if header_value not in (None, "") and not has_body_value:
            in_values[field] = header_value
            present_fields.add(field)
            continue
        if bool(entry.get("header_required_in", False)) and not has_body_value:
            missing.append(header_name)

    if missing:
        detail = {"detail": "Missing required header(s)", "headers": missing}
        if _is_jsonrpc(ctx):
            _stage_rpc_error(
                ctx,
                code=-32602,
                message="Invalid params",
                data={"reason": "Missing required header(s)", "headers": missing},
            )
            return
        raise HTTPException(
            status_code=_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


def _inject_path_params_for_bulk(payload: Any, ctx: Any) -> Any:
    if not isinstance(payload, list):
        return payload

    temp = getattr(ctx, "temp", None)
    route = temp.get("route") if isinstance(temp, Mapping) else None
    path_params = route.get("path_params") if isinstance(route, Mapping) else None
    if not isinstance(path_params, Mapping) or not path_params:
        return payload

    merged: list[Any] = []
    changed = False
    for item in payload:
        if not isinstance(item, Mapping):
            merged.append(item)
            continue
        merged_item = {
            key: _coerce_model_field_value(ctx, key, value)
            for key, value in path_params.items()
        }
        merged_item.update(item)
        changed = changed or merged_item != item
        merged.append(merged_item)

    if changed:
        logger.debug("Injected path params into bulk payload items")
        return merged
    return payload


def _reject_disallowed_wrapper_keys(
    payload: Any, *, schema_in: Mapping[str, Any]
) -> None:
    by_field = schema_in.get("by_field", {})
    field_names = set(by_field.keys()) if isinstance(by_field, Mapping) else set()
    allowed_wrapper_keys = field_names & _WRAPPER_KEYS

    def _check_mapping(item: Mapping[str, Any]) -> None:
        disallowed = sorted(
            key
            for key in item
            if key in _WRAPPER_KEYS and key not in allowed_wrapper_keys
        )
        if disallowed:
            raise HTTPException(
                status_code=_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "reason": "Wrapper keys are not allowed; params must match the operation schema.",
                    "disallowed_keys": disallowed,
                },
            )

    if isinstance(payload, Mapping):
        _check_mapping(payload)
        return

    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, Mapping):
                _check_mapping(item)


def _coerce_model_field_value(ctx: Any, field: str, value: Any) -> Any:
    model = getattr(ctx, "model", None)
    table = getattr(model, "__table__", None) if model is not None else None
    columns = getattr(table, "columns", None) if table is not None else None
    column = columns.get(field) if columns is not None else None
    col_type = getattr(column, "type", None)
    py_type = getattr(col_type, "python_type", None)

    if py_type is _uuid.UUID and isinstance(value, str):
        try:
            return _uuid.UUID(value)
        except Exception:
            return value
    return value


class AtomImpl(Atom[Executing, Executing]):
    name = "wire.build_in"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Executing]) -> Ctx[Executing]:
        _run(obj, ctx)
        return ctx.promote(ExecutingCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
