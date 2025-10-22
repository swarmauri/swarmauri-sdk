"""Manifests for the hybrid demo: SPA and MPA variants."""

from __future__ import annotations

from datetime import datetime, timedelta
from random import Random
from typing import Any, Iterable, Mapping

from layout_engine import (
    SizeToken,
    TileSpec,
    Viewport,
    block,
    col,
    compute_etag,
    quick_manifest_from_table,
    quick_view_model_from_table,
    row,
    table,
    to_plain_dict,
)
from layout_engine_atoms import build_default_registry


SEED_INCIDENTS: list[dict[str, str]] = [
    {
        "account": "Aurora Analytics",
        "owner": "Lopez",
        "status": "Mitigated by automation",
        "updated": "2 min ago",
    },
    {
        "account": "Nimbus Retail",
        "owner": "Singh",
        "status": "Waiting for customer reply",
        "updated": "7 min ago",
    },
    {
        "account": "Atlas Manufacturing",
        "owner": "Fernandez",
        "status": "Investigating alerts",
        "updated": "12 min ago",
    },
]


def _trend_points(seed: int, count: int = 12) -> Iterable[dict[str, float | str]]:
    rng = Random(seed)
    base = datetime.now() - timedelta(weeks=count - 1)
    value = rng.uniform(70, 92)
    for idx in range(count):
        value += rng.uniform(-2.5, 3.5)
        yield {
            "x": (base + timedelta(weeks=idx)).strftime("%Y-%m-%d"),
            "y": round(max(value, 40), 1),
        }


def create_spa_manifest() -> Mapping[str, Any]:
    """Single-page manifest highlighting realtime incidents."""

    registry = build_default_registry()
    layout = table(
        row(
            col(block("tile_hero"), size=SizeToken.l),
            col(block("tile_arr"), size=SizeToken.s),
        ),
        row(
            col(block("tile_health"), size=SizeToken.s),
            col(block("tile_activation"), size=SizeToken.s),
            col(block("tile_conversion"), size=SizeToken.s),
        ),
        row(col(block("tile_trend"), size=SizeToken.xl)),
        row(col(block("tile_incidents"), size=SizeToken.xl)),
    )

    tiles = [
        TileSpec(
            id="tile_hero",
            role="viz:panel:markdown",
            props={
                "title": "Operations Overview",
                "body": (
                    "### Activation remains on track\n"
                    "Monitor activation velocity, ARR expansion, and live incidents from a single surface."
                ),
            },
        ),
        TileSpec(
            id="tile_arr",
            role="viz:metric:kpi",
            props={
                "label": "Expansion ARR",
                "value": 2_450_000,
                "delta": 0.12,
                "format": "currency_compact",
                "period": "Quarter to date",
            },
        ),
        TileSpec(
            id="tile_health",
            role="viz:metric:kpi",
            props={
                "label": "Customer Health",
                "value": 0.87,
                "delta": 0.04,
                "period": "30 day trend",
            },
        ),
        TileSpec(
            id="tile_activation",
            role="viz:metric:kpi",
            props={
                "label": "Activation Velocity",
                "value": 14,
                "delta": -0.9,
                "period": "Avg. days to activate",
            },
        ),
        TileSpec(
            id="tile_conversion",
            role="viz:metric:kpi",
            props={
                "label": "Conversion",
                "value": 0.42,
                "delta": 0.06,
                "period": "Quarter to date",
            },
        ),
        TileSpec(
            id="tile_trend",
            role="viz:timeseries:line",
            props={
                "label": "Activation Velocity (days)",
                "series": [
                    {
                        "label": "Actual",
                        "points": list(_trend_points(seed=2024, count=10)),
                    },
                    {
                        "label": "Target",
                        "points": list(_trend_points(seed=3000, count=10)),
                    },
                ],
            },
        ),
        TileSpec(
            id="tile_incidents",
            role="viz:table:basic",
            props={
                "label": "Live Incident Stream",
                "columns": [
                    {"key": "account", "name": "Account"},
                    {"key": "owner", "name": "Owner"},
                    {"key": "status", "name": "Status"},
                    {"key": "updated", "name": "Updated"},
                ],
                "rows": list(SEED_INCIDENTS),
            },
        ),
    ]

    manifest = quick_manifest_from_table(
        layout,
        Viewport(width=1280, height=960),
        tiles,
        atoms_registry=registry,
        version="spa.2025.06",
    )

    payload = to_plain_dict(manifest)
    payload["theme"] = {
        "tokens": {
            "color-surface": "#060b1a",
            "color-accent": "#5ab1ff",
        }
    }

    payload_without_etag = dict(payload)
    payload_without_etag.pop("etag", None)
    payload["etag"] = compute_etag(payload_without_etag)
    return payload


