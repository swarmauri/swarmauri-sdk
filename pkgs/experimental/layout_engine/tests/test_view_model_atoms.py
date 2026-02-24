from __future__ import annotations

from layout_engine.atoms.default import AtomRegistry
from layout_engine.atoms.spec import AtomSpec
from layout_engine.compile import LayoutCompiler
from layout_engine.core.size import Size
from layout_engine.core.viewport import Viewport
from layout_engine.grid.spec import GridSpec, GridTrack, GridTile
from layout_engine.tiles.spec import TileSpec


def test_view_model_includes_atom_metadata() -> None:
    compiler = LayoutCompiler()
    registry = AtomRegistry()
    registry.register(
        AtomSpec(
            role="swarmakit:vue:button",
            module="@swarmakit/vue",
            export="Button",
            version="0.0.22",
            defaults={"size": "md"},
            framework="vue",
            package="@swarmakit/vue",
            family="swarmakit",
            registry={"name": "swarmakit", "version": "0.0.22", "framework": "vue"},
        )
    )
    registry.revision = "rev-1"  # type: ignore[attr-defined]

    grid_spec = GridSpec(
        columns=[GridTrack(size=Size(1, "fr"))],
        row_height=200,
        gap_x=24,
        gap_y=16,
        tokens={"columns": "sgd:columns:8"},
    )
    placements = [GridTile(tile_id="btn", col=0, row=0)]
    frames = compiler.frames(grid_spec, Viewport(width=800, height=600), placements)

    tiles = [TileSpec(id="btn", role="swarmakit:vue:button", props={"tone": "primary"})]

    vm = compiler.view_model(
        grid_spec,
        Viewport(width=800, height=600),
        frames,
        tiles,
        atoms_registry=registry,
        channels=[{"id": "ui.events", "scope": "page", "topic": "page:{page_id}:ui"}],
        ws_routes=[{"path": "/ws/ui", "channels": ("ui.events",)}],
    )

    atom_payload = vm["tiles"][0]["atom"]
    assert atom_payload["role"] == "swarmakit:vue:button"
    assert atom_payload["framework"] == "vue"
    assert atom_payload["registry"]["name"] == "swarmakit"
    assert atom_payload["registry"]["version"] == "0.0.22"
    assert vm["meta"]["grid_tokens"]["columns"] == "sgd:columns:8"
    assert vm["meta"]["atoms"]["revision"] == "rev-1"
    assert vm["meta"]["layout"]["gap"]["x"] == 24
    layout_props = vm["tiles"][0]["props"]["layout"]
    assert layout_props["gap"]["x"] == 24
    assert layout_props["padding"]["x"] == 12
    assert vm["channels"][0]["id"] == "ui.events"
