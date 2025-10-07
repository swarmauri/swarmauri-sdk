from __future__ import annotations
from .spec import Block, Column, Row, Table
from ..core.size import SizeToken
from ..core.viewport import Viewport
from ..grid.spec import GridSpec, GridTile
from .default import GridBuilder

# ---- atomic constructors ----


def block(tile_id: str, *, col_span: int = 1, row_span: int = 1) -> Block:
    """Create a Block (atomic tile placeholder)."""
    return Block(tile_id=tile_id, col_span=col_span, row_span=row_span)


def col(*blocks: Block, size: SizeToken = SizeToken.m) -> Column:
    """Create a Column with a size token and a sequence of blocks."""
    return Column(size=size, blocks=tuple(blocks))


def row(*columns: Column, height_rows: int = 1) -> Row:
    """Create a Row from columns, with an optional row-height floor in logical units."""
    return Row(columns=tuple(columns), height_rows=height_rows)


def table(*rows: Row, gap_x: int = 12, gap_y: int = 12) -> Table:
    """Create a Table with gaps between columns and rows (in pixels)."""
    return Table(rows=tuple(rows), gap_x=gap_x, gap_y=gap_y)


# ---- higher-level helpers ----


def stack(*blocks: Block, size: SizeToken = SizeToken.m, height_rows: int = 1) -> Row:
    """Create a single-column row with blocks stacked vertically."""
    return row(col(*blocks, size=size), height_rows=height_rows)


def hstack(*blocks: Block, size: SizeToken = SizeToken.m, height_rows: int = 1) -> Row:
    """Create a row placing each block into its own column (uniform size)."""
    columns = tuple(col(b, size=size) for b in blocks)
    return row(*columns, height_rows=height_rows)


def build_grid(
    tbl: Table, vp: Viewport, *, row_height: int = 180, min_track_px: int = 200
) -> tuple[GridSpec, list[GridTile]]:
    """Compile the authoring Table into a GridSpec + placements using GridBuilder."""
    return GridBuilder(row_height=row_height, min_track_px=min_track_px).to_grid(
        tbl, vp
    )


def gridify(
    tbl: Table, vp: Viewport, *, row_height: int = 180, min_track_px: int = 200
) -> tuple[GridSpec, list[GridTile]]:
    """Alias for :func:`build_grid` maintained for compatibility."""
    return build_grid(tbl, vp, row_height=row_height, min_track_px=min_track_px)
