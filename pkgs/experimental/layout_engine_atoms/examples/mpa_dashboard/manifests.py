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


# --- Demo configuration -------------------------------------------------------------------------

ROW_HEIGHT = 220
VIEWPORT = Viewport(width=1440, height=960)
VERSION = "2025.10"

PANEL_STYLE = {
    "backgroundColor": "rgba(15, 23, 42, 0.82)",
    "border": "1px solid rgba(148, 163, 184, 0.22)",
    "boxShadow": "0 18px 44px rgba(2, 6, 23, 0.6)",
    "borderRadius": "18px",
    "padding": "24px",
}

CARD_STYLE = {
    **PANEL_STYLE,
    "--card-bg": "rgba(15, 23, 42, 0.82)",
    "--card-border": "1px solid rgba(148, 163, 184, 0.3)",
    "--card-hover-bg": "rgba(56, 189, 248, 0.16)",
    "--card-selected-border-color": "#38bdf8",
    "padding": "24px",
    "height": "50%",
}

SUMMARY_STYLE = {
    **PANEL_STYLE,
    "backgroundColor": "rgba(56, 189, 248, 0.14)",
    "border": "1px solid rgba(56, 189, 248, 0.35)",
    "--summary-bg": "rgba(15, 118, 110, 0.12)",
    "--summary-border-color": "rgba(21, 94, 117, 0.45)",
}

ACTION_STYLE = {
    **PANEL_STYLE,
    "background": "radial-gradient(circle at 20% 20%, rgba(56,189,248,0.28), rgba(15,23,42,0.92))",
}


@dataclass(frozen=True)
class PageDefinition:
    """Declarative description of a demo page."""

    id: str
    title: str
    route: str
    tagline: str
    description: str
    builder: Callable[[], tuple]


# --- Page builders -------------------------------------------------------------------------------


def _overview_page() -> tuple:
    layout = table(
        row(col(block("overview_hero"), size=SizeToken.xxl)),
        row(
            col(
                block("overview_actions"),
                block("overview_pulses"),
                size=SizeToken.m,
            ),
            col(block("overview_metrics"), size=SizeToken.m),
            col(
                block("overview_progress"),
                size=SizeToken.xl,
            ),
        ),
        row(col(block("overview_timeline"), size=SizeToken.xxl)),
        gap_x=24,
        gap_y=6,
    )

    tiles: list[Tile] = [
        tile(
            "overview_hero",
            "swarmakit:vue:cardbased-list",
            props={
                "style": CARD_STYLE,
                "cards": [
                    {
                        "title": "Autonomous services",
                        "description": "27 providers are synced; 94% SLA adherence in the last 24h.",
                    },
                    {
                        "title": "Signals this hour",
                        "description": "3.1k realtime events processed with 0.2s median latency.",
                    },
                    {
                        "title": "Experiments live",
                        "description": "Nine experiments running across ops, growth, and market loops.",
                    },
                ],
            },
        ),
        tile(
            "overview_actions",
            "swarmakit:vue:actionable-list",
            props={
                "items": [
                    {"label": "Review API catalogue drift", "actionLabel": "Inspect"},
                    {
                        "label": "Enable adaptive throttling",
                        "actionLabel": "Activate",
                        "loading": False,
                    },
                    {
                        "label": "Archive legacy widget set",
                        "actionLabel": "Archive",
                        "disabled": True,
                    },
                ],
                "style": ACTION_STYLE,
            },
        ),
        tile(
            "overview_pulses",
            "swarmakit:vue:activity-indicators",
            props={
                "type": "success",
                "message": "All cores synchronized — next ingest checkpoint in 12 minutes.",
                "style": {
                    "backgroundColor": "rgba(56, 189, 248, 0.16)",
                    "color": "#e0f2fe",
                    "border": "1px solid rgba(56, 189, 248, 0.45)",
                    "borderRadius": "18px",
                    "padding": "20px 24px",
                    "--success-bg-color": "rgba(56, 189, 248, 0.18)",
                    "--success-text-color": "#e0f2fe",
                },
            },
        ),
        tile(
            "overview_metrics",
            "swarmakit:vue:data-summary",
            props={
                "data": [112, 126, 131, 148, 162, 176, 183, 195],
                "style": SUMMARY_STYLE,
            },
        ),
        tile(
            "overview_progress",
            "swarmakit:vue:progress-bar",
            props={
                "progress": 72,
                "style": {
                    "background": "rgba(56, 189, 248, 0.18)",
                    "borderRadius": "14px",
                    "padding": "18px 20px",
                    "boxShadow": "0 18px 44px rgba(2, 6, 23, 0.55)",
                    "border": "1px solid rgba(56, 189, 248, 0.45)",
                    "margin": "0 auto",
                    "maxWidth": "320px",
                },
            },
        ),
        tile(
            "overview_timeline",
            "swarmakit:vue:timeline-list",
            props={
                "items": [
                    {
                        "id": "1",
                        "label": "✅ Platform deploy 09:10 UTC",
                        "completed": True,
                    },
                    {
                        "id": "2",
                        "label": "✅ Ops swarm retro 11:30 UTC",
                        "completed": True,
                    },
                    {
                        "id": "3",
                        "label": "• Partner sync-in 14:00 UTC",
                        "completed": False,
                    },
                    {
                        "id": "4",
                        "label": "• Pulse export 18:45 UTC",
                        "completed": False,
                    },
                ],
                "style": PANEL_STYLE,
            },
        ),
    ]

    return layout, tiles


