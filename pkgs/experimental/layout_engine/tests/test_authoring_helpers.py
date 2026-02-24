from __future__ import annotations

import importlib

from layout_engine.authoring import build_site_manifest, grid_token_snapshot
from layout_engine.authoring.helpers import register_swarma_atoms
from layout_engine.atoms import AtomRegistry
from layout_engine.core.size import Size
from layout_engine.grid.spec import GridSpec, GridTrack
from layout_engine.site.spec import PageSpec, SiteSpec, SlotSpec


def test_grid_token_snapshot() -> None:
    spec = GridSpec(
        columns=[GridTrack(size=Size(1, "fr"))],
        gap_x=24,
        gap_y=16,
        baseline_unit=12,
        tokens={"columns": "sgd:columns:4"},
    )
    snapshot = grid_token_snapshot(spec)
    assert snapshot["tokens"]["columns"] == "sgd:columns:4"
    assert snapshot["baseline_unit"] == 12
    assert snapshot["columns"] == 1


def test_build_site_manifest_compiles_pages(monkeypatch) -> None:
    site = SiteSpec(
        base_path="/",
        pages=(
            PageSpec(
                id="home",
                route="/",
                title="Home",
                slots=(SlotSpec(name="main", role="layout"),),
            ),
        ),
    )

    def compiler() -> dict[str, object]:
        return {
            "viewport": {"width": 800, "height": 600},
            "grid": {"columns": []},
            "tiles": [],
        }

    result = build_site_manifest(site, {"home": compiler})
    assert "home" in result
    manifest = result["home"]
    assert manifest.site is not None
    assert manifest.site.pages[0]["id"] == "home"


def test_register_swarma_atoms_optional(monkeypatch) -> None:
    registry = AtomRegistry()

    class DummyCatalog:
        def __init__(self):
            self._presets = []

        def presets(self):
            return []

        def get(self, role):
            raise KeyError(role)

    class DummyModule:
        @staticmethod
        def build_catalog(name):
            return DummyCatalog()

    module_stub = DummyModule()

    def fake_import(name):
        if name == "layout_engine_atoms.catalog":
            return module_stub
        raise ImportError(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    registry = register_swarma_atoms(registry, catalog="vue")
    assert isinstance(registry, AtomRegistry)
