from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Callable

from layout_engine import Manifest, Viewport, compute_etag
from layout_engine.manifest.utils import from_dict, to_dict
from layout_engine.site.spec import PageSpec, SiteSpec
from layout_engine.structure import block, col, row, table
from layout_engine.core import SizeToken
from layout_engine_atoms.manifest import (
    Tile,
    build_manifest_from_table,
    create_registry,
    tile,
)

ROW_HEIGHT = 200
VIEWPORT = Viewport(width=1280, height=860)
VERSION = "2025.10"

CARD_STYLE = {
    "backgroundColor": "rgba(15, 23, 42, 0.82)",
    "border": "1px solid rgba(148, 163, 184, 0.22)",
    "borderRadius": "20px",
    "padding": "24px",
    "boxShadow": "0 18px 44px rgba(2, 6, 23, 0.6)",
}


@dataclass(frozen=True)
class PageDefinition:
    id: str
    title: str
    route: str
    description: str
    builder: Callable[[], tuple]


def _overview_page() -> tuple:
    layout = table(
        row(
            col(block("overview_hero"), size=SizeToken.xl),
            col(block("overview_pulse")),
        ),
        row(
            col(block("overview_metrics"), size=SizeToken.xl),
        ),
        gap_x=24,
        gap_y=24,
    )
    tiles: list[Tile] = [
        tile(
            "overview_hero",
            "swarmakit:svelte:cardbased-list",
            props={
                "style": CARD_STYLE,
                "cards": [
                    {
                        "title": "Svelte Runtime",
                        "description": "Layout engine demo powered by mount_svelte_app.",
                    },
                    {
                        "title": "Realtime events",
                        "description": "Hero pulse updates via websocket.",
                    },
                ],
            },
        ),
        tile(
            "overview_pulse",
            "swarmakit:svelte:activity-indicators",
            props={
                "type": "info",
                "message": "Waiting for realtime event…",
                "style": CARD_STYLE,
            },
        ),
        tile(
            "overview_metrics",
            "swarmakit:svelte:data-summary",
            props={
                "data": [12, 15, 22, 35, 44, 57, 68, 74],
                "style": CARD_STYLE,
            },
        ),
    ]
    return layout, tiles


PAGE_SEQUENCE: tuple[PageDefinition, ...] = (
    PageDefinition(
        id="overview",
        title="Svelte Overview",
        route="/",
        description="Svelte runtime sample dashboard with realtime bindings.",
        builder=_overview_page,
    ),
)

PAGES = {page.id: page for page in PAGE_SEQUENCE}
DEFAULT_PAGE_ID = PAGE_SEQUENCE[0].id

SITE_SPEC = SiteSpec(
    base_path="/",
    pages=tuple(
        PageSpec(id=page.id, route=page.route, title=page.title)
        for page in PAGE_SEQUENCE
    ),
)


@lru_cache(maxsize=1)
def get_registry():
    widget_overrides = {
        "swarmakit:svelte:cardbased-list": {
            "module": "@layout-engine/svelte-widgets",
            "export": "CardbasedList",
            "defaults": {},
        },
        "swarmakit:svelte:activity-indicators": {
            "module": "@layout-engine/svelte-widgets",
            "export": "ActivityIndicators",
            "defaults": {},
        },
        "swarmakit:svelte:data-summary": {
            "module": "@layout-engine/svelte-widgets",
            "export": "DataSummary",
            "defaults": {},
        },
    }
    return create_registry(catalog="svelte", overrides=widget_overrides)


def build_manifest(page_id: str) -> Manifest:
    try:
        page = PAGES[page_id]
    except KeyError as exc:
        raise KeyError(f"Unknown demo page '{page_id}'") from exc

    layout, tiles = page.builder()
    manifest, _ = build_manifest_from_table(
        layout,
        tiles,
        registry=get_registry(),
        row_height=ROW_HEIGHT,
        viewport=VIEWPORT,
        version=VERSION,
    )

    manifest_dict = to_dict(manifest)
    manifest_dict["site"] = {
        "active_page": page.id,
        "pages": [
            {"id": spec.id, "route": spec.route, "title": spec.title}
            for spec in SITE_SPEC.pages
        ],
        "navigation": {"base_path": SITE_SPEC.base_path},
    }
    meta = dict(manifest_dict.get("meta", {}))
    meta["page"] = {
        "id": page.id,
        "title": page.title,
        "description": page.description,
    }
    manifest_dict["meta"] = meta
    manifest_dict["etag"] = compute_etag(manifest_dict)

    hydrated = from_dict(manifest_dict)
    return hydrated
