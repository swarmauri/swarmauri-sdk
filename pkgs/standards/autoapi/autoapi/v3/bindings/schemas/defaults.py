from __future__ import annotations
import logging

# autoapi/v3/bindings/schemas/defaults.py

from typing import Dict, Optional, Type

from pydantic import BaseModel

from ...op import OpSpec
from ...schema import (
    _build_schema,
    _build_list_params,
    _make_bulk_rows_model,
    _make_bulk_rows_response_model,
    _make_bulk_ids_model,
    _make_deleted_response_model,
    _make_pk_model,
)
from .utils import _pk_info

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/schemas/defaults")


def _default_schemas_for_spec(
    model: type, sp: OpSpec
) -> Dict[str, Optional[Type[BaseModel]]]:
    """
    Decide default IN/OUT schemas for a given OpSpec (ignores sp.request_model/response_model).

    New rules:
      • Canonical targets → provide canonical defaults.
      • Custom target     → no defaults (raw) unless explicitly overridden.
    """
    target = sp.target
    result: Dict[str, Optional[Type[BaseModel]]] = {
        "in_": None,
        "out": None,
        "in_item": None,
        "out_item": None,
    }

    # Element schema for many OUT shapes
    read_schema: Optional[Type[BaseModel]] = _build_schema(model, verb="read")

    # Canonical targets
    if target == "create":
        item_in = _build_schema(model, verb="create")
        result["in_"] = item_in
        result["out"] = read_schema

    elif target == "read":
        pk_name, pk_type = _pk_info(model)
        result["in_"] = _make_pk_model(model, "read", pk_name, pk_type)
        result["out"] = read_schema

    elif target == "update":
        pk_name, _ = _pk_info(model)
        result["in_"] = _build_schema(model, verb="update", exclude={pk_name})
        result["out"] = read_schema

    elif target == "replace":
        pk_name, _ = _pk_info(model)
        result["in_"] = _build_schema(model, verb="replace", exclude={pk_name})
        result["out"] = read_schema

    elif target == "merge":
        pk_name, _ = _pk_info(model)
        result["in_"] = _build_schema(model, verb="update", exclude={pk_name})
        result["out"] = read_schema

    elif target == "delete":
        # For RPC delete, a body with PK is allowed; REST delete ignores body.
        result["in_"] = _build_schema(model, verb="delete")
        result["out"] = read_schema

    elif target == "list":
        params = _build_list_params(model)
        result["in_"] = params
        result["out"] = read_schema

    elif target == "clear":
        params = _build_list_params(model)
        result["in_"] = params
        result["out"] = _make_deleted_response_model(model, "clear")

    elif target == "bulk_create":
        item_in = _build_schema(
            model,
            verb="create",
            name=f"{model.__name__}BulkCreateItem",
        )
        result["in_"] = _make_bulk_rows_model(model, "bulk_create", item_in)
        result["in_item"] = item_in
        result["out"] = (
            _make_bulk_rows_response_model(model, "bulk_create", read_schema)
            if read_schema
            else None
        )
        result["out_item"] = read_schema

    elif target == "bulk_update":
        item_in = _build_schema(
            model,
            verb="update",
            name=f"{model.__name__}BulkUpdateItem",
        )
        result["in_"] = _make_bulk_rows_model(model, "bulk_update", item_in)
        result["in_item"] = item_in
        result["out"] = (
            _make_bulk_rows_response_model(model, "bulk_update", read_schema)
            if read_schema
            else None
        )
        result["out_item"] = read_schema

    elif target == "bulk_replace":
        item_in = _build_schema(
            model,
            verb="replace",
            name=f"{model.__name__}BulkReplaceItem",
        )
        result["in_"] = _make_bulk_rows_model(model, "bulk_replace", item_in)
        result["in_item"] = item_in
        result["out"] = (
            _make_bulk_rows_response_model(model, "bulk_replace", read_schema)
            if read_schema
            else None
        )
        result["out_item"] = read_schema

    elif target == "bulk_merge":
        item_in = _build_schema(
            model,
            verb="update",
            name=f"{model.__name__}BulkMergeItem",
        )
        result["in_"] = _make_bulk_rows_model(model, "bulk_merge", item_in)
        result["in_item"] = item_in
        result["out"] = (
            _make_bulk_rows_response_model(model, "bulk_merge", read_schema)
            if read_schema
            else None
        )
        result["out_item"] = read_schema

    elif target == "bulk_delete":
        pk_name, pk_type = _pk_info(model)
        result["in_"] = _make_bulk_ids_model(model, "bulk_delete", pk_type)
        result["out"] = _make_deleted_response_model(model, "bulk_delete")

    elif target == "custom":
        # Build schemas for custom operations based on verb-specific IO specs
        alias = sp.alias
        specs = getattr(model, "__autoapi_cols__", {})
        in_fields = {
            name
            for name, spec in specs.items()
            if alias in set(getattr(getattr(spec, "io", None), "in_verbs", []) or [])
        }
        out_fields = {
            name
            for name, spec in specs.items()
            if alias in set(getattr(getattr(spec, "io", None), "out_verbs", []) or [])
        }
        result["in_"] = (
            _build_schema(model, verb=alias, include=in_fields) if in_fields else None
        )
        result["out"] = (
            _build_schema(model, verb=alias, include=out_fields) if out_fields else None
        )

    else:
        # Defensive default: treat unknown like custom (raw)
        result["in_"] = None
        result["out"] = None

    return result
