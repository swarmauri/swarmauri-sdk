from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
from ..core.size import SizeToken

@dataclass(frozen=True)
class Block:
    """Atomic content unit to be placed in a column.

    - tile_id: unique identifier of the tile to render
    - col_span / row_span: logical spans within the derived grid
    """
    tile_id: str
    col_span: int = 1
    row_span: int = 1

@dataclass(frozen=True)
class Column:
    """Column within a Row with a semantic size token (xxs..xxl)."""
    size: SizeToken
    blocks: Tuple[Block, ...] = ()

    def is_empty(self) -> bool:
        return len(self.blocks) == 0

@dataclass(frozen=True)
class Row:
    """Row contains one or more Columns.

    - height_rows: minimal row-span the row should occupy (used as a floor
      when no blocks force a taller span).
    """
    columns: Tuple[Column, ...]
    height_rows: int = 1

    def column_count(self) -> int:
        return len(self.columns)

@dataclass(frozen=True)
class Table:
    """High-level authoring artifact composed of Rows → Columns → Blocks.

    The GridBuilder compiles this into an explicit GridSpec + GridTile placements.
    """
    rows: Tuple[Row, ...]
    gap_x: int = 12
    gap_y: int = 12

    def is_empty(self) -> bool:
        return len(self.rows) == 0
