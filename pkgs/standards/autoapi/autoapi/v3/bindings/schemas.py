# autoapi/v3/bindings/schemas.py
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type

from pydantic import BaseModel, Field, create_model

from ..opspec import OpSpec
from ..schema import _schema as _build_schema
from ..schema import create_list_schema as _build_list_params

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
    if table is None or getattr(table, "primary_key", None) is None:
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
    return create_model(  # type: ignore[call-arg]
        name,
        rows=(List[item_schema], Field(...)),  # type: ignore[name-defined]
    )


def _make_bulk_ids_model(
    model: type, verb: str, pk_type: type | Any
) -> Type[BaseModel]:
    """
    Build a wrapper schema with an `ids: List[pk_type]` field.
    """
    name = f"{model.__name__}{_camel(verb)}Request"
    return create_model(  # type: ignore[call-arg]
        name,
        ids=(List[pk_type], Field(...)),  # type: ignore[name-defined]
    )


def _make_pk_model(
    model: type, verb: str, pk_name: str, pk_type: type | Any
) -> Type[BaseModel]:
    """Build a simple schema requiring a single primary-key field."""
    name = f"{model.__name__}{_camel(verb)}Request"
    return create_model(  # type: ignore[call-arg]
        name,
        **{pk_name: (pk_type, Field(...))},
    )


# ───────────────────────────────────────────────────────────────────────────────
# Core builder
# ───────────────────────────────────────────────────────────────────────────────


def _schemas_for_spec(model: type, sp: OpSpec) -> Dict[str, Optional[Type[BaseModel]]]:
    """
    Decide which IN/OUT/LIST schemas to attach for a given OpSpec.
    Returns a dict with keys: "in_", "out", "list".
    """
    target = sp.target
    result: Dict[str, Optional[Type[BaseModel]]] = {
        "in_": None,
        "out": None,
        "list": None,
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
        # If caller wants "model" return, supply read schema; otherwise keep None (raw)
        if sp.returns == "model":
            result["out"] = result["out"] or read_schema

    elif target == "read":
        # Require primary key in the request
        pk_name, pk_type = _pk_info(model)
        result["in_"] = result["in_"] or _make_pk_model(model, "read", pk_name, pk_type)
        if sp.returns == "model":
            result["out"] = result["out"] or read_schema

    elif target == "update":
        result["in_"] = result["in_"] or _build_schema(model, verb="update")
        if sp.returns == "model":
            result["out"] = result["out"] or read_schema

    elif target == "replace":
        result["in_"] = result["in_"] or _build_schema(model, verb="replace")
        if sp.returns == "model":
            result["out"] = result["out"] or read_schema

    elif target == "delete":
        # Require PK in body for RPC shape; REST may pass it as a path param.
        result["in_"] = result["in_"] or _build_schema(model, verb="delete")
        if sp.returns == "model":
            result["out"] = result["out"] or read_schema
        else:
            # default raw (e.g., {"deleted": 1})
            result["out"] = result["out"] or None

    elif target == "list":
        # Filters/paging in request; element OUT is the read schema
        params = _build_list_params(model)
        result["list"] = params
        result["in_"] = result["in_"] or params
        if sp.returns == "model":
            result["out"] = result["out"] or read_schema

    elif target == "clear":
        # Same filters as list; OUT is raw by default ({"deleted": N})
        params = _build_list_params(model)
        result["list"] = params
        result["in_"] = result["in_"] or params
        if sp.returns == "model":
            result["out"] = result["out"] or read_schema
        else:
            result["out"] = result["out"] or None

    # Bulk variants
    elif target == "bulk_create":
        item_in = _build_schema(model, verb="create")
        result["in_"] = result["in_"] or _make_bulk_rows_model(
            model, "bulk_create", item_in
        )
        if sp.returns == "model":
            result["out"] = result["out"] or read_schema

    elif target == "bulk_update":
        item_in = _build_schema(model, verb="update")
        result["in_"] = result["in_"] or _make_bulk_rows_model(
            model, "bulk_update", item_in
        )
        if sp.returns == "model":
            result["out"] = result["out"] or read_schema

    elif target == "bulk_replace":
        item_in = _build_schema(model, verb="replace")
        result["in_"] = result["in_"] or _make_bulk_rows_model(
            model, "bulk_replace", item_in
        )
        if sp.returns == "model":
            result["out"] = result["out"] or read_schema

    elif target == "bulk_delete":
        pk_name, pk_type = _pk_info(model)
        result["in_"] = result["in_"] or _make_bulk_ids_model(
            model, "bulk_delete", pk_type
        )
        # OUT defaults to raw ({"deleted": N}); only supply model if explicitly requested
        if sp.returns == "model":
            result["out"] = result["out"] or read_schema
        else:
            result["out"] = result["out"] or None

    # Custom ops: use overrides if present; otherwise
    elif target == "custom":
        # No default IN unless provided; OUT uses read schema when returns="model"
        if sp.returns == "model":
            result["out"] = result["out"] or read_schema

    else:
        # Unknown targets – leave as provided
        pass

    return result


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def build_and_attach(
    model: type, specs: Sequence[OpSpec], *, only_keys: Optional[Sequence[_Key]] = None
) -> None:
    """
    Build request/response/list schemas per OpSpec and attach them under:
        model.schemas.<alias>.in_   -> request model (or None)
        model.schemas.<alias>.out   -> response model (or None)
        model.schemas.<alias>.list  -> list/filter params model (or None)

    If `only_keys` is provided, limit work to those (alias,target) pairs.
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

        # Attach only when we have a model; skip None values
        if shapes.get("in_") is not None:
            setattr(ns, "in_", shapes["in_"])
        if shapes.get("out") is not None:
            setattr(ns, "out", shapes["out"])
        if shapes.get("list") is not None:
            setattr(ns, "list", shapes["list"])

        logger.debug(
            "schemas: %s.%s -> in=%s out=%s list=%s",
            model.__name__,
            sp.alias,
            getattr(ns, "in_", None).__name__ if getattr(ns, "in_", None) else None,
            getattr(ns, "out", None).__name__ if getattr(ns, "out", None) else None,
            getattr(ns, "list", None).__name__ if getattr(ns, "list", None) else None,
        )


__all__ = ["build_and_attach"]
