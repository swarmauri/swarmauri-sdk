from __future__ import annotations

from layout_engine.structure import block, col, row, table

from layout_engine_atoms.manifest import (
    create_registry,
    quick_manifest,
    quick_manifest_from_table,
    tile,
)


def test_quick_manifest_builds_manifest() -> None:
    registry = create_registry()

    manifest = quick_manifest(
        [
            tile("hero", "swarmakit:vue:cardbased-list", span="full", props={"cards": []}),
            tile("summary", "swarmakit:vue:data-summary", span="half", props={"data": [1, 2, 3]}),
            tile("activity", "swarmakit:vue:activity-indicators", span="half", props={"type": "success"}),
        ],
        registry=registry,
        columns=2,
    )

    assert manifest.kind == "layout_manifest"
    ids = [t["id"] if isinstance(t, dict) else t.id for t in manifest.tiles]
    assert ids == ["hero", "summary", "activity"]


def test_quick_manifest_from_table_builds_manifest() -> None:
    registry = create_registry()

    layout = table(
        row(col(block("hero")), col(block("activity"))),
        row(col(block("summary")), col(block("extra"))),
    )

    manifest = quick_manifest_from_table(
        layout,
        [
            tile("hero", "swarmakit:vue:cardbased-list"),
            tile("summary", "swarmakit:vue:data-summary"),
            tile("activity", "swarmakit:vue:activity-indicators"),
            tile("extra", "swarmakit:vue:progress-bar"),
        ],
        registry=registry,
    )

    assert manifest.kind == "layout_manifest"
    ids = [t["id"] if isinstance(t, dict) else t.id for t in manifest.tiles]
    assert set(ids) == {"hero", "summary", "activity", "extra"}
