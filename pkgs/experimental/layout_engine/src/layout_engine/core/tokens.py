from __future__ import annotations

from typing import Any, Mapping, Sequence

from .size import Size, SizeToken, tokens_to_fr_sizes

DEFAULT_BASELINE_MULTIPLIER = 8


def _clone_sizes(sizes: Sequence[Size]) -> list[Size]:
    return [
        Size(value=size.value, unit=size.unit, min_px=size.min_px, max_px=size.max_px)
        for size in sizes
    ]


SWISS_GRID_COLUMNS: dict[str, tuple[Size, ...]] = {
    "sgd:columns:12": tuple(tokens_to_fr_sizes([SizeToken.s] * 12, min_px=64)),
    "sgd:columns:8": tuple(tokens_to_fr_sizes([SizeToken.m] * 8, min_px=72)),
    "sgd:columns:6": tuple(tokens_to_fr_sizes([SizeToken.m] * 6, min_px=88)),
    "sgd:columns:4": tuple(tokens_to_fr_sizes([SizeToken.l] * 4, min_px=120)),
}

SWISS_GRID_GUTTERS: dict[str, dict[str, int]] = {
    "sgd:gutter:tight": {"gap_x": 16, "gap_y": 16},
    "sgd:gutter:standard": {"gap_x": 24, "gap_y": 24},
    "sgd:gutter:generous": {"gap_x": 32, "gap_y": 28},
}

SWISS_BASELINE_UNITS: dict[str, int] = {
    "sgd:baseline:8": 8,
    "sgd:baseline:10": 10,
    "sgd:baseline:12": 12,
}


def resolve_grid_tokens(tokens: Mapping[str, str]) -> dict[str, Any]:
    """Materialize Swiss-grid token selections into concrete numeric values."""

    resolved: dict[str, Any] = {"tokens": dict(tokens)}

    column_key = tokens.get("columns")
    if column_key:
        try:
            template = SWISS_GRID_COLUMNS[column_key]
        except KeyError as exc:
            raise KeyError(f"Unknown column token '{column_key}'") from exc
        resolved["columns"] = _clone_sizes(template)

    gutter_key = tokens.get("gutter")
    if gutter_key:
        try:
            gutter = SWISS_GRID_GUTTERS[gutter_key]
        except KeyError as exc:
            raise KeyError(f"Unknown gutter token '{gutter_key}'") from exc
        resolved.update(gutter)

    baseline_key = tokens.get("baseline")
    if baseline_key:
        try:
            baseline_px = SWISS_BASELINE_UNITS[baseline_key]
        except KeyError as exc:
            raise KeyError(f"Unknown baseline token '{baseline_key}'") from exc
        resolved["baseline_unit"] = baseline_px
        resolved["row_height"] = baseline_px * DEFAULT_BASELINE_MULTIPLIER

    return resolved
