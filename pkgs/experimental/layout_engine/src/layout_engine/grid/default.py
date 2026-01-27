from __future__ import annotations
from typing import List
from .base import IGridResolver
from .spec import GridSpec, GridTile, GridTrack
from ..core.viewport import Viewport
from ..core.frame import Frame
from ..core.size import resolve_column_widths


class ExplicitGridResolver(IGridResolver):
    """Deterministic resolver for explicit grids.

    Features:
      - px/%/fr support with min/max clamps per track
      - horizontal gaps, row height, vertical gaps
      - breakpoints: choose alternative columns when viewport.width <= max_width
      - strict placement validation (column bounds and spans)

    Algorithm:
      1) Choose track list by breakpoint (if any).
      2) Resolve pixel widths via `resolve_column_widths`.
      3) Compute column x-offsets.
      4) For each GridTile, create a Frame; validate bounds.
    """

    def frames(
        self, spec: GridSpec, vp: Viewport, tiles: list[GridTile]
    ) -> dict[str, Frame]:
        cols = self._columns_for_viewport(spec, vp)
        n = len(cols)
        if n == 0:
            return {}

        widths = resolve_column_widths([c.size for c in cols], vp.width, spec.gap_x)
        xoffs = self._x_offsets(widths, spec.gap_x)

        frames: dict[str, Frame] = {}
        for gt in tiles:
            if gt.col < 0 or gt.col >= n:
                raise ValueError(
                    f"tile '{gt.tile_id}' col out of range: {gt.col} in [0,{n - 1}]"
                )
            if gt.col_span < 1 or gt.col + gt.col_span > n:
                raise ValueError(
                    f"tile '{gt.tile_id}' col_span invalid: start={gt.col} span={gt.col_span} with {n} columns"
                )
            if gt.row < 0 or gt.row_span < 1:
                raise ValueError(
                    f"tile '{gt.tile_id}' row/row_span invalid: row={gt.row} row_span={gt.row_span}"
                )

            x = xoffs[gt.col]
            w = sum(widths[gt.col : gt.col + gt.col_span]) + spec.gap_x * (
                gt.col_span - 1
            )
            y = gt.row * (spec.row_height + spec.gap_y)
            h = gt.row_span * spec.row_height + spec.gap_y * (gt.row_span - 1)
            frames[gt.tile_id] = Frame(x=x, y=y, w=w, h=h)

        return frames

    # ------------- helpers -------------
    @staticmethod
    def _x_offsets(widths: List[int], gap: int) -> List[int]:
        xoffs: List[int] = []
        run = 0
        for i, w in enumerate(widths):
            xoffs.append(run)
            run += w + (gap if i < len(widths) - 1 else 0)
        return xoffs

    @staticmethod
    def _columns_for_viewport(spec: GridSpec, vp: Viewport) -> List[GridTrack]:
        if not spec.breakpoints:
            return spec.columns
        # choose first whose max_width >= vp.width
        for max_w, cols in sorted(spec.breakpoints, key=lambda x: x[0]):
            if vp.width <= max_w:
                return cols
        return spec.columns


class Grid:
    """Default grid runtime wrapper that pairs a GridSpec with a resolver."""

    def __init__(self, spec: GridSpec, resolver: IGridResolver | None = None):
        self.spec = spec
        self.resolver = resolver or ExplicitGridResolver()

    def frames(self, vp: Viewport, placements: list[GridTile]) -> dict[str, Frame]:
        return self.resolver.frames(self.spec, vp, placements)

    # --- context manager support ---
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False
