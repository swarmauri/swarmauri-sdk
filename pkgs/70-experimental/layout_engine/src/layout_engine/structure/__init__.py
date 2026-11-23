"""Structure authoring DSL for layout tables."""

from __future__ import annotations

from .spec import Block, Column, Row, Table
from .base import IGridBuilder
from .default import GridBuilder, validate_table
from .shortcuts import (
    block,
    col,
    row,
    table,
    stack,
    hstack,
    build_grid,
    gridify,
)
from .decorators import table_ctx, table_defaults, derive_policy

__all__ = [
    "Block",
    "Column",
    "Row",
    "Table",
    "IGridBuilder",
    "GridBuilder",
    "validate_table",
    "block",
    "col",
    "row",
    "table",
    "stack",
    "hstack",
    "build_grid",
    "gridify",
    "table_ctx",
    "table_defaults",
    "derive_policy",
]
