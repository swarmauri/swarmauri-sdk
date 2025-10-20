"""Build the manifest used by the Revenue Ops Command Center example."""

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
    row,
    table,
    to_plain_dict,
)
from layout_engine_atoms import build_default_registry


def _kpi_tile(tile_id: str, label: str, value: float, delta: float) -> TileSpec:
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


def _trend_points(seed: int, count: int = 8) -> Iterable[dict[str, float | str]]:
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
    registry = build_default_registry()

    # Customise default atoms for the command center.
    registry.override(
        "viz:metric:kpi",
        defaults={
            "sparkline": False,
            "format": "currency",
            "theme": {
                "tokens": {
                    "accent": "#ff6b6b",
                }
            },
        },
    )

    registry.override(
        "viz:timeseries:line",
        defaults={"legend": True, "curve": "smooth"},
    )

    layout = table(
        row(
            col(block("tile_net_new"), size=SizeToken.m),
            col(block("tile_logo_retention"), size=SizeToken.m),
            col(block("tile_pipeline_velocity"), size=SizeToken.m),
        ),
        row(col(block("tile_revenue_trend"), size=SizeToken.xl)),
        row(
            col(block("tile_incidents"), size=SizeToken.l),
            col(block("tile_notes"), size=SizeToken.s),
        ),
    )

    tiles: list[TileSpec] = [
        _kpi_tile("tile_net_new", "Net New ARR", 1_480_000, 0.14),
        _kpi_tile("tile_logo_retention", "Logo Retention", 0.934, 0.02),
        _kpi_tile("tile_pipeline_velocity", "Pipeline Velocity", 2.8, -0.04),
        TileSpec(
            id="tile_revenue_trend",
            role="viz:timeseries:line",
            props={
                "label": "Revenue Trend",
                "series": [
                    {
                        "label": "Closing ARR",
                        "points": list(_trend_points(seed=42)),
                    },
                    {
                        "label": "Expansion ARR",
                        "points": list(_trend_points(seed=1337)),
                    },
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
                        "account": "Initrode",
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
            id="tile_notes",
            role="viz:panel:markdown",
            props={
                "title": "Revenue Ops Notes",
                "body": (
                    "### Key focus areas\n"
                    "- Finalise Q3 forecast adjustments\n"
                    "- Close the Acme renewal blocker\n"
                    "- Monitor trial conversion cohort anomaly\n"
                ),
            },
        ),
    ]

    manifest = quick_manifest_from_table(
        layout,
        Viewport(width=1280, height=960),
        tiles,
        atoms_registry=registry,
        version="2025.05",
    )
    payload = to_plain_dict(manifest)

    page_theme = {
        "tokens": {
            "color-surface": "#f5f1ff",
            "color-surface-elevated": "#ffffff",
            "color-surface-muted": "#f8f5ff",
            "color-border": "#f3d3d3",
            "color-border-strong": "#edbcbc",
            "color-text-primary": "#1f1a3d",
            "color-text-subtle": "#3c356d",
            "color-text-muted": "#5a4f91",
            "color-accent": "#ff6b6b",
            "color-accent-soft": "#ffd4d4",
            "density": 0.92,
        },
        "style": {
            "background": "radial-gradient(circle at top, #ffe1c3, #f0f3ff 70%)",
            "color-scheme": "light",
            "color": "var(--le-color-text-primary)",
        },
    }

    payload["pages"] = [
        {
            "id": "revenue-ops",
            "label": "Revenue Ops Command Center",
            "slug": "revenue-ops",
            "viewport": dict(payload["viewport"]),
            "grid": dict(payload["grid"]),
            "tiles": list(payload["tiles"]),
            "theme": page_theme,
        }
    ]
    payload["theme"] = {
        "tokens": dict(page_theme["tokens"]),
        "style": dict(page_theme["style"]),
    }

    payload_without_etag = dict(payload)
    payload_without_etag.pop("etag", None)
    payload["etag"] = compute_etag(payload_without_etag)

    return payload


__all__ = ["create_manifest"]
