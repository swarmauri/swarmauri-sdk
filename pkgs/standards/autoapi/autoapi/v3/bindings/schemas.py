# autoapi/v3/bindings/schemas.py
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type

from pydantic import BaseModel, Field, create_model

from ..opspec import OpSpec
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


# ───────────────────────────────────────────────────────────────────────────────
# Core builder
# ───────────────────────────────────────────────────────────────────────────────


def _schemas_for_spec(model: type, sp: OpSpec) -> Dict[str, Optional[Type[BaseModel]]]:
    """Decide which IN/OUT schemas to attach for a given OpSpec."""
    target = sp.target
    result: Dict[str, Optional[Type[BaseModel]]] = {
        "in_": None,
        "out": None,
    }

    # Respect explicit overrides first
    if sp.request_model is not None:
        result["in_"] = sp.request_model
    if sp.response_model is not None:
        result["out"] = sp.response_model

    # Default element schema used for many OUT shapes
    read_schema: Optional[Type[BaseModel]] = _build_schema(model, verb="read")

    # Canonical targets
    if target == "create":
        result["in_"] = result["in_"] or _build_schema(model, verb="create")
        result["out"] = result["out"] or read_schema

    elif target == "read":
        pk_name, pk_type = _pk_info(model)
        result["in_"] = result["in_"] or _make_pk_model(model, "read", pk_name, pk_type)
        result["out"] = result["out"] or read_schema

    elif target == "update":
        result["in_"] = result["in_"] or _build_schema(model, verb="update")
        result["out"] = result["out"] or read_schema

    elif target == "replace":
        result["in_"] = result["in_"] or _build_schema(model, verb="replace")
        result["out"] = result["out"] or read_schema

    elif target == "delete":
        result["in_"] = result["in_"] or _build_schema(model, verb="delete")
        result["out"] = result["out"] or read_schema

    elif target == "list":
        params = _build_list_params(model)
        result["in_"] = result["in_"] or params
        result["out"] = result["out"] or read_schema

    elif target == "clear":
        params = _build_list_params(model)
        result["in_"] = result["in_"] or params
        result["out"] = result["out"] or read_schema

    elif target == "bulk_create":
        item_in = _build_schema(model, verb="create")
        result["in_"] = result["in_"] or _make_bulk_rows_model(
            model, "bulk_create", item_in
        )
        result["out"] = result["out"] or read_schema

    elif target == "bulk_update":
        item_in = _build_schema(model, verb="update")
        result["in_"] = result["in_"] or _make_bulk_rows_model(
            model, "bulk_update", item_in
        )
        result["out"] = result["out"] or read_schema

    elif target == "bulk_replace":
        item_in = _build_schema(model, verb="replace")
        result["in_"] = result["in_"] or _make_bulk_rows_model(
            model, "bulk_replace", item_in
        )
        result["out"] = result["out"] or read_schema

    elif target == "bulk_delete":
        pk_name, pk_type = _pk_info(model)
        result["in_"] = result["in_"] or _make_bulk_ids_model(
            model, "bulk_delete", pk_type
        )
        result["out"] = result["out"] or read_schema

    elif target == "custom":
        result["out"] = result["out"] or read_schema

    else:
        result["out"] = result["out"] or read_schema

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

    For list/clear operations the list/filter params model is attached as the
    ``in_`` schema. If `only_keys` is provided, limit work to those
    (alias,target) pairs.
    """
    if not hasattr(model, "schemas"):
        model.schemas = SimpleNamespace()

    wanted = set(only_keys or ())

    for sp in specs:
        key = (sp.alias, sp.target)
        if wanted and key not in wanted:
            continue

        ns = _ensure_alias_namespace(model, sp.alias)
        shapes = _schemas_for_spec(model, sp)

        # Attach only non-null schemas so the namespace reflects available shapes
        in_schema = shapes.get("in_")
        if in_schema is not None:
            setattr(ns, "in_", in_schema)
        out_schema = shapes.get("out")
        if out_schema is not None:
            setattr(ns, "out", out_schema)

        logger.debug(
            "schemas: %s.%s -> in=%s out=%s",
            model.__name__,
            sp.alias,
            getattr(ns, "in_", None).__name__ if getattr(ns, "in_", None) else None,
            getattr(ns, "out", None).__name__ if getattr(ns, "out", None) else None,
        )


__all__ = ["build_and_attach"]
