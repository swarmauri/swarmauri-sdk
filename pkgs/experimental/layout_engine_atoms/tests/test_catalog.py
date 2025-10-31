from layout_engine import AtomRegistry

from layout_engine_atoms import (
    DEFAULT_ATOMS,
    DEFAULT_PRESETS,
    AtomPreset,
    build_default_registry,
)
from layout_engine_atoms.catalog import swarma_svelte, swarma_vue


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


def test_swarma_vue_presets_cover_swarmakit_components() -> None:
    assert len(swarma_vue.DEFAULT_PRESETS) == 157
    assert "swarmakit:vue:button" in swarma_vue.DEFAULT_PRESETS
    registry = swarma_vue.build_registry()
    assert isinstance(registry, AtomRegistry)
    button_spec = registry.get("swarmakit:vue:button")
    assert button_spec.module == "@swarmakit/vue"


def test_swarma_svelte_presets_cover_swarmakit_components() -> None:
    assert len(swarma_svelte.DEFAULT_PRESETS) == 71
    assert "swarmakit:svelte:button" in swarma_svelte.DEFAULT_PRESETS
    registry = swarma_svelte.build_registry()
    assert isinstance(registry, AtomRegistry)
    button_spec = registry.get("swarmakit:svelte:button")
    assert button_spec.module == "@swarmakit/svelte"
