# autoapi/v3/bindings/builder.py
"""
Compat shim: bindings-level access to schema builder helpers.
Prefer importing from `autoapi.v3.schema`, but this keeps older code working.
"""
from __future__ import annotations

from ..schema import _build_schema, _build_list_params

__all__ = ["_build_schema", "_build_list_params"]
