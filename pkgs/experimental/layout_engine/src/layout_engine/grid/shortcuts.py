from __future__ import annotations
from typing import Iterable

from .default import Grid
from .spec import GridSpec, GridTrack, GridTile
from ..core.size import Size, SizeToken, tokens_to_fr_sizes


def tracks_fr(fr_values: Iterable[float], *, min_px: int = 200) -> list[GridTrack]:
    return [GridTrack(Size(float(v), unit="fr", min_px=min_px)) for v in fr_values]


def tracks_px(px_values: Iterable[float]) -> list[GridTrack]:
    return [GridTrack(Size(float(v), unit="px")) for v in px_values]


def tracks_pct(percent_values: Iterable[float], *, min_px: int = 0) -> list[GridTrack]:
    return [GridTrack(Size(float(v), unit="%", min_px=min_px)) for v in percent_values]


def make_gridspec(
    fr_values: list[float], *, row_height: int = 180, gap_x: int = 12, gap_y: int = 12
) -> GridSpec:
    columns = tracks_fr(fr_values)
    return GridSpec(columns=columns, row_height=row_height, gap_x=gap_x, gap_y=gap_y)


def make_gridspec_from_tokens(
    tokens: list[SizeToken],
    *,
    row_height: int = 180,
    gap_x: int = 12,
    gap_y: int = 12,
    min_px: int = 200,
) -> GridSpec:
    sizes = tokens_to_fr_sizes(tokens, min_px=min_px)
    columns = [GridTrack(s) for s in sizes]
    return GridSpec(columns=columns, row_height=row_height, gap_x=gap_x, gap_y=gap_y)


def gridspec_from_tokens(tokens: list[SizeToken], **kwargs) -> GridSpec:
    """Backward compatible alias for :func:`make_gridspec_from_tokens`."""
    return make_gridspec_from_tokens(tokens, **kwargs)


def breakpoint(max_width: int, columns: list[GridTrack]) -> tuple[int, list[GridTrack]]:
    """Helper to define a breakpoint entry."""
    return (max_width, columns)


def breakpoints(
    *entries: tuple[int, list[GridTrack]],
) -> list[tuple[int, list[GridTrack]]]:
    """Collect breakpoint tuples into a list."""
    return list(entries)


def place(
    tile_id: str, col: int, row: int, *, col_span: int = 1, row_span: int = 1
) -> GridTile:
    return GridTile(tile_id, col, row, col_span, row_span)


def define_gridspec(
    *,
    columns: list[GridTrack] | None = None,
    row_height: int = 180,
    gap_x: int = 12,
    gap_y: int = 12,
    breakpoints=None,
) -> GridSpec:
    return GridSpec(
        columns=columns or [],
        row_height=row_height,
        gap_x=gap_x,
        gap_y=gap_y,
        breakpoints=breakpoints or (),
    )


def derive_gridspec(base: GridSpec, **overrides) -> GridSpec:
    return GridSpec(
        columns=overrides.get("columns", base.columns),
        row_height=overrides.get("row_height", base.row_height),
        gap_x=overrides.get("gap_x", base.gap_x),
        gap_y=overrides.get("gap_y", base.gap_y),
        breakpoints=overrides.get("breakpoints", base.breakpoints),
    )


def make_grid(spec: GridSpec) -> Grid:
    return Grid(spec=spec)
