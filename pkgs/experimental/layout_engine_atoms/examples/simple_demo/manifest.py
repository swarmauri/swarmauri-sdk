"""Minimal example showing how to use layout_engine_atoms presets with layout-engine."""

from __future__ import annotations

import json

from layout_engine import LayoutCompiler, ManifestBuilder, TileSpec, Viewport
from layout_engine.core.size import Size
from layout_engine.grid.spec import GridSpec, GridTile, GridTrack
from layout_engine_atoms import build_registry


def build_manifest_dict() -> dict:
    """Return a manifest dictionary ready to be served as JSON."""

    atoms = build_registry(name="vue")
    atoms.override("swarmakit:vue:cardbased-list", defaults={})

    grid = GridSpec(
        columns=[
            GridTrack(size=Size(1, "fr")),
            GridTrack(size=Size(1, "fr")),
        ],
        row_height=220,
        tokens={"columns": "sgd:columns:2"},
    )
    viewport = Viewport(width=1280, height=960)
    placements = [
        GridTile(tile_id="hero", col=0, row=0, col_span=2),
        GridTile(tile_id="summary", col=0, row=1),
        GridTile(tile_id="activity", col=1, row=1),
        GridTile(tile_id="progress", col=0, row=2, col_span=2),
        GridTile(tile_id="status", col=0, row=3),
        GridTile(tile_id="actions", col=1, row=3),
    ]

    compiler = LayoutCompiler()
    frames = compiler.frames(grid, viewport, placements)
    tiles = [
        TileSpec(
            id="hero",
            role="swarmakit:vue:cardbased-list",
            props={
                "style": {
                    "color": "#e2e8f0",
                    "--card-bg": "rgba(15, 23, 42, 0.85)",
                    "--card-border": "1px solid rgba(148, 163, 184, 0.25)",
                    "--card-hover-bg": "rgba(56, 189, 248, 0.15)",
                    "--card-selected-border-color": "#38bdf8",
                },
                "cards": [
                    {
                        "title": "Swiss Grid Defaults",
                        "description": "Tokens keep columns, gaps, and baselines aligned across runtimes.",
                    },
                    {
                        "title": "SwarmaKit Registry",
                        "description": "Atoms auto-import with merged defaults for consistent UX payloads.",
                    },
                    {
                        "title": "Realtime Ready",
                        "description": "Channels and websocket routes unlock live dashboards out of the box.",
                    },
                ],
            },
        ),
        TileSpec(
            id="summary",
            role="swarmakit:vue:data-summary",
            props={
                "style": {
                    "--summary-bg": "rgba(56, 189, 248, 0.12)",
                    "--summary-border-color": "rgba(148, 163, 184, 0.45)",
                },
                "data": [120, 135, 142, 138, 149, 162, 158, 171],
            },
        ),
        TileSpec(
            id="activity",
            role="swarmakit:vue:activity-indicators",
            props={
                "type": "success",
                "message": "All runtimes healthy · last sync 2m ago",
                "style": {
                    "--success-bg-color": "rgba(56, 189, 248, 0.18)",
                    "--success-text-color": "#e0f2fe",
                    "--padding": "18px",
                },
            },
        ),
        TileSpec(
            id="progress",
            role="swarmakit:vue:progress-bar",
            props={
                "progress": 52,
            },
        ),
        TileSpec(
            id="status",
            role="swarmakit:vue:status-dots",
            props={
                "status": "online",
            },
        ),
        TileSpec(
            id="actions",
            role="swarmakit:vue:actionable-list",
            props={
                "items": [
                    {"label": "Review staging publish", "actionLabel": "Open"},
                    {
                        "label": "Sync atom catalog updates",
                        "actionLabel": "Run",
                        "loading": True,
                    },
                    {
                        "label": "Archive legacy layout",
                        "actionLabel": "Archive",
                        "disabled": True,
                    },
                ],
            },
        ),
    ]
    view_model = compiler.view_model(
        grid,
        viewport,
        frames,
        tiles,
        atoms_registry=atoms,
        channels=[{"id": "ui.events", "scope": "page", "topic": "page:{page_id}:ui"}],
        ws_routes=[{"path": "/ws/ui", "channels": ["ui.events"]}],
    )

    manifest = ManifestBuilder().build(view_model)
    payload = manifest.model_dump()

    for tile in payload.get("tiles", []):
        atom = tile.get("atom")
        if not atom:
            continue
        atom.setdefault("role", tile.get("role"))
        if atom.get("module") == "@swarmakit/vue":
            atom.setdefault("family", "swarmakit")
            atom.setdefault("package", "@swarmakit/vue")

    return payload


def build_manifest_json(indent: int | None = 2) -> str:
    """Return the manifest as a JSON string."""

    return json.dumps(build_manifest_dict(), indent=indent)


if __name__ == "__main__":
    print(build_manifest_json())
