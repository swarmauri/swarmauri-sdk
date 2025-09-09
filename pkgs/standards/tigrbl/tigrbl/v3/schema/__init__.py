# tigrbl/v3/schema/__init__.py
from .builder import _build_schema, _build_list_params
from .utils import (
    namely_model,
    _make_bulk_rows_model,
    _make_bulk_rows_response_model,
    _make_bulk_ids_model,
    _make_deleted_response_model,
    _make_pk_model,
)
from .get_schema import get_schema
from .decorators import schema_ctx
from .collect import collect_decorated_schemas
from ._schema import Schema
from .schema_spec import SchemaSpec
from .shortcuts import schema, schema_spec
from .types import SchemaRef, SchemaArg, SchemaKind

__all__ = [
    "_build_schema",
    "_build_list_params",
    "namely_model",
    "_make_bulk_rows_model",
    "_make_bulk_rows_response_model",
    "_make_bulk_ids_model",
    "_make_deleted_response_model",
    "_make_pk_model",
    "get_schema",
    "schema_ctx",
    "collect_decorated_schemas",
    "Schema",
    "SchemaSpec",
    "schema",
    "schema_spec",
    "SchemaRef",
    "SchemaArg",
    "SchemaKind",
]
