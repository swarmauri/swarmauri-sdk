# autoapi/v3/bindings/schemas.py
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Callable

from pydantic import BaseModel, Field, create_model

from ..opspec import OpSpec
from ..opspec.types import SchemaRef, SchemaArg  # lazy-capable schema args
from ..schema import _build_schema, _build_list_params, namely_model

logger = logging.getLogger(__name__)

_Key = Tuple[str, str]  # (alias, target)


# ───────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ───────────────────────────────────────────────────────────────────────────────


def _camel(s: str) -> str:
    return "".join(p.capitalize() or "_" for p in s.split("_"))


def _ensure_alias_namespace(model: type, alias: str) -> SimpleNamespace:
    ns = getattr(model.schemas, alias, None)
    if ns is None:
        ns = SimpleNamespace()
        setattr(model.schemas, alias, ns)
    return ns


def _pk_info(model: type) -> Tuple[str, type | Any]:
    """
    Return (pk_name, python_type) for single-PK tables. If composite, returns (pk, Any).
    """
    table = getattr(model, "__table__", None)
    if table is None or not getattr(table, "primary_key", None):
        return ("id", Any)
    cols = list(table.primary_key.columns)  # type: ignore[attr-defined]
    if not cols:
        return ("id", Any)
    if len(cols) > 1:
        # Composite keys: schema builder uses verb='delete' to require what's needed.
        # For bulk_delete we fall back to Any.
        return ("id", Any)
    col = cols[0]
    py_t = getattr(getattr(col, "type", None), "python_type", Any)
    return (getattr(col, "name", "id"), py_t or Any)


def _make_bulk_rows_model(
    model: type, verb: str, item_schema: Type[BaseModel]
) -> Type[BaseModel]:
    """
    Build a wrapper schema with a `rows: List[item_schema]` field.
    """
    name = f"{model.__name__}{_camel(verb)}Request"
    schema = create_model(  # type: ignore[call-arg]
        name,
        rows=(List[item_schema], Field(...)),  # type: ignore[name-defined]
    )
    return namely_model(
        schema,
        name=name,
        doc=f"{verb} request schema for {model.__name__}",
    )


def _make_bulk_ids_model(
    model: type, verb: str, pk_type: type | Any
) -> Type[BaseModel]:
    """
    Build a wrapper schema with an `ids: List[pk_type]` field.
    """
    name = f"{model.__name__}{_camel(verb)}Request"
    schema = create_model(  # type: ignore[call-arg]
        name,
        ids=(List[pk_type], Field(...)),  # type: ignore[name-defined]
    )
    return namely_model(
        schema,
        name=name,
        doc=f"{verb} request schema for {model.__name__}",
    )


def _make_pk_model(
    model: type, verb: str, pk_name: str, pk_type: type | Any
) -> Type[BaseModel]:
    """Build a wrapper schema with a single primary-key field."""
    name = f"{model.__name__}{_camel(verb)}Request"
    schema = create_model(  # type: ignore[call-arg]
        name,
        **{pk_name: (pk_type, Field(...))},  # type: ignore[name-defined]
    )
    return namely_model(
        schema,
        name=name,
        doc=f"{verb} request schema for {model.__name__}",
    )


def _parse_str_ref(s: str) -> Tuple[str, str]:
    """
    Parse dotted schema ref "alias.in" | "alias.out" (and tolerate ".list_out" by mapping to 'out').
    """
    s = s.strip()
    if "." not in s:
        raise ValueError(f"Invalid schema path '{s}', expected 'alias.in|out|list_out'")
    alias, kind = s.split(".", 1)
    kind = kind.strip()
    if kind == "list_out":
        # This codebase only exposes `.out` for list ops; treat list_out as out.
        kind = "out"
    if kind not in {"in", "out"}:
        raise ValueError(f"Invalid schema kind '{kind}', expected 'in' or 'out'")
    return alias.strip(), kind


