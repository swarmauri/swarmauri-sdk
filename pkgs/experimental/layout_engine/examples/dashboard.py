"""Minimal end-to-end example for layout_engine.

Run with:
    uv run --directory experimental/layout_engine --package layout-engine python examples/dashboard.py

The script builds a component registry, declares a table-based layout, compiles it
into a manifest, and exports an HTML preview.
"""

from __future__ import annotations

from pathlib import Path

from layout_engine import (
    ComponentRegistry,
    ComponentSpec,
    SizeToken,
    TileSpec,
    Viewport,
    block,
    col,
    quick_manifest_from_table,
    row,
    table,
)
from layout_engine.targets.media import HtmlExporter

OUTPUT_HTML = Path(__file__).with_suffix(".html")


def build_components() -> ComponentRegistry:
    """Register semantic roles with front-end modules and defaults."""
    registry = ComponentRegistry()
    registry.register_many(
        [
            ComponentSpec(
                role="hero",
                module="@demo/hero-card",
                defaults={
                    "heading": "Realtime fleet telemetry",
                    "cta": "Open dashboard",
                },
            ),
            ComponentSpec(
                role="stat",
                module="@demo/metric-tile",
                defaults={
                    "format": "compact",
                    "trend": "stable",
                },
            ),
            ComponentSpec(
                role="activity",
                module="@demo/activity-feed",
                defaults={
                    "limit": 5,
                },
            ),
        ]
    )
    return registry


def build_tiles() -> list[TileSpec]:
    """Declare tile constraints and authoring-time props."""
    return [
        TileSpec(
            id="hero",
            role="hero",
            min_w=600,
            min_h=320,
            props={
                "heading": "Autonomous ops overview",
                "cta": "View incidents",
            },
        ),
        TileSpec(
            id="stat_revenue",
            role="stat",
            min_w=260,
            min_h=180,
            props={
                "label": "Monthly revenue",
                "value": "$1.2M",
                "trend": "up",
            },
        ),
        TileSpec(
            id="stat_nps",
            role="stat",
            min_w=260,
            min_h=180,
            props={
                "label": "Support CSAT",
                "value": "93",
                "format": "percent",
            },
        ),
        TileSpec(
            id="activity",
            role="activity",
            min_w=640,
            min_h=360,
            props={
                "title": "Recent activity",
            },
        ),
    ]


def build_structure():
    """Author a table layout with rows, columns, and tile placements."""
    return table(
        row(
            col(block("hero"), size=SizeToken.xl),
            col(block("stat_revenue"), block("stat_nps"), size=SizeToken.s),
            height_rows=2,
        ),
        row(
            col(block("activity"), size=SizeToken.l),
        ),
        gap_x=24,
        gap_y=24,
    )


def main() -> int:
    viewport = Viewport(width=1280, height=720)
    components = build_components()
    tiles = build_tiles()
    layout = build_structure()

    manifest = quick_manifest_from_table(
        layout,
        viewport,
        tiles,
        row_height=200,
        components_registry=components,
    )

    print("Manifest version:", manifest.version)
    for tile in manifest.tiles:
        frame = tile["frame"]
        props = tile.get("props", {})
        print(
            f"- {tile['id']}: role={tile['role']} frame=({frame['x']}, {frame['y']}, {frame['w']}x{frame['h']}) props={props}"
        )

    exporter = HtmlExporter(
        title="Layout Engine Dashboard",
        inline_css="""
        body{margin:0;font-family:system-ui,sans-serif;background:#0f172a;color:#f8fafc;}
        .page{background:linear-gradient(135deg,#1e293b,#0f172a);}
        .tile{border-radius:18px;padding:24px;background:rgba(15,118,110,0.2);border:1px solid rgba(45,212,191,0.35);}
        .tile::after{content:attr(data-tile);position:absolute;top:16px;left:20px;font-size:14px;color:#a5f3fc;}
        .tile[data-tile^='stat']{background:rgba(14,116,144,0.2);border-color:rgba(56,189,248,0.45);}
        """,
    )
    exporter.export(manifest, out=str(OUTPUT_HTML))
    print("Exported HTML preview →", OUTPUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
