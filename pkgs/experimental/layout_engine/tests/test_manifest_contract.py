from __future__ import annotations

from layout_engine import (
    AtomRegistry,
    AtomSpec,
    LayoutCompiler,
    ManifestBuilder,
    TileSpec,
    Viewport,
    validate_manifest,
)
from layout_engine.core.size import Size
from layout_engine.grid.spec import GridSpec, GridTrack, GridTile
from layout_engine.manifest.spec import ChannelManifest, WsRouteManifest
from layout_engine.site.spec import PageSpec, SiteSpec, SlotSpec


def test_manifest_with_site_and_channels_validates() -> None:
    builder = ManifestBuilder()
    site = SiteSpec(
        base_path="/app",
        pages=(
            PageSpec(
                id="dashboard",
                route="/",
                title="Dashboard",
                slots=(SlotSpec(name="main", role="layout"),),
            ),
        ),
    )

    view_model = {
        "viewport": {"width": 1280, "height": 720},
        "grid": {"columns": []},
        "tiles": [],
    }

    manifest = builder.build(
        view_model,
        site=site,
        active_page="dashboard",
        channels=[
            ChannelManifest(id="ui.events", scope="page", topic="page:{page_id}:ui")
        ],
        ws_routes=[WsRouteManifest(path="/ws/ui", channels=("ui.events",))],
    )

    validate_manifest(manifest)
    assert manifest.channels[0].id == "ui.events"
    assert manifest.ws_routes[0].channels == ("ui.events",)


def test_swarma_catalog_override_propagates_to_manifest() -> None:
    # Build registry with an override without depending on layout_engine_atoms availability.
    registry = AtomRegistry()
    registry.register(
        AtomSpec(
            role="swarmakit:vue:button",
            module="@swarmakit/vue",
            export="Button",
            version="0.0.22",
            defaults={},
        )
    )
    registry.override("swarmakit:vue:button", defaults={"size": "lg"})

    compiler = LayoutCompiler()
    grid_spec = GridSpec(columns=[GridTrack(size=Size(1, "fr"))], row_height=200)
    viewport = Viewport(width=800, height=600)
    frames_map = compiler.frames(
        grid_spec, viewport, [GridTile(tile_id="btn", col=0, row=0)]
    )
    tiles = [TileSpec(id="btn", role="swarmakit:vue:button", props={})]

    view_model = compiler.view_model(
        grid_spec,
        viewport,
        frames_map,
        tiles,
        atoms_registry=registry,
    )

    manifest = ManifestBuilder().build(view_model)
    tile = manifest.tiles[0]
    assert tile["props"]["size"] == "lg"
    assert tile["atom"]["defaults"]["size"] == "lg"