def _resolve_schema_arg(model: type, arg: SchemaArg) -> Type[BaseModel]:
    """
    Resolve a SchemaArg to an actual Pydantic model class.
    Accepts:
      • Pydantic model classes
      • SchemaRef("alias","in|out|list_out")
      • dotted "alias.in|out|list_out"
      • thunk: lambda cls: cls.schemas.alias.in_ / .out
    """
    if arg is None:  # type: ignore[unreachable]
        return None  # pragma: no cover

    # direct class
    if isinstance(arg, type) and issubclass(arg, BaseModel):
        return arg  # type: ignore[return-value]

    # callable thunk
    if callable(arg):
        res = arg(model)  # type: ignore[misc]
        if not (isinstance(res, type) and issubclass(res, BaseModel)):
            raise TypeError("Schema thunk must return a Pydantic model class")
        return res  # type: ignore[return-value]

    # SchemaRef
    if isinstance(arg, SchemaRef):
        ns = getattr(model, "schemas", None)
        if ns is None or getattr(ns, arg.alias, None) is None:
            raise KeyError(f"Unknown schema alias '{arg.alias}'")
        alias_ns = getattr(ns, arg.alias)
        kind = "out" if arg.kind == "list_out" else arg.kind
        attr = "in_" if kind == "in" else "out"
        res = getattr(alias_ns, attr, None)
        if res is None:
            raise KeyError(f"Schema '{arg.alias}.{attr}' not found on {model.__name__}")
        return res  # type: ignore[return-value]

    # dotted string
    if isinstance(arg, str):
        alias, kind = _parse_str_ref(arg)
        ns = getattr(model, "schemas", None)
        if ns is None or getattr(ns, alias, None) is None:
            raise KeyError(f"Unknown schema alias '{alias}'")
        alias_ns = getattr(ns, alias)
        attr = "in_" if kind == "in" else "out"
        res = getattr(alias_ns, attr, None)
        if res is None:
            raise KeyError(f"Schema '{alias}.{attr}' not found on {model.__name__}")
        return res  # type: ignore[return-value]

    raise TypeError(f"Unsupported SchemaArg type: {type(arg)}")


# ───────────────────────────────────────────────────────────────────────────────
# Core builder (defaults only; overrides are applied later)
# ───────────────────────────────────────────────────────────────────────────────


