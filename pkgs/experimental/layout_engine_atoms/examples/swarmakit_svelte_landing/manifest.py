"""Build the manifest for the SwarmaKit Svelte landing page demo."""

from __future__ import annotations

from typing import Any, Mapping

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
from layout_engine_atoms.catalog import swarma_svelte


def create_manifest() -> Mapping[str, Any]:
    registry = swarma_svelte.build_registry()

    layout = table(
        row(col(block("tile_hero"), size=SizeToken.xl)),
        row(
            col(block("tile_feature_highlights"), size=SizeToken.l),
            col(block("tile_roadmap"), size=SizeToken.m),
        ),
        row(
            col(block("tile_navigation"), size=SizeToken.s),
            col(block("tile_cta"), size=SizeToken.s),
        ),
    )

    tiles: list[TileSpec] = [
        TileSpec(
            id="tile_hero",
            role="swarmakit:svelte:carousel",
            props={
                "slides": [
                    {
                        "src": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1400&q=80",
                        "alt": "Teams collaborating on analytics dashboards",
                    },
                    {
                        "src": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1400&q=80",
                        "alt": "Engineer reviewing application metrics",
                    },
                    {
                        "src": "https://images.unsplash.com/photo-1545239351-1141bd82e8a6?w=1400&q=80",
                        "alt": "Designing customer journeys on screen",
                    },
                ],
                "interval": 6000,
            },
        ),
        TileSpec(
            id="tile_feature_highlights",
            role="swarmakit:svelte:cardbased-list",
            props={
                "cards": [
                    {
                        "title": "Unified Workflow",
                        "description": "Bring AI agents, dashboards, and ops tooling into a single collaborative workspace.",
                    },
                    {
                        "title": "Embedded Intelligence",
                        "description": "Deploy SwarmaKit atoms in Svelte apps with realtime data, theming, and live updates baked in.",
                    },
                    {
                        "title": "Design System Ready",
                        "description": "Match your brand tokens instantly with layout-engine's runtime theme controller.",
                    },
                ]
            },
        ),
        TileSpec(
            id="tile_roadmap",
            role="swarmakit:svelte:timeline-list",
            props={
                "items": [
                    {"id": 1, "label": "Private beta onboarding", "completed": True},
                    {"id": 2, "label": "Realtime analytics launch", "completed": True},
                    {"id": 3, "label": "Partner integrations rollout"},
                    {"id": 4, "label": "Self-serve automations"},
                ],
                "activeIndex": 2,
            },
        ),
        TileSpec(
            id="tile_navigation",
            role="swarmakit:svelte:contextual-navigation",
            props={
                "menuItems": [
                    {"name": "Product", "link": "#product"},
                    {"name": "Platform", "link": "#platform"},
                    {"name": "Pricing", "link": "#pricing"},
                    {"name": "Resources", "link": "#resources"},
                ]
            },
        ),
        TileSpec(
            id="tile_cta",
            role="swarmakit:svelte:badge",
            props={
                "label": "Book a live walkthrough",
                "type": "status",
                "ariaLabel": "Book a live walkthrough call",
            },
        ),
    ]

    manifest = quick_manifest_from_table(
        layout,
        Viewport(width=1440, height=960),
        tiles,
        atoms_registry=registry,
        version="2025.06",
    )
    payload = to_plain_dict(manifest)
    payload.setdefault("label", "SwarmaKit Svelte Landing")
    payload.setdefault("title", "SwarmaKit Svelte Landing Page")
    payload.setdefault(
        "theme",
        {
            "tokens": {
                "color-surface": "#050512",
                "color-surface-elevated": "rgba(20, 23, 51, 0.88)",
                "color-text-primary": "#f3f4ff",
                "color-text-muted": "rgba(201, 205, 255, 0.72)",
                "color-accent": "#7c6cff",
                "grid-column-gap": "1.5rem",
                "grid-row-gap": "1.75rem",
            },
            "style": {
                "background": "radial-gradient(circle at 10% 20%, #1d1930 0%, #050512 60%)",
            },
        },
    )
    return payload


__all__ = ["create_manifest"]
