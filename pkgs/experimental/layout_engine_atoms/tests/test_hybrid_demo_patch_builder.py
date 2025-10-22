from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path


def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


_HYBRID_DEMO_DIR = Path(__file__).resolve().parents[1] / "examples" / "hybrid_demo"
_manifest_mod = _load_module("hybrid_demo_manifest", _HYBRID_DEMO_DIR / "manifest.py")
_patches_mod = _load_module("hybrid_demo_patches", _HYBRID_DEMO_DIR / "patches.py")

SEED_INCIDENTS = _manifest_mod.SEED_INCIDENTS
create_mpa_manifest = _manifest_mod.create_mpa_manifest
create_spa_manifest = _manifest_mod.create_spa_manifest
MpaPatchBuilder = _patches_mod.MpaPatchBuilder
PatchBuilder = _patches_mod.PatchBuilder


def test_mpa_patch_builder_retains_overview_page_order():
    builder = MpaPatchBuilder(create_mpa_manifest)
    rows = deepcopy(SEED_INCIDENTS)
    patch = builder.build_patch(rows)

    assert "pages" in patch
    page_ids = [page.get("id") for page in patch["pages"]]
    assert page_ids[0] == "overview"
    assert "incidents" in page_ids

    incidents_page = next(
        page for page in patch["pages"] if page.get("id") == "incidents"
    )
    table = next(
        tile
        for tile in incidents_page.get("tiles", [])
        if tile.get("id") == "tile_incidents"
    )
    assert table["props"]["rows"][0]["account"] == rows[0]["account"]


def test_spa_patch_preserves_tile_layout():
    builder = PatchBuilder(create_spa_manifest)
    rows = deepcopy(SEED_INCIDENTS)
    patch = builder.build_patch(rows)

    original_tiles = create_spa_manifest()["tiles"]
    assert len(patch["tiles"]) == len(original_tiles)
    incident_tile = next(
        tile for tile in patch["tiles"] if tile.get("id") == "tile_incidents"
    )
    assert incident_tile["props"]["rows"][0]["account"] == rows[0]["account"]
    hero_tile = next(tile for tile in patch["tiles"] if tile.get("id") == "tile_hero")
    assert hero_tile["props"]["body"].startswith("### Activation")