def create_mpa_manifest() -> Mapping[str, Any]:
    """Multi-page manifest (Overview + Incidents workspace)."""

    registry = build_default_registry()

    overview_layout = table(
        row(
            col(block("tile_overview_hero"), size=SizeToken.l),
            col(block("tile_navigate"), size=SizeToken.s),
        ),
        row(
            col(block("tile_health"), size=SizeToken.s),
            col(block("tile_arr"), size=SizeToken.s),
            col(block("tile_advocates"), size=SizeToken.s),
        ),
        row(col(block("tile_segments"), size=SizeToken.xl)),
    )

    incidents_layout = table(
        row(col(block("tile_back"), size=SizeToken.s)),
        row(col(block("tile_incidents"), size=SizeToken.xl)),
    )

    overview_tiles = [
        TileSpec(
            id="tile_overview_hero",
            role="viz:panel:markdown",
            props={
                "title": "Customer Success Overview",
                "body": (
                    "Track activation health across cohorts. Switch to incidents to monitor open escalations."
                ),
            },
        ),
        TileSpec(
            id="tile_navigate",
            role="ui:button:primary",
            props={
                "label": "View Incidents",
                "caption": "Open the incident response workspace",
                "targetPage": "incidents",
            },
        ),
        TileSpec(
            id="tile_health",
            role="viz:metric:kpi",
            props={
                "label": "Global Health",
                "value": 0.86,
                "delta": 0.05,
                "period": "Rolling 30 days",
            },
        ),
        TileSpec(
            id="tile_arr",
            role="viz:metric:kpi",
            props={
                "label": "Expansion ARR",
                "value": 2_980_000,
                "delta": 0.08,
                "format": "currency_compact",
            },
        ),
        TileSpec(
            id="tile_advocates",
            role="viz:metric:kpi",
            props={
                "label": "Active Advocates",
                "value": 72,
                "delta": 0.11,
                "period": "Quarter to date",
            },
        ),
        TileSpec(
            id="tile_segments",
            role="viz:bar:horizontal",
            props={
                "label": "Segment Health",
                "series": [
                    {"label": "Enterprise", "value": 92, "annotation": "Top 10%"},
                    {"label": "Growth", "value": 84, "annotation": "Improving"},
                    {"label": "SMB", "value": 76},
                ],
            },
        ),
    ]

    incidents_tiles = [
        TileSpec(
            id="tile_back",
            role="ui:button:secondary",
            props={
                "label": "Back to Overview",
                "caption": "Return to KPIs",
                "targetPage": "overview",
            },
        ),
        TileSpec(
            id="tile_incidents",
            role="viz:table:basic",
            props={
                "label": "Live Incident Stream",
                "columns": [
                    {"key": "account", "name": "Account"},
                    {"key": "owner", "name": "Owner"},
                    {"key": "status", "name": "Status"},
                    {"key": "updated", "name": "Updated"},
                ],
                "rows": list(SEED_INCIDENTS),
            },
        ),
    ]

    overview_vm = quick_view_model_from_table(
        overview_layout,
        Viewport(width=1280, height=900),
        overview_tiles,
        atoms_registry=registry,
    )
    incidents_vm = quick_view_model_from_table(
        incidents_layout,
        Viewport(width=1280, height=900),
        incidents_tiles,
        atoms_registry=registry,
    )

    manifest = quick_manifest_from_table(
        overview_layout,
        Viewport(width=1280, height=900),
        overview_tiles,
        atoms_registry=registry,
        version="mpa.2025.06",
    )
    payload = to_plain_dict(manifest)
    payload["pages"] = [
        {
            "id": "overview",
            "label": "Overview",
            "grid": dict(overview_vm["grid"]),
            "viewport": dict(overview_vm["viewport"]),
            "tiles": list(overview_vm["tiles"]),
        },
        {
            "id": "incidents",
            "label": "Incidents",
            "grid": dict(incidents_vm["grid"]),
            "viewport": dict(incidents_vm["viewport"]),
            "tiles": list(incidents_vm["tiles"]),
        },
    ]

    payload_without_etag = dict(payload)
    payload_without_etag.pop("etag", None)
    payload["etag"] = compute_etag(payload_without_etag)
    return payload


__all__ = [
    "SEED_INCIDENTS",
    "create_spa_manifest",
    "create_mpa_manifest",
]
