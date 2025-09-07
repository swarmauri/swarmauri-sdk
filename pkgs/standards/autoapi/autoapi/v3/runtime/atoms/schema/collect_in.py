# autoapi/v3/runtime/atoms/schema/collect_in.py
from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional
import logging

from ... import events as _ev
from ...kernel import get_cached_specs

# Runs at the very beginning of the lifecycle, before in-model build/validation.
ANCHOR = _ev.SCHEMA_COLLECT_IN  # "schema:collect_in"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """
    schema:collect_in@schema:collect_in

    Purpose
    -------
    Collect a minimal, vendor-neutral description of the inbound schema so that
    wire:build_in/validate_in can construct/validate the request model.
      - Respect IO exposure flags (defaulting to allow input).
      - Heuristically determine "required" vs "optional" per op & storage hints.
      - Capture simple type/shape hints for docs (no pydantic import here).
      - Include optional inbound alias (if authors provided one).

    Inputs (conventions)
    --------------------
    - ctx.specs : Mapping[str, ColumnSpec]
    - ctx.op    : Optional[str]  → e.g. "create" | "update" | "replace" | "merge" | "delete"
    - ctx.cfg   : Optional[...]  → may contain policy overrides (see _required_for_inbound)
    - ctx.persist : bool         → non-persist ops still expose in-model for filters, but usually tiny

    Effects
    -------
    - ctx.temp["schema_in"] = {
        "fields": [
          {
            "name": str,
            "required": bool,
            "virtual": bool,         # storage=None
            "nullable": Optional[bool],
            "py_type": Optional[str],
            "alias_in": Optional[str],
            "max_length": Optional[int],
          }, ...
        ],
        "required": tuple[str, ...],
        "optional": tuple[str, ...],
        "by_field": {name: <entry>, ...},   # convenience
        "order": tuple[str, ...],           # stable field order for wire builder
      }
    """
    logger.debug("Running schema:collect_in")
    model = (
        getattr(ctx, "model", None)
        or getattr(ctx, "Model", None)
        or type(getattr(ctx, "obj", None))
    )
    specs: Mapping[str, Any] = getattr(ctx, "specs", None) or (
        get_cached_specs(model) if model else {}
    )
    if not specs:
        logger.debug("No specs provided; skipping schema collection")
        return

    temp = _ensure_temp(ctx)
    if "schema_in" in temp:
        logger.debug("schema_in already populated; skipping")
        return
    op = (getattr(ctx, "op", None) or "").lower() or None

    fields_sorted = sorted(specs.keys())
    entries: list[Dict[str, Any]] = []
    by_field: Dict[str, Dict[str, Any]] = {}
    req: list[str] = []
    opt: list[str] = []

    for field in fields_sorted:
        col = specs[field]
        storage = getattr(col, "storage", None)
        io = getattr(col, "io", None)
        f = getattr(col, "field", None)

        in_enabled = _bool_attr(io, "in_", "allow_in", "expose_in", default=True)
        if (
            in_enabled
            and storage is not None
            and getattr(storage, "primary_key", False)
        ):
            if not getattr(io, "in_verbs", ()):  # implicit: no inbound verbs specified
                in_enabled = False
        if not in_enabled:
            logger.debug("Field %s excluded from inbound schema", field)
            # Not accepted on input — skip entirely for inbound schema
            continue

        is_virtual = storage is None
        nullable = getattr(storage, "nullable", None) if storage is not None else None
        if op:
            for obj in (f, col, io):
                allow = getattr(obj, "allow_null_in", ())
                if allow and op in allow:
                    # Only relax nullability when the storage layer permits it
                    if nullable is not False:
                        nullable = True
                    break
        alias_in = _infer_in_alias(field, col)
        py_type = _py_type_str(f)

        max_len = _max_len(col)

        required = _required_for_inbound(op, col, nullable, is_virtual, ctx)

        entry = {
            "name": field,
            "required": bool(required),
            "virtual": is_virtual,
            "nullable": nullable
            if nullable is not None
            else (None if is_virtual else True),
            "py_type": py_type,
            "alias_in": alias_in,
            "max_length": max_len,
        }
        entries.append(entry)
        by_field[field] = entry
        (req if entry["required"] else opt).append(field)
        logger.debug(
            "Collected field %s (required=%s, virtual=%s, alias=%s)",
            field,
            entry["required"],
            entry["virtual"],
            alias_in,
        )

    schema_in = {
        "fields": entries,
        "required": tuple(req),
        "optional": tuple(opt),
        "by_field": by_field,
        "order": tuple(e["name"] for e in entries),
    }
    temp["schema_in"] = schema_in
    logger.debug("schema_in populated with %d fields", len(entries))


# ──────────────────────────────────────────────────────────────────────────────
# Internals (tolerant to spec shapes)
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def _bool_attr(obj: Any, *names: str, default: bool) -> bool:
    for n in names:
        if hasattr(obj, n):
            v = getattr(obj, n)
            if isinstance(v, bool):
                return v
    return default


def _py_type_str(field_spec: Any) -> Optional[str]:
    """
    Best-effort Python type name for docs: FieldSpec.py_type or similar.
    Falls back to None if not available.
    """
    if field_spec is None:
        return None
    # Common attributes: py_type, python_type
    for name in ("py_type", "python_type"):
        t = getattr(field_spec, name, None)
        if t is None:
            continue
        try:
            # typing objects / classes → readable names
            return getattr(t, "__name__", None) or str(t)
        except Exception:
            return str(t)
    return None


def _max_len(colspec: Any) -> Optional[int]:
    """
    Try to detect a maximum length for inbound strings (ColumnSpec/FieldSpec/IOSpec hints).
    """
    for obj in (
        colspec,
        getattr(colspec, "field", None),
        getattr(colspec, "io", None),
        getattr(colspec, "storage", None),
    ):
        if obj is None:
            continue
        for name in ("max_length", "max_len", "length", "size"):
            v = getattr(obj, name, None)
            if isinstance(v, int) and v > 0:
                return v
    return None


def _infer_in_alias(field: str, colspec: Any) -> Optional[str]:
    """
    Inbound alias inference (author-supplied). We look for common names.
    """
    # Column-level direct hints
    for obj in (colspec, getattr(colspec, "io", None), getattr(colspec, "field", None)):
        if obj is None:
            continue
        for name in ("alias_in", "request_alias", "in_alias", "alias"):
            val = getattr(obj, name, None)
            if isinstance(val, str) and val:
                return val
    return None


def _required_for_inbound(
    op: Optional[str],
    colspec: Any,
    nullable: Optional[bool],
    is_virtual: bool,
    ctx: Any,
) -> bool:
    """
    Heuristic 'required' decision with override points.
    Policy precedence (first hit wins):
      1) Explicit IO flag: io.required_in / io.required / col.required_in
      2) cfg override: cfg.required_policy[op][field] (if present)
      3) Storage heuristics for CREATE/REPLACE/UPSERT:
         - non-nullable storage
         - no server_default/server_onupdate/computed/autoincrement/identity
         - no ColumnSpec.default_factory
      4) Otherwise optional
    """
    # 1) Explicit IO / column flags
    io = getattr(colspec, "io", None)
    for obj in (io, colspec):
        if obj is None:
            continue
        for name in ("required_in", "required"):
            v = getattr(obj, name, None)
            if isinstance(v, bool):
                return v

    # 2) cfg override (very soft; ignore errors)
    cfg = getattr(ctx, "cfg", None)
    if cfg is not None:
        rp = getattr(cfg, "required_policy", None)
        try:
            if rp and op and hasattr(rp, "get"):
                # expected shape: dict[op][field] = bool
                v = rp.get(op, {}).get(getattr(colspec, "name", None) or "", None)  # type: ignore[attr-defined]
                if isinstance(v, bool):
                    return v
        except Exception:
            pass

    # 3) Storage heuristics (writes)
    if op in {"create", "replace", "merge"} and not is_virtual:
        s = getattr(colspec, "storage", None)
        if s is not None:
            # nullable=False implies required unless a server-side value exists
            non_nullable = nullable is False
            has_server = any(
                bool(getattr(s, name, None))
                for name in (
                    "default",
                    "server_default",
                    "server_onupdate",
                    "computed",
                    "sa_computed",
                    "onupdate",
                    "identity",
                    "sequence",
                    "autoincrement",
                )
            )
            has_factory = callable(getattr(colspec, "default_factory", None))
            if non_nullable and not has_server and not has_factory:
                return True

    # default: optional
    return False


__all__ = ["ANCHOR", "run"]
