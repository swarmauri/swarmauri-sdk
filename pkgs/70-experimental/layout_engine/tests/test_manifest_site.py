from __future__ import annotations

from layout_engine.events import clear_channels, get_channel
from layout_engine.manifest.default import ManifestBuilder
from layout_engine.manifest.utils import to_dict
from layout_engine.manifest.spec import ChannelManifest, WsRouteManifest
from layout_engine.site.spec import PageSpec, SiteSpec, SlotSpec


def test_manifest_builder_merges_site_metadata() -> None:
    builder = ManifestBuilder()
    site = SiteSpec(
        base_path="/app",
        pages=(
            PageSpec(
                id="home",
                route="/",
                title="Home",
                slots=(SlotSpec(name="main", role="layout"),),
            ),
            PageSpec(
                id="reports",
                route="/reports/:id",
                title="Reports",
                slots=(SlotSpec(name="main", role="layout"),),
            ),
        ),
    )

    manifest = builder.build(
        {
            "viewport": {"width": 1280, "height": 720},
            "grid": {"columns": []},
            "tiles": [],
        },
        site=site,
        active_page="home",
    )

    assert manifest.site is not None
    assert manifest.site.active_page == "home"
    assert len(manifest.site.pages) == 2
    home = manifest.site.pages[0]
    assert home["id"] == "home"
    assert home["route"] == "/"

    # Ensure serialization retains site payload
    serialized = to_dict(manifest)
    assert "site" in serialized
    assert serialized["site"]["navigation"]["base_path"] == "/app"


def test_manifest_builder_registers_channels_and_routes() -> None:
    clear_channels()
    builder = ManifestBuilder()
    channel = ChannelManifest(
        id="ui.events",
        scope="page",
        topic="page:{page_id}:ui",
    )
    route = WsRouteManifest(path="/ws/ui", channels=("ui.events",))

    manifest = builder.build(
        {
            "viewport": {"width": 640, "height": 480},
            "grid": {"columns": []},
            "tiles": [],
        },
        channels=[channel],
        ws_routes=[route],
    )

    assert manifest.channels[0].id == "ui.events"
    assert manifest.ws_routes[0].path == "/ws/ui"
    serialized = to_dict(manifest)
    assert serialized["channels"][0]["topic"] == "page:{page_id}:ui"
    assert tuple(serialized["ws_routes"][0]["channels"]) == ("ui.events",)
    channel_def = get_channel("ui.events")
    assert channel_def is not None
    assert channel_def["topic"] == "page:{page_id}:ui"
    clear_channels()
