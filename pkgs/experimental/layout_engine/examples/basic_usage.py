"""Simple quick-start example for ``layout_engine``.

Run with:
    uv run --directory experimental/layout_engine --package layout-engine python examples/basic_usage.py

The script assembles a component registry, builds a small layout, generates a
manifest JSON file, and emits an HTML preview next to the script.
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
from layout_engine.manifest import manifest_to_json
from layout_engine.targets.media import HtmlExporter

OUTPUT_JSON = Path(__file__).with_suffix(".json")
OUTPUT_HTML = Path(__file__).with_suffix(".html")


def build_registry() -> ComponentRegistry:
    """Register semantic roles with demo front-end modules."""
    registry = ComponentRegistry()
    registry.register_many(
        [
            ComponentSpec(
                role="stat",
                module="@demo/metric",  # maps to a remote module in a real app
                defaults={"format": "compact"},
            ),
            ComponentSpec(
                role="timeseries",
                module="@demo/timeseries",
                defaults={"interval": "1h"},
            ),
        ]
    )
    return registry


def build_tiles() -> list[TileSpec]:
    """Create tiles with authoring-time props and constraints."""
    return [
        TileSpec(
            id="stat_revenue",
            role="stat",
            min_w=240,
            min_h=160,
            props={"label": "Monthly revenue", "value": "$1.2M", "trend": "up"},
        ),
        TileSpec(
            id="stat_growth",
            role="stat",
            min_w=240,
            min_h=160,
            props={"label": "Subscriber growth", "value": "18%", "trend": "stable"},
        ),
        TileSpec(
            id="ts_orders",
            role="timeseries",
            min_w=480,
            min_h=280,
            props={"title": "Orders per hour", "series": [380, 420, 460, 510]},
        ),
    ]


def build_structure():
    """Author a table layout with rows, columns, and tile placements."""
    return table(
        row(
            col(block("stat_revenue"), size=SizeToken.m),
            col(block("stat_growth"), size=SizeToken.m),
        ),
        row(
            col(block("ts_orders"), size=SizeToken.l),
        ),
        gap_x=24,
        gap_y=24,
    )


def main() -> int:
    viewport = Viewport(width=960, height=600)
    registry = build_registry()
    tiles = build_tiles()
    layout = build_structure()

    manifest = quick_manifest_from_table(
        layout,
        viewport,
        tiles,
        row_height=180,
        components_registry=registry,
    )

    OUTPUT_JSON.write_text(manifest_to_json(manifest, indent=2))
    HtmlExporter(title="Layout Engine Quickstart").export(
        manifest, out=str(OUTPUT_HTML)
    )

    print("Generated manifest →", OUTPUT_JSON)
    print("Exported HTML preview →", OUTPUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
