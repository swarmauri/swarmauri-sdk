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
    assert "swarmakit:vue:button" in DEFAULT_PRESETS
    button_preset = DEFAULT_PRESETS["swarmakit:vue:button"]
    assert isinstance(button_preset, AtomPreset)
    assert button_preset.module == "@swarmakit/vue"


def test_default_atoms_match_presets() -> None:
    assert set(DEFAULT_ATOMS) == set(DEFAULT_PRESETS)
    spec = DEFAULT_ATOMS["swarmakit:vue:button"]
    assert spec.module == "@swarmakit/vue"
    assert spec.export == "Button"


def test_build_default_registry() -> None:
    registry = build_default_registry()
    assert isinstance(registry, AtomRegistry)
    spec = registry.get("swarmakit:vue:button")
    assert spec.module == "@swarmakit/vue"

    merged = registry.resolve_props("swarmakit:vue:button", {"size": "lg"})
    assert merged["size"] == "lg"


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