def _operations_page() -> tuple:
    layout = table(
        row(
            col(block("operations_overview", row_span=2), size=SizeToken.xxl),
            col(
                block("operations_alerts"),
                size=SizeToken.l,
            ),
            col(block("operations_uptime")),
        ),
        row(
            col(block("operations_queue_depth"), size=SizeToken.s),
            col(block("operations_tasks"), size=SizeToken.s),
        ),
        gap_x=24,
        gap_y=24,
    )

    tiles: list[Tile] = [
        tile(
            "operations_overview",
            "swarmakit:vue:cardbased-list",
            props={
                "style": CARD_STYLE,
                "cards": [
                    {
                        "title": "Incidents",
                        "description": "0 active · 4 resolved in the last shift window.",
                    },
                    {
                        "title": "Escalations",
                        "description": "3 teams on standby · pager latency 41s median.",
                    },
                    {
                        "title": "Workflow health",
                        "description": "Auto-remediation closed 67% of triggered runbooks.",
                    },
                ],
            },
        ),
        tile(
            "operations_alerts",
            "swarmakit:vue:actionable-list",
            props={
                "items": [
                    {"label": "Rebalance build runners", "actionLabel": "Run"},
                    {"label": "Approve router firmware", "actionLabel": "Review"},
                    {
                        "label": "Mute noisy insight feed",
                        "actionLabel": "Pause",
                        "loading": True,
                    },
                ],
                "style": ACTION_STYLE,
            },
        ),
        tile(
            "operations_uptime",
            "swarmakit:vue:progress-circle",
            props={
                "progress": 80,
                "status": "active",
                "style": {
                    "padding": "32px",
                    "background": "rgba(15, 118, 110, 0.18)",
                    "borderRadius": "20px",
                    "border": "1px solid rgba(45, 212, 191, 0.45)",
                    "display": "grid",
                    "placeItems": "center",
                    "color": "#ccfbf1",
                    "gap": "12px",
                },
            },
        ),
        tile(
            "operations_queue_depth",
            "swarmakit:vue:data-summary",
            props={
                "data": [42, 33, 24, 19, 21, 22, 18, 15],
                "style": SUMMARY_STYLE,
            },
        ),
        tile(
            "operations_tasks",
            "swarmakit:vue:selectable-list-with-item-details",
            props={
                "items": [
                    {
                        "id": "A-104",
                        "label": "Validate drift reports",
                        "details": "Ensure new connectors conform to baseline schema.",
                    },
                    {
                        "id": "A-221",
                        "label": "Rotate ephemeral keys",
                        "details": "Applies to fleet staging and XFN sandboxes.",
                    },
                    {
                        "id": "A-310",
                        "label": "Sync playbook analytics",
                        "details": "Share trendline with reliability guild.",
                    },
                ],
                "style": PANEL_STYLE,
            },
        ),
    ]

    return layout, tiles


