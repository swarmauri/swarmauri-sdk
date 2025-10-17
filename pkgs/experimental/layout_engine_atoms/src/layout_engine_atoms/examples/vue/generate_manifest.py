"""Build and optionally persist the dashboard manifest used by the Vue example.

Run with:
    uv run --directory pkgs/experimental/layout_engine_atoms --package layout-engine-atoms \\
        python -m layout_engine_atoms.examples.vue.generate_manifest
"""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parents[4]

# Ensure local packages are importable when running the script directly.
sys.path.insert(0, str(REPO_ROOT / "pkgs/experimental/layout_engine/src"))
sys.path.insert(0, str(REPO_ROOT / "pkgs/experimental/layout_engine_atoms/src"))

from layout_engine import (  # noqa: E402  (deferred import)
    Manifest,
    SizeToken,
    TileSpec,
    Viewport,
    block,
    col,
    manifest_to_json,
    quick_manifest_from_table,
    row,
    table,
)
from layout_engine_atoms import build_default_registry  # noqa: E402


def manifest_output_path() -> Path:
    return CURRENT_DIR / "dashboard.manifest.json"


def create_manifest() -> Manifest:
    """Compose a sample revenue dashboard manifest."""
    registry = build_default_registry()
    registry.override(
        "viz:metric:kpi",
        defaults={"format": "currency_compact", "sparkline": True},
    )
    registry.override(
        "viz:timeseries:line",
        defaults={"legend": False, "curve": "linear"},
    )

    layout = table(
        row(
            col(block("tile_revenue"), size=SizeToken.m),
            col(block("tile_users"), size=SizeToken.m),
            col(block("tile_retention"), size=SizeToken.m),
        ),
        row(
            col(block("tile_trend"), size=SizeToken.xl),
        ),
        row(
            col(block("tile_ops"), size=SizeToken.xl),
        ),
    )

    tiles = [
        TileSpec(
            id="tile_revenue",
            role="viz:metric:kpi",
            props={
                "label": "Net Revenue",
                "value": 12_400_000,
                "delta": 0.18,
                "trend": "up",
                "period": "QTD",
            },
        ),
        TileSpec(
            id="tile_users",
            role="viz:metric:kpi",
            props={
                "label": "Active Workspaces",
                "value": 48_200,
                "delta": 0.12,
                "trend": "up",
                "period": "Trailing 30d",
            },
        ),
        TileSpec(
            id="tile_retention",
            role="viz:metric:kpi",
            props={
                "label": "Logo Retention",
                "value": 0.931,
                "delta": 0.02,
                "trend": "up",
                "period": "Trailing 12m",
            },
        ),
        TileSpec(
            id="tile_trend",
            role="viz:timeseries:line",
            props={
                "label": "Revenue trend",
                "series": [
                    {
                        "label": "New ARR",
                        "points": [
                            {"x": "2024-09-01", "y": 8.2},
                            {"x": "2024-10-01", "y": 8.5},
                            {"x": "2024-11-01", "y": 9.2},
                            {"x": "2024-12-01", "y": 10.4},
                            {"x": "2025-01-01", "y": 11.05},
                            {"x": "2025-02-01", "y": 11.6},
                            {"x": "2025-03-01", "y": 12.4},
                        ],
                    },
                    {
                        "label": "Expansion ARR",
                        "points": [
                            {"x": "2024-09-01", "y": 2.7},
                            {"x": "2024-10-01", "y": 2.9},
                            {"x": "2024-11-01", "y": 3.2},
                            {"x": "2024-12-01", "y": 3.7},
                            {"x": "2025-01-01", "y": 4.0},
                            {"x": "2025-02-01", "y": 4.4},
                            {"x": "2025-03-01", "y": 4.8},
                        ],
                    },
                ],
            },
        ),
        TileSpec(
            id="tile_ops",
            role="viz:table:basic",
            props={
                "label": "Top expansion opportunities",
                "columns": [
                    {"key": "account", "name": "Account"},
                    {"key": "stage", "name": "Stage"},
                    {"key": "owner", "name": "Owner"},
                    {"key": "value", "name": "ARR ($k)"},
                ],
                "rows": [
                    {
                        "account": "Globex Retail",
                        "stage": "Contracting",
                        "owner": "Varma",
                        "value": 240,
                    },
                    {
                        "account": "Initech",
                        "stage": "Proposal",
                        "owner": "Garcia",
                        "value": 190,
                    },
                    {
                        "account": "Aperture Labs",
                        "stage": "Discovery",
                        "owner": "Chen",
                        "value": 160,
                    },
                    {
                        "account": "Wonka Foods",
                        "stage": "Demo",
                        "owner": "Singh",
                        "value": 130,
                    },
                ],
            },
        ),
    ]

    return quick_manifest_from_table(
        layout,
        Viewport(width=1280, height=960),
        tiles,
        atoms_registry=registry,
        version="2025.10",
    )


def write_manifest(manifest: Manifest) -> Path:
    serialized = manifest_to_json(manifest, indent=2)
    output_path = manifest_output_path()
    output_path.write_text(serialized + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    manifest = create_manifest()
    output = write_manifest(manifest)
    relative_output = output.relative_to(REPO_ROOT)
    print(f"Dashboard manifest written to {relative_output}")


if __name__ == "__main__":
    main()
