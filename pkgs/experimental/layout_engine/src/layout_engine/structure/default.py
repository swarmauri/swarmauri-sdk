from __future__ import annotations
from typing import List
from .base import IGridBuilder
from .spec import Table, Row, Block
from ..core.viewport import Viewport
from ..core.size import Size, DEFAULT_TOKEN_WEIGHTS
from ..grid.spec import GridSpec, GridTrack, GridTile


class GridBuilder(IGridBuilder):
    """Deterministic compiler from authoring DSL → explicit grid.

    Rules:
      - The number of **grid columns** equals the max column count across rows.
      - The **column weights** are taken from the first row that has that max column count.
        (A simple and deterministic policy that's easy to reason about.)
      - Each row's columns are mapped proportionally into the canonical max column count.
      - Blocks stack top-to-bottom inside each column. Each block's `row_span` is additive.
      - The row's effective height (in logical rows) is:
            max(Row.height_rows, max_stacked_row_span_across_columns)
    """

    def __init__(self, row_height: int = 180, min_track_px: int = 200):
        self.row_height = row_height
        self.min_track_px = min_track_px

    # --- public API ---
    def to_grid(self, t: Table, vp: Viewport) -> tuple[GridSpec, list[GridTile]]:
        max_cols = max((len(r.columns) for r in t.rows), default=0)
        if max_cols == 0:
            return GridSpec(columns=[]), []

        # choose the first row that has max_cols as the reference for weights
        ref_row = next(r for r in t.rows if len(r.columns) == max_cols)
        weights = [DEFAULT_TOKEN_WEIGHTS[c.size] for c in ref_row.columns]
        total = sum(weights) or 1.0
        tracks = [
            GridTrack(size=Size(value=w / total, unit="fr", min_px=self.min_track_px))
            for w in weights
        ]
        gs = GridSpec(
            columns=tracks, row_height=self.row_height, gap_x=t.gap_x, gap_y=t.gap_y
        )

        # placements
        placements: List[GridTile] = []
        seen_ids: set[str] = set()
        cur_grid_row = 0

        for r in t.rows:
            # map this row's columns into the canonical max_cols
            col_map = self._column_map(r, max_cols)
            base_floor = max(1, r.height_rows)
            tallest = 0

            for idx, col in enumerate(r.columns):
                start_col, span_cols = col_map[idx]
                # stack blocks within this (start_col .. span)
                local_rows_used = 0
                for blk in col.blocks:
                    self._validate_block(blk, seen_ids)
                    # effective spans
                    eff_col_span = max(1, span_cols * max(1, blk.col_span))
                    eff_row_span = max(1, blk.row_span)
                    placements.append(
                        GridTile(
                            tile_id=blk.tile_id,
                            col=start_col,
                            row=cur_grid_row + local_rows_used,
                            col_span=eff_col_span,
                            row_span=eff_row_span,
                        )
                    )
                    local_rows_used += eff_row_span
                tallest = max(tallest, local_rows_used)

            cur_grid_row += max(base_floor, tallest)

        return gs, placements

    # --- internals ---
    def _column_map(self, r: Row, max_cols: int) -> list[tuple[int, int]]:
        """Map the row's columns to starting index + span so that total == max_cols.

        The distribution is proportional to the row's SizeToken weights; rounding is corrected
        by distributing the drift ±1 across columns from left to right.
        """
        n = len(r.columns)
        if n <= 0:
            return []
        if n == max_cols:
            return [(i, 1) for i in range(n)]

        weights = [DEFAULT_TOKEN_WEIGHTS[c.size] for c in r.columns]
        s = sum(weights) or 1.0
        raw = [w / s * max_cols for w in weights]
        spans = [max(1, round(x)) for x in raw]

        drift = max_cols - sum(spans)
        i = 0
        while drift != 0 and spans:
            step = 1 if drift > 0 else -1
            j = i % len(spans)
            spans[j] = max(1, spans[j] + step)
            drift -= step
            i += 1

        starts = []
        run = 0
        for sp in spans:
            starts.append(run)
            run += sp
        return list(zip(starts, spans))

    @staticmethod
    def _validate_block(blk: Block, seen: set[str]) -> None:
        if not blk.tile_id:
            raise ValueError("Block.tile_id must be non-empty")
        if blk.tile_id in seen:
            raise ValueError(f"Duplicate tile_id in structure: {blk.tile_id}")
        seen.add(blk.tile_id)


def validate_table(table: Table) -> Table:
    """Basic validation for authoring tables."""
    seen: set[str] = set()
    for row in table.rows:
        if not row.columns:
            raise ValueError("Each row must contain at least one column")
        for col in row.columns:
            for block in col.blocks:
                if not block.tile_id:
                    raise ValueError("Each block must have a tile_id")
                if block.tile_id in seen:
                    raise ValueError(f"Duplicate tile_id '{block.tile_id}' detected")
                seen.add(block.tile_id)
    return table
