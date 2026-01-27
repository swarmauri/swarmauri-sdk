from __future__ import annotations

from typing import Any

from ..core.tokens import DEFAULT_BASELINE_MULTIPLIER
from ..grid.spec import GridSpec


def _spacing_scale(baseline: int) -> dict[str, int]:
    half = max(2, baseline // 2)
    quarter = max(1, baseline // 4)
    return {
        "xxs": quarter,
        "xs": max(2, (baseline * 3) // 8),
        "sm": half,
        "md": baseline,
        "lg": int(baseline * 1.5),
        "xl": baseline * 2,
    }


def layout_tokens_from_grid(spec: GridSpec) -> dict[str, Any]:
    """Derive layout tokens and SwarmaKit-friendly layout props from a grid spec."""

    baseline = (
        int(spec.baseline_unit)
        if spec.baseline_unit is not None
        else max(4, spec.row_height // DEFAULT_BASELINE_MULTIPLIER)
    )
    gap_x = int(spec.gap_x)
    gap_y = int(spec.gap_y)

    layout_meta = {
        "baseline": baseline,
        "gap": {"x": gap_x, "y": gap_y},
        "columns": len(spec.columns),
        "spacing_scale": _spacing_scale(baseline),
    }

    padding_x = max(4, gap_x // 2)
    padding_y = max(4, gap_y // 2)

    # SwarmaKit atoms expect a `layout` block describing spacing rhythm.
    swarma_layout = {
        "layout": {
            "padding": {"x": padding_x, "y": padding_y},
            "gap": {"x": gap_x, "y": gap_y},
            "baseline": baseline,
            "spacing": _spacing_scale(baseline),
        }
    }

    return {"meta": layout_meta, "swarma_props": swarma_layout}
