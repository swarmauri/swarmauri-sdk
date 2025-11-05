"""Minimal example showing how to use layout_engine_atoms manifest helpers."""

from __future__ import annotations

import json

from layout_engine.structure import block, col, row, table

from layout_engine_atoms.manifest import (
    create_registry,
    quick_manifest_from_table,
    tile,
)


def build_manifest_dict() -> dict:
    """Return a manifest dictionary ready to be served as JSON."""

    registry = create_registry(catalog="vue")

    layout = table(
        row(col(block("hero")), col(block("progress")), height_rows=2),
        row(col(block("summary")), col(block("activity"))),
        row(col(block("status")), col(block("actions"))),
    )

    tiles = [
        tile(
            "hero",
            "swarmakit:vue:cardbased-list",
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
        tile(
            "summary",
            "swarmakit:vue:data-summary",
            span="half",
            props={
                "style": {
                    "backgroundColor": "rgba(56, 189, 248, 0.12)",
                    "color": "#e0f2fe",
                    "--summary-bg": "rgba(56, 189, 248, 0.12)",
                    "--summary-border-color": "rgba(148, 163, 184, 0.45)",
                    "boxShadow": "0 0 0 1px rgba(56, 189, 248, 0.25)",
                },
                "data": [120, 135, 142, 138, 149, 162, 158, 171],
            },
        ),
        tile(
            "activity",
            "swarmakit:vue:activity-indicators",
            span="half",
            props={
                "type": "success",
                "message": "All runtimes healthy · last sync 2m ago",
                "style": {
                    "backgroundColor": "rgba(56, 189, 248, 0.18)",
                    "color": "#e0f2fe",
                    "--success-bg-color": "rgba(56, 189, 248, 0.18)",
                    "--success-text-color": "#e0f2fe",
                    "--padding": "18px",
                },
            },
        ),
        tile(
            "progress",
            "swarmakit:vue:progress-bar",
            props={
                "progress": 72,
            },
        ),
        tile(
            "status",
            "swarmakit:vue:status-dots",
            span="half",
            props={
                "status": "online",
                "style": {
                    "fontSize": "1.1rem",
                    "gap": "12px",
                },
            },
        ),
        tile(
            "actions",
            "swarmakit:vue:actionable-list",
            span="half",
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

    manifest = quick_manifest_from_table(
        layout,
        tiles,
        registry=registry,
        row_height=220,
        channels=[{"id": "ui.events", "scope": "page", "topic": "page:{page_id}:ui"}],
        ws_routes=[{"path": "/ws/ui", "channels": ["ui.events"]}],
    )
    return manifest.model_dump()


def build_manifest_json(indent: int | None = 2) -> str:
    """Return the manifest as a JSON string."""

    return json.dumps(build_manifest_dict(), indent=indent)


if __name__ == "__main__":
    print(build_manifest_json())
