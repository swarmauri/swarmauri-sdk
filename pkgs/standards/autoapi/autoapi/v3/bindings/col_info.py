# autoapi/v3/bindings/col_info.py
"""
Compat shim: bindings-level access to Column.info["autoapi"] utilities.
Prefer importing from `autoapi.v3.schema.col_info`, but this keeps older code working.

This will be fully deprecated in place of ColumnSpecs.
"""

from __future__ import annotations
import logging

import warnings

from ..schema.col_info import (
    VALID_KEYS,
    VALID_VERBS,
    WRITE_VERBS,
    normalize,
    check,
    should_include_in_input,
    should_include_in_output,
)

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/col_info")

warnings.warn(
    "autoapi.v3.bindings.col_info is deprecated; Column.info['autoapi'] will be removed. "
    "Use ColumnSpecs instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "VALID_KEYS",
    "VALID_VERBS",
    "WRITE_VERBS",
    "normalize",
    "check",
    "should_include_in_input",
    "should_include_in_output",
]