def _revenue_page() -> tuple:
    layout = table(
        row(
            col(block("revenue_highlights", row_span=2), size=SizeToken.l),
            col(
                block("revenue_health"),
                size=SizeToken.m,
            ),
        ),
        row(
            col(block("revenue_forecast"), size=SizeToken.m),
            col(block("revenue_actions"), size=SizeToken.m),
            col(block("revenue_wins"), size=SizeToken.m)
        ),
        gap_x=24,
        gap_y=24,
    )

    tiles: list[Tile] = [
        tile(
            "revenue_highlights",
            "swarmakit:vue:cardbased-list",
            props={
                "style": CARD_STYLE,
                "cards": [
                    {
                        "title": "Quarter bookings",
                        "description": "$48.2M recognised · tracking +12% above target.",
                    },
                    {
                        "title": "Expansion velocity",
                        "description": "Net retention 134% · 27 expansions closed this month.",
                    },
                    {
                        "title": "Enterprise pilots",
                        "description": "Five Fortune 100 pilots active · two in procurement review.",
                    },
                ],
            },
        ),
        tile(
            "revenue_health",
            "swarmakit:vue:progress-bar",
            props={
                "progress": 84,
                "style": {
                    "background": "rgba(56, 189, 248, 0.18)",
                    "padding": "18px",
                    "borderRadius": "16px",
                    "boxShadow": "0 18px 44px rgba(2, 6, 23, 0.55)",
                    "border": "1px solid rgba(56, 189, 248, 0.45)",
                    "margin": "0 auto",
                    "maxWidth": "320px",
                },
            },
        ),
        tile(
            "revenue_wins",
            "swarmakit:vue:timeline-list",
            props={
                "items": [
                    {
                        "id": "deal-1",
                        "label": "Arcadia Labs · ARR $1.2M",
                        "completed": True,
                    },
                    {
                        "id": "deal-2",
                        "label": "Northwind AI · ARR $880k",
                        "completed": True,
                    },
                    {
                        "id": "deal-3",
                        "label": "Globex Cloud · ARR $1.9M",
                        "completed": False,
                    },
                    {
                        "id": "deal-4",
                        "label": "Zeno Systems · ARR $620k",
                        "completed": False,
                    },
                ],
                "style": PANEL_STYLE,
            },
        ),
        tile(
            "revenue_forecast",
            "swarmakit:vue:data-summary",
            props={
                "data": [5.1, 6.3, 6.9, 7.8, 8.5, 9.4, 10.2, 10.8],
                "style": SUMMARY_STYLE,
            },
        ),
        tile(
            "revenue_actions",
            "swarmakit:vue:actionable-list",
            props={
                "items": [
                    {"label": "Launch lifecycle nurture", "actionLabel": "Send"},
                    {"label": "Prep executive QBR deck", "actionLabel": "Draft"},
                    {
                        "label": "Prioritise CS follow-ups",
                        "actionLabel": "Review",
                        "loading": True,
                    },
                ],
                "style": ACTION_STYLE,
            },
        ),
    ]

    return layout, tiles


PAGE_SEQUENCE: tuple[PageDefinition, ...] = (
    PageDefinition(
        id="overview",
        title="Executive pulse",
        route="/",
        tagline="Strategic signals, live impact",
        description="An executive overview combining live telemetry, team focus, and forward-looking signals.",
        builder=_overview_page,
    ),
    PageDefinition(
        id="operations",
        title="Operations watch",
        route="/operations",
        tagline="Reliability command surface",
        description="Deep dive into reliability workflows, shift posture, and automation throughput.",
        builder=_operations_page,
    ),
    PageDefinition(
        id="revenue",
        title="Revenue intelligence",
        route="/revenue",
        tagline="Momentum with leading indicators",
        description="Commercial momentum tracking bookings, expansion efficiency, and deal choreography.",
        builder=_revenue_page,
    ),
)

PAGES: dict[str, PageDefinition] = {page.id: page for page in PAGE_SEQUENCE}

SITE_SPEC = SiteSpec(
    base_path="/",
    pages=tuple(
        PageSpec(
            id=page.id,
            route=page.route,
            title=page.title,
            meta={"tagline": page.tagline},
        )
        for page in PAGE_SEQUENCE
    ),
)

