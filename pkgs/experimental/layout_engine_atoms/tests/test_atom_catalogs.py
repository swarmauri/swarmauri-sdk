from __future__ import annotations

import pytest
from layout_engine import AtomSpec

from layout_engine_atoms.default import AtomPresetCatalog
from layout_engine_atoms.spec import AtomPreset
from layout_engine_atoms.swarma import AtomProps, SwarmaAtomCatalog


def make_preset(
    role: str,
    *,
    module: str = "pkg",
    export: str = "Component",
    version: str = "1.0.0",
    defaults: dict[str, object] | None = None,
) -> AtomPreset:
    return AtomPreset(
        role=role,
        module=module,
        export=export,
        version=version,
        defaults=defaults or {},
    )


def make_spec(
    role: str, *, module: str = "pkg", export: str = "Component", version: str = "1.0.0"
) -> AtomSpec:
    return AtomSpec(
        role=role,
        module=module,
        export=export,
        version=version,
        defaults={"foo": "bar"},
    )


def test_atom_preset_catalog_from_specs_and_registry_roundtrip() -> None:
    specs = [
        AtomSpec(
            role="test:a",
            module="pkg",
            export="Alpha",
            version="1.0",
            defaults={"flag": True},
        ),
        AtomSpec(
            role="test:b",
            module="pkg",
            export="Beta",
            version="1.1",
            defaults={"count": 3},
        ),
    ]

    catalog = AtomPresetCatalog.from_specs(specs)

    assert sorted(p.role for p in catalog.presets()) == ["test:a", "test:b"]
    as_specs = catalog.as_specs()
    assert set(as_specs) == {"test:a", "test:b"}
    assert as_specs["test:a"].export == "Alpha"

    registry = catalog.build_registry()
    stored = registry.get("test:b")
    assert stored.export == "Beta"
    assert stored.defaults["count"] == 3


def test_atom_preset_catalog_get_unknown_role_raises() -> None:
    catalog = AtomPresetCatalog({"test:a": make_preset("test:a")})

    with pytest.raises(KeyError):
        catalog.get("missing")


class ButtonProps(AtomProps):
    size: str = "md"
    tone: str | None = None


def test_swarma_atom_catalog_merge_props_and_get_spec() -> None:
    preset = make_preset("swarmakit:vue:button", defaults={"tone": "primary"})
    catalog = SwarmaAtomCatalog([preset], props_schema=ButtonProps)

    spec = catalog.get_spec("swarmakit:vue:button")
    assert spec.module == "pkg"

    merged = catalog.merge_props("swarmakit:vue:button", {"size": "lg"})
    assert merged == {"size": "lg", "tone": "primary"}


def test_swarma_atom_catalog_with_overrides_returns_new_instance() -> None:
    preset = make_preset("swarmakit:vue:badge", defaults={"tone": "info"})
    catalog = SwarmaAtomCatalog([preset], props_schema=ButtonProps)

    updated = catalog.with_overrides("swarmakit:vue:badge", defaults={"tone": "warn"})

    assert updated is not catalog
    assert updated.merge_props("swarmakit:vue:badge")["tone"] == "warn"
    assert catalog.merge_props("swarmakit:vue:badge")["tone"] == "info"


def test_swarma_atom_catalog_with_extra_presets_accepts_specs() -> None:
    preset = make_preset("swarmakit:vue:badge")
    extra_spec = make_spec("swarmakit:vue:chip", module="pkg2")

    catalog = SwarmaAtomCatalog([preset], props_schema=ButtonProps)
    extended = catalog.with_extra_presets({"alias": extra_spec})

    assert "swarmakit:vue:badge" in extended.as_specs()
    assert "swarmakit:vue:chip" in extended.as_specs()
    assert extended.get_spec("swarmakit:vue:chip").module == "pkg2"


def test_swarma_atom_catalog_with_overrides_unknown_role() -> None:
    catalog = SwarmaAtomCatalog([make_preset("swarmakit:vue:button")])
    with pytest.raises(KeyError):
        catalog.with_overrides("swarmakit:vue:missing", defaults={})


def test_swarma_atom_catalog_rejects_invalid_payload() -> None:
    catalog = SwarmaAtomCatalog([make_preset("swarmakit:vue:button")])

    with pytest.raises(TypeError):
        catalog.with_extra_presets({"bad": object()})  # type: ignore[arg-type]
