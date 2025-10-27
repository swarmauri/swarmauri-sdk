"""Build the manifest used by the Svelte runtime example."""

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
    quick_manifest_from_table,
    row,
    table,
    to_plain_dict,
)


def _kpi(tile_id: str, label: str, value: float, delta: float) -> TileSpec:
    return TileSpec(
        id=tile_id,
        role="viz:metric:kpi",
        props={
            "label": label,
            "value": value,
            "delta": delta,
            "period": "Last 30 days",
        },
    )


def _series(seed: int, count: int = 8) -> Iterable[dict[str, float | str]]:
    rng = Random(seed)
    base = datetime.now() - timedelta(days=(count - 1) * 7)
    value = rng.uniform(8, 12)
    for idx in range(count):
        value += rng.uniform(-0.3, 0.6)
        yield {
            "x": (base + timedelta(days=idx * 7)).strftime("%Y-%m-%d"),
            "y": round(max(value, 0), 2),
        }


def create_manifest() -> Mapping[str, Any]:
    layout = table(
        row(
            col(block("tile_net_new"), size=SizeToken.m),
            col(block("tile_logo_retention"), size=SizeToken.m),
            col(block("tile_pipeline_velocity"), size=SizeToken.m),
        ),
        row(
            col(block("tile_notes"), size=SizeToken.l),
            col(block("tile_segments"), size=SizeToken.s),
        ),
        row(col(block("tile_revenue_trend"), size=SizeToken.xl)),
        row(
            col(block("tile_incidents"), size=SizeToken.l),
            col(block("tile_nav_command_center"), size=SizeToken.s),
        ),
    )

    tiles: list[TileSpec] = [
        _kpi("tile_net_new", "Net New ARR", 1_480_000, 0.14),
        _kpi("tile_logo_retention", "Logo Retention", 0.934, 0.02),
        _kpi("tile_pipeline_velocity", "Pipeline Velocity", 2.8, -0.04),
        TileSpec(
            id="tile_notes",
            role="viz:panel:markdown",
            props={
                "title": "Weekly Focus",
                "body": (
                    "### Action Items\n"
                    "- Finalise Q3 forecast adjustments\n"
                    "- Close the Acme renewal blocker\n"
                    "- Monitor trial conversion cohort anomaly\n"
                ),
            },
        ),
        TileSpec(
            id="tile_segments",
            role="viz:bar:horizontal",
            props={
                "label": "Segment Performance",
                "series": [
                    {"label": "Enterprise", "value": 68, "annotation": "↑ 6 pts"},
                    {"label": "Mid-market", "value": 54, "annotation": "↑ 2 pts"},
                    {"label": "SMB", "value": 41, "annotation": "↓ 3 pts"},
                ],
            },
        ),
        TileSpec(
            id="tile_revenue_trend",
            role="viz:timeseries:line",
            props={
                "label": "Revenue Trend",
                "series": [
                    {"label": "Closing ARR", "points": list(_series(seed=42))},
                    {"label": "Expansion ARR", "points": list(_series(seed=451))},
                ],
            },
        ),
        TileSpec(
            id="tile_incidents",
            role="viz:table:basic",
            props={
                "label": "Open Revenue Incidents",
                "columns": [
                    {"key": "account", "name": "Account"},
                    {"key": "owner", "name": "Owner"},
                    {"key": "severity", "name": "Severity"},
                    {"key": "opened", "name": "Opened"},
                ],
                "rows": [
                    {
                        "account": "Globex Retail",
                        "owner": "Varma",
                        "severity": "Critical",
                        "opened": "2 hours ago",
                    },
                    {
                        "account": "Initrode Labs",
                        "owner": "Chen",
                        "severity": "High",
                        "opened": "8 hours ago",
                    },
                    {
                        "account": "Vehement Capital",
                        "owner": "Garcia",
                        "severity": "Medium",
                        "opened": "1 day ago",
                    },
                ],
            },
        ),
        TileSpec(
            id="tile_nav_command_center",
            role="ui:button:primary",
            props={
                "label": "Open Command Center",
                "caption": "Launch the full revenue ops workspace",
                "href": "https://swarmauri.com/",
                "target": "_blank",
            },
        ),
    ]

    manifest = quick_manifest_from_table(
        layout,
        Viewport(width=1280, height=960),
        tiles,
        version="2025.06",
    )
    payload = to_plain_dict(manifest)
    payload.setdefault("label", "Svelte Runtime Demo")
    payload.setdefault("title", "Svelte Runtime Demo")
    return payload

