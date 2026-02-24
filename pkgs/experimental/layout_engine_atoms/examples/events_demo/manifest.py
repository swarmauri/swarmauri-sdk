"""Manifest helpers for the realtime UiEvent demo."""

from __future__ import annotations

from layout_engine_atoms.manifest import create_registry, quick_manifest, tile


def build_manifest(counter_value: int = 0) -> dict:
    """Return a manifest dictionary that references UiEvents-aware tiles."""

    registry = create_registry(catalog="vue")

    tiles = [
        tile(
            "metric",
            "swarmakit:vue:progress-bar",
            span="half",
            props={
                "progress": counter_value,
                "label": f"Button clicks: {counter_value}",
                "style": {
                    "--progress-bg": "rgba(56, 189, 248, 0.25)",
                    "--progress-fg": "#38bdf8",
                },
            },
        ),
        tile(
            "trigger",
            "swarmakit:vue:button",
            span="half",
            props={
                "label": "Increment Counter",
                "variant": "primary",
                "size": "lg",
                "events": {
                    "primary": {
                        "id": "ui.increment",
                        "trigger": "click",
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
                "id": "demo.counter",
                "scope": "page",
                "topic": "page:counter",
                "description": "Broadcasts the latest button click count.",
            }
        ],
        ws_routes=[{"path": "/ws/events", "channels": ["demo.counter"]}],
    )

    manifest_dict = manifest.model_dump()

    manifest_dict.setdefault("meta", {}).setdefault(
        "page",
        {
            "title": "UiEvent Counter Demo",
            "description": "Click the button to execute a Python handler and patch the counter tile via realtime events.",
        },
    )

    return manifest_dict
