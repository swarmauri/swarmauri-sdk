"""Rich UiEvent demo manifest."""

from __future__ import annotations

from layout_engine_atoms.manifest import create_registry, quick_manifest, tile


def build_manifest(counter_value: int = 0, entries: list[dict] | None = None) -> dict:
    registry = create_registry(catalog="vue")
    logs = entries or []

    tiles = [
        tile(
            "metric",
            "swarmakit:vue:progress-bar",
            span="half",
            props={
                "progress": counter_value,
                "label": f"Ops processed · {counter_value}",
                "style": {
                    "--progress-fg": "#22d3ee",
                    "--progress-bg": "rgba(45, 212, 191, 0.2)",
                },
            },
        ),
        tile(
            "status",
            "swarmakit:vue:status-dots",
            span="half",
            props={
                "status": "online",
                "message": "Idle",
                "style": {"fontSize": "1.1rem"},
            },
        ),
        tile(
            "toggle",
            "swarmakit:vue:toggle-switch",
            span="half",
            props={
                "checked": True,
                "style": {
                    "--toggle-width": "140px",
                    "--toggle-height": "60px",
                    "--toggle-bg-color": "rgba(148,163,184,0.4)",
                    "--toggle-checked-bg-color": "#22d3ee",
                    "--toggle-slider-color": "#020617",
                    "margin": "0 auto",
                },
                "events": {
                    "change": {
                        "id": "ui.toggle_status",
                        "prop": "checked",
                    }
                },
            },
        ),
        tile(
            "activity",
            "swarmakit:vue:cardbased-list",
            span="full",
            props={
                "title": "Activity Log",
                "cards": logs or [
                    {"title": "Ready", "description": "No events processed yet."}
                ],
            },
        ),
        tile(
            "manual",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "Process single task",
                "size": "lg",
                "variant": "primary",
                "style": {
                    "color": "#020617",
                    "backgroundColor": "#22d3ee",
                },
                "events": {
                    "primary": {
                        "id": "ui.increment",
                        "payload": {"delta": 1, "source": "Manual trigger"},
                    }
                },
            },
        ),
        tile(
            "burst",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "Process 5 tasks",
                "variant": "secondary",
                "style": {
                    "color": "#020617",
                    "backgroundColor": "#a855f7",
                },
                "events": {
                    "primary": {
                        "id": "ui.increment",
                        "payload": {"delta": 5, "source": "Burst run"},
                    }
                },
            },
        ),
        tile(
            "reset",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "Flush queue",
                "variant": "destructive",
                "style": {
                    "color": "#fff",
                    "backgroundColor": "#ef4444",
                },
                "events": {
                    "primary": {
                        "id": "ui.reset",
                        "payload": {"source": "Reset control"},
                    }
                },
            },
        ),
        tile(
            "notify",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "Broadcast maintenance",
                "variant": "ghost",
                "style": {
                    "color": "#0ea5e9",
                    "backgroundColor": "rgba(14,165,233,0.15)",
                    "border": "1px solid rgba(14,165,233,0.4)",
                },
                "events": {
                    "primary": {
                        "id": "ui.broadcast",
                        "payload": {
                            "message": "Scheduled maintenance starting now."
                        },
                    }
                },
            },
        ),
    ]

    manifest = quick_manifest(
        tiles,
        registry=registry,
        columns=2,
        channels=[
            {
                "id": "event.hub",
                "scope": "page",
                "topic": "page:events",
                "description": "Pushes counter values and activity log updates.",
            }
        ],
        ws_routes=[{"path": "/ws/events", "channels": ["event.hub"]}],
    )

    manifest_dict = manifest.model_dump()
    manifest_dict.setdefault("meta", {}).setdefault(
        "page",
        {
            "title": "UiEvents Command Center",
            "description": "Control SwarmaKit tiles with multiple frontend events and realtime patches.",
        },
    )
    return manifest_dict
