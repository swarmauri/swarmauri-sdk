from __future__ import annotations

from pydantic import BaseModel

from ..core.size import Size


class GridTrack(BaseModel):
    """A single grid column track with a Size (px|%|fr)."""

    size: Size


class GridSpec(BaseModel):
    """Explicit grid container description.

    - columns: list of GridTrack defining the column sizing scheme
    - row_height: height of one row unit in pixels
    - gap_x/gap_y: inter-column and inter-row gaps in pixels
    - breakpoints: optional list of (max_width_px, columns_for_that_break)
      The first entry whose max_width >= viewport.width wins.
    """

    columns: list[GridTrack]
    row_height: int = 180
    gap_x: int = 12
    gap_y: int = 12
    breakpoints: list[tuple[int, list[GridTrack]]] = ()


class GridTile(BaseModel):
    """A tile placement within the grid." """

    tile_id: str
    col: int
    row: int
    col_span: int = 1
    row_span: int = 1