def _default_schemas_for_spec(model: type, sp: OpSpec) -> Dict[str, Optional[Type[BaseModel]]]:
    """
    Decide default IN/OUT schemas for a given OpSpec (ignores sp.request_model/response_model).
    """
    target = sp.target
    result: Dict[str, Optional[Type[BaseModel]]] = {"in_": None, "out": None}

    # Default element schema used for many OUT shapes
    read_schema: Optional[Type[BaseModel]] = _build_schema(model, verb="read")

    # Canonical targets
    if target == "create":
        result["in_"] = _build_schema(model, verb="create")
        result["out"] = read_schema

    elif target == "read":
        pk_name, pk_type = _pk_info(model)
        result["in_"] = _make_pk_model(model, "read", pk_name, pk_type)
        result["out"] = read_schema

    elif target == "update":
        result["in_"] = _build_schema(model, verb="update")
        result["out"] = read_schema

    elif target == "replace":
        result["in_"] = _build_schema(model, verb="replace")
        result["out"] = read_schema

    elif target == "delete":
        result["in_"] = _build_schema(model, verb="delete")
        result["out"] = read_schema

    elif target == "list":
        params = _build_list_params(model)
        result["in_"] = params
        result["out"] = read_schema

    elif target == "clear":
        params = _build_list_params(model)
        result["in_"] = params
        result["out"] = read_schema

    elif target == "bulk_create":
        item_in = _build_schema(model, verb="create")
        result["in_"] = _make_bulk_rows_model(model, "bulk_create", item_in)
        result["out"] = read_schema

    elif target == "bulk_update":
        item_in = _build_schema(model, verb="update")
        result["in_"] = _make_bulk_rows_model(model, "bulk_update", item_in)
        result["out"] = read_schema

    elif target == "bulk_replace":
        item_in = _build_schema(model, verb="replace")
        result["in_"] = _make_bulk_rows_model(model, "bulk_replace", item_in)
        result["out"] = read_schema

    elif target == "bulk_delete":
        pk_name, pk_type = _pk_info(model)
        result["in_"] = _make_bulk_ids_model(model, "bulk_delete", pk_type)
        result["out"] = read_schema

    elif target == "custom":
        # No opinion on IN; OUT defaults to a read-like element
        result["out"] = read_schema

    else:
        result["out"] = read_schema

    # Fallbacks (keep existing behavior)
    result["in_"] = result["in_"] or _build_schema(model, verb="create")
    result["out"] = result["out"] or read_schema

    return result


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def build_and_attach(
    model: type, specs: Sequence[OpSpec], *, only_keys: Optional[Sequence[_Key]] = None
) -> None:
    """
    Build request and response schemas per OpSpec and attach them under:
        model.schemas.<alias>.in_   -> request model (or None)
        model.schemas.<alias>.out   -> response model (or None)

    Two-pass strategy:
      1) Allocate alias namespaces and attach DEFAULT schemas for all specs
         (ignoring per-spec overrides). Defaults are only set if not already present,
         preserving prior overrides during incremental rebinds.
      2) Resolve and apply overrides from OpSpec.request_model / response_model
         (supports direct class, SchemaRef, dotted string, or lambda thunk).

    If `only_keys` is provided, overrides are limited to those (alias,target) pairs.
    Defaults are still ensured for all specs so cross-op SchemaRefs resolve reliably.
    """
    if not hasattr(model, "schemas"):
        model.schemas = SimpleNamespace()

    wanted = set(only_keys or ())

    # Pass 0: ensure a namespace per alias
    for sp in specs:
        _ = _ensure_alias_namespace(model, sp.alias)

    # Pass 1: attach defaults for all specs (do not clobber existing values)
    for sp in specs:
        ns = _ensure_alias_namespace(model, sp.alias)
        shapes = _default_schemas_for_spec(model, sp)

        # Only set if missing to avoid overwriting any previous overrides
        if getattr(ns, "in_", None) is None and shapes.get("in_") is not None:
            setattr(ns, "in_", shapes["in_"])
        if getattr(ns, "out", None) is None and shapes.get("out") is not None:
            setattr(ns, "out", shapes["out"])

        logger.debug(
            "schemas(default): %s.%s -> in=%s out=%s",
            model.__name__,
            sp.alias,
            getattr(ns, "in_", None).__name__ if getattr(ns, "in_", None) else None,
            getattr(ns, "out", None).__name__ if getattr(ns, "out", None) else None,
        )

    # Pass 2: apply per-spec overrides (respect only_keys if provided)
    for sp in specs:
        key = (sp.alias, sp.target)
        if wanted and key not in wanted:
            continue

        ns = _ensure_alias_namespace(model, sp.alias)

        if sp.request_model is not None:
            try:
                resolved_in = _resolve_schema_arg(model, sp.request_model)  # type: ignore[arg-type]
            except Exception as e:
                logger.exception(
                    "Failed resolving request schema for %s.%s: %s",
                    model.__name__, sp.alias, e
                )
                raise
            setattr(ns, "in_", resolved_in)

        if sp.response_model is not None:
            try:
                resolved_out = _resolve_schema_arg(model, sp.response_model)  # type: ignore[arg-type]
            except Exception as e:
                logger.exception(
                    "Failed resolving response schema for %s.%s: %s",
                    model.__name__, sp.alias, e
                )
                raise
            setattr(ns, "out", resolved_out)

        logger.debug(
            "schemas(override): %s.%s -> in=%s out=%s",
            model.__name__,
            sp.alias,
            getattr(ns, "in_", None).__name__ if getattr(ns, "in_", None) else None,
            getattr(ns, "out", None).__name__ if getattr(ns, "out", None) else None,
        )


__all__ = ["build_and_attach"]
