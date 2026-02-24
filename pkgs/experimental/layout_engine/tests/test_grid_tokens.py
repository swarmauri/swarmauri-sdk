from __future__ import annotations

from layout_engine.core import (
    DEFAULT_BASELINE_MULTIPLIER,
    SWISS_BASELINE_UNITS,
    resolve_grid_tokens,
)
from layout_engine.grid import GridSpec, gridspec_to_dict, gridspec_from_dict


def test_resolve_grid_tokens_materializes_sizes() -> None:
    tokens = {
        "columns": "sgd:columns:12",
        "gutter": "sgd:gutter:standard",
        "baseline": "sgd:baseline:8",
    }
    resolved = resolve_grid_tokens(tokens)

    assert len(resolved["columns"]) == 12
    assert resolved["gap_x"] == 24
    assert resolved["gap_y"] == 24
    assert resolved["baseline_unit"] == SWISS_BASELINE_UNITS["sgd:baseline:8"]
    assert (
        resolved["row_height"]
        == SWISS_BASELINE_UNITS["sgd:baseline:8"] * DEFAULT_BASELINE_MULTIPLIER
    )


def test_grid_spec_from_tokens_roundtrip() -> None:
    tokens = {
        "columns": "sgd:columns:8",
        "gutter": "sgd:gutter:tight",
        "baseline": "sgd:baseline:10",
    }

    spec = GridSpec.from_tokens(tokens)

    assert spec.tokens == tokens
    assert spec.baseline_unit == SWISS_BASELINE_UNITS["sgd:baseline:10"]
    assert len(spec.columns) == 8

    payload = gridspec_to_dict(spec)
    assert payload["tokens"] == tokens
    assert payload["baseline_unit"] == SWISS_BASELINE_UNITS["sgd:baseline:10"]

    restored = gridspec_from_dict(payload)
    assert restored.tokens == tokens
    assert restored.baseline_unit == SWISS_BASELINE_UNITS["sgd:baseline:10"]
    assert len(restored.columns) == 8