DEFAULT_PAGE_ID = PAGE_SEQUENCE[0].id


# --- Registry helpers ----------------------------------------------------------------------------


def _apply_atom_metadata(manifest: Manifest, registry) -> None:
    tiles = manifest.tiles if isinstance(manifest.tiles, list) else list(manifest.tiles)
    for tile in tiles:
        if not isinstance(tile, dict):
            continue
        try:
            spec = registry.get(tile["role"])
        except Exception:  # noqa: BLE001
            continue
        atom_data = dict(tile.get("atom") or {})
        atom_data.setdefault("role", spec.role)
        atom_data.setdefault("module", spec.module)
        atom_data.setdefault("export", spec.export)
        atom_data.setdefault("version", spec.version)
        if spec.defaults and not atom_data.get("defaults"):
            atom_data["defaults"] = dict(spec.defaults)
        if getattr(spec, "family", None) and not atom_data.get("family"):
            atom_data["family"] = spec.family
        if getattr(spec, "framework", None) and not atom_data.get("framework"):
            atom_data["framework"] = spec.framework
        if getattr(spec, "package", None) and not atom_data.get("package"):
            atom_data["package"] = spec.package
        tokens = getattr(spec, "tokens", None)
        if tokens and not atom_data.get("tokens"):
            atom_data["tokens"] = dict(tokens)
        registry_meta = getattr(spec, "registry", None)
        if registry_meta and not atom_data.get("registry"):
            atom_data["registry"] = dict(registry_meta)
        tile["atom"] = atom_data


def _ensure_viewport_bounds(payload: dict[str, object]) -> None:
    viewport = payload.setdefault("viewport", {})
    if not isinstance(viewport, dict):
        return
    tiles = payload.get("tiles")
    if not isinstance(tiles, list):
        return
    max_bottom = 0
    for entry in tiles:
        if not isinstance(entry, dict):
            continue
        frame = entry.get("frame")
        if not isinstance(frame, dict):
            continue
        bottom = int(frame.get("y", 0)) + int(frame.get("h", 0))
        if bottom > max_bottom:
            max_bottom = bottom
    current = int(viewport.get("height", 0))
    if max_bottom > current:
        viewport["height"] = max_bottom


@lru_cache(maxsize=1)
def get_registry():
    registry = create_registry(catalog="vue")
    return registry


# --- Manifest plumbing ---------------------------------------------------------------------------


def _site_payload(active_page: str) -> dict[str, object]:
    return {
        "pages": [
            {
                "id": spec.id,
                "route": spec.route,
                "title": spec.title,
                "slots": [slot.model_dump() for slot in spec.slots],
                "meta": dict(spec.meta),
            }
            for spec in SITE_SPEC.pages
        ],
        "active_page": active_page,
        "navigation": {"base_path": SITE_SPEC.base_path},
    }


def build_manifest(page_id: str) -> Manifest:
    """Return a manifest for the requested page id with site metadata attached."""

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
    manifest_dict["site"] = _site_payload(page.id)

    meta = dict(manifest_dict.get("meta", {}))
    meta["page"] = {
        "id": page.id,
        "title": page.title,
        "description": page.description,
        "tagline": page.tagline,
    }
    meta.setdefault("theme", {}).update(
        {
            "accent": "#38bdf8",
            "panel": "rgba(15, 23, 42, 0.85)",
            "surface": "#020617",
        }
    )
    manifest_dict["meta"] = meta
    _ensure_viewport_bounds(manifest_dict)
    manifest_dict["etag"] = compute_etag(manifest_dict)

    hydrated = from_dict(manifest_dict)
    _apply_atom_metadata(hydrated, get_registry())
    return hydrated


# --- Page utilities -------------------------------------------------------------------------------


def available_pages() -> tuple[PageDefinition, ...]:
    """Return the ordered tuple of available demo pages."""

    return PAGE_SEQUENCE


def resolve_page_by_route(route: str) -> str | None:
    """Return the page id for a route if known."""

    normalized = route or "/"
    for page in PAGE_SEQUENCE:
        if page.route == normalized:
            return page.id
    return None
