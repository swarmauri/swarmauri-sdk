from layout_engine import AtomRegistry

from layout_engine_atoms import (
    DEFAULT_ATOMS,
    DEFAULT_PRESETS,
    AtomPreset,
    build_default_registry,
)


def test_default_presets_are_registered() -> None:
    assert DEFAULT_PRESETS, "expected non-empty preset catalog"
    assert "ui:button:primary" in DEFAULT_PRESETS
    assert isinstance(DEFAULT_PRESETS["ui:button:primary"], AtomPreset)


def test_default_atoms_match_presets() -> None:
    assert set(DEFAULT_ATOMS) == set(DEFAULT_PRESETS)
    spec = DEFAULT_ATOMS["viz:metric:kpi"]
    assert spec.module == "@swarmauri/atoms/Metrics"
    assert spec.export == "KpiCard"


def test_build_default_registry() -> None:
    registry = build_default_registry()
    assert isinstance(registry, AtomRegistry)
    spec = registry.get("viz:metric:kpi")
    assert spec.defaults["format"] == "compact"

    merged = registry.resolve_props("input:date-range", {"presets": ["today"]})
    assert merged["presets"] == ["today"]
    assert "presets" in merged
