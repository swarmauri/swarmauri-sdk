"""Build the manifest for the Customer Success Command Center example."""

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
    quick_view_model_from_table,
    row,
    table,
    to_plain_dict,
)
from layout_engine_atoms import build_default_registry


def _trend_points(seed: int, count: int = 12) -> Iterable[dict[str, float | str]]:
    rng = Random(seed)
    base = datetime.now() - timedelta(weeks=count - 1)
    value = rng.uniform(68, 92)
    for idx in range(count):
        value += rng.uniform(-2.5, 3.5)
        yield {
            "x": (base + timedelta(weeks=idx)).strftime("%Y-%m-%d"),
            "y": round(max(value, 40), 1),
        }


def _kpi_tile(
    tile_id: str,
    label: str,
    value: float,
    delta: float,
    *,
    format: str | None = None,
    period: str = "Last 30 days",
) -> TileSpec:
    props: dict[str, Any] = {
        "label": label,
        "value": value,
        "delta": delta,
        "period": period,
    }
    if format:
        props["format"] = format
    return TileSpec(
        id=tile_id,
        role="viz:metric:kpi",
        props=props,
    )


def _overview_layout():
    return table(
        row(
            col(block("tile_hero"), size=SizeToken.l),
            col(block("tile_cta"), size=SizeToken.s),
        ),
        row(
            col(block("tile_health"), size=SizeToken.m),
            col(block("tile_expansion"), size=SizeToken.m),
            col(block("tile_retention"), size=SizeToken.m),
        ),
        row(col(block("tile_trend"), size=SizeToken.xl)),
        row(
            col(block("tile_playbooks"), size=SizeToken.l),
            col(block("tile_wins"), size=SizeToken.s),
        ),
    )


def _accounts_layout():
    return table(
        row(
            col(block("tile_back"), size=SizeToken.s),
            col(block("tile_accounts_summary"), size=SizeToken.l),
        ),
        row(
            col(block("tile_segments"), size=SizeToken.m),
            col(block("tile_churn"), size=SizeToken.m),
            col(block("tile_advocates"), size=SizeToken.m),
        ),
        row(col(block("tile_cohort"), size=SizeToken.xl)),
        row(
            col(block("tile_accounts_table"), size=SizeToken.l),
            col(block("tile_accounts_notes"), size=SizeToken.s),
        ),
    )


def _overview_tiles() -> list[TileSpec]:
    hero_body = (
        "### Welcome back, Team!\n"
        "Deliver on customer promises and keep health trending up across all segments. "
        "Monitor playbooks in flight and celebrate recent wins."
    )
    return [
        TileSpec(
            id="tile_hero",
            role="viz:panel:markdown",
            props={
                "title": "Customer Success Command Center",
                "body": hero_body,
            },
        ),
        TileSpec(
            id="tile_cta",
            role="ui:button:primary",
            props={
                "label": "View Key Accounts",
                "caption": "Jump into the account deep dive workspace",
                "targetPage": "accounts",
            },
        ),
        _kpi_tile(
            "tile_health",
            "Global Health",
            0.86,
            0.05,
            period="Quarter to date",
        ),
        _kpi_tile(
            "tile_expansion",
            "Expansion ARR",
            2_450_000,
            0.12,
            format="currency_compact",
            period="Last 30 days",
        ),
        _kpi_tile(
            "tile_retention",
            "Renewal Confidence",
            0.93,
            0.03,
            period="Next 90 days",
        ),
        TileSpec(
            id="tile_trend",
            role="viz:timeseries:line",
            props={
                "label": "Net Revenue Retention",
                "series": [
                    {
                        "label": "NRR %",
                        "points": list(_trend_points(seed=2024)),
                    },
                    {
                        "label": "Target %",
                        "points": list(_trend_points(seed=1000)),
                    },
                ],
            },
        ),
        TileSpec(
            id="tile_playbooks",
            role="viz:table:basic",
            props={
                "label": "Active Success Playbooks",
                "columns": [
                    {"key": "segment", "name": "Segment"},
                    {"key": "playbook", "name": "Playbook"},
                    {"key": "owner", "name": "Owner"},
                    {"key": "status", "name": "Status"},
                ],
                "rows": [
                    {
                        "segment": "Enterprise",
                        "playbook": "Executive QBR Sprint",
                        "owner": "Lopez",
                        "status": "In Progress",
                    },
                    {
                        "segment": "Mid-market",
                        "playbook": "CSAT Recovery Loop",
                        "owner": "Singh",
                        "status": "Reviewing",
                    },
                    {
                        "segment": "Adoption",
                        "playbook": "Activation Accelerator",
                        "owner": "Rahman",
                        "status": "On Track",
                    },
                ],
            },
        ),
        TileSpec(
            id="tile_wins",
            role="viz:panel:markdown",
            props={
                "title": "Recent Win Stories",
                "body": (
                    "- **Acme Robotics** upsold +$420k after pilot automation workshop\n"
                    "- **Northwind** expanded to EMEA region with 3 strategic advocates\n"
                    "- **Zephyr Cloud** renewed early with zero expansion backlog"
                ),
            },
        ),
    ]


def _accounts_tiles() -> list[TileSpec]:
    return [
        TileSpec(
            id="tile_back",
            role="ui:button:primary",
            props={
                "label": "Back to Overview",
                "caption": "Return to high-level metrics",
                "targetPage": "overview",
                "variant": "secondary",
            },
        ),
        TileSpec(
            id="tile_accounts_summary",
            role="viz:panel:markdown",
            props={
                "title": "Operational Focus",
                "body": (
                    "- 48 enterprise accounts monitored with weekly checkpoints\n"
                    "- Expansion opportunities prioritised across advocate tier\n"
                    "- Automations triaging playbook assignments nightly"
                ),
            },
        ),
        _kpi_tile(
            "tile_churn",
            "At-Risk Churn",
            0.11,
            -0.02,
            period="Moving 60 days",
        ),
        _kpi_tile(
            "tile_advocates",
            "Active Advocates",
            68,
            0.08,
            period="Rolling 90 days",
        ),
        TileSpec(
            id="tile_segments",
            role="viz:bar:horizontal",
            props={
                "label": "Segment Health Distribution",
                "series": [
                    {"label": "Enterprise", "value": 92, "annotation": "Top quartile"},
                    {"label": "Mid-market", "value": 84, "annotation": "Improving"},
                    {"label": "SMB", "value": 76},
                    {"label": "Growth", "value": 88, "annotation": "Playbook success"},
                ],
            },
        ),
        TileSpec(
            id="tile_cohort",
            role="viz:timeseries:line",
            props={
                "label": "Activation Velocity (Days)",
                "series": [
                    {
                        "label": "New Customers",
                        "points": [
                            {"x": point["x"], "y": max(25 - idx * 1.1, 12)}
                            for idx, point in enumerate(_trend_points(88, 8))
                        ],
                    },
                ],
            },
        ),
        TileSpec(
            id="tile_accounts_table",
            role="viz:table:basic",
            props={
                "label": "Strategic Accounts",
                "columns": [
                    {"key": "account", "name": "Account"},
                    {"key": "csm", "name": "CSM"},
                    {"key": "stage", "name": "Stage"},
                    {"key": "health", "name": "Health"},
                    {"key": "next", "name": "Next Action"},
                ],
                "rows": [
                    {
                        "account": "Quantum Analytics",
                        "csm": "Carson",
                        "stage": "Adoption",
                        "health": "92 / 100",
                        "next": "Executive QBR 11/02",
                    },
                    {
                        "account": "Nimbus Retail",
                        "csm": "Idowu",
                        "stage": "Renewal Prep",
                        "health": "78 / 100",
                        "next": "Risk workshop 10/28",
                    },
                    {
                        "account": "Atlas Manufacturing",
                        "csm": "Fernandez",
                        "stage": "Expansion",
                        "health": "88 / 100",
                        "next": "Automation demo 10/25",
                    },
                ],
            },
        ),
        TileSpec(
            id="tile_accounts_notes",
            role="viz:panel:markdown",
            props={
                "title": "Guidance",
                "body": (
                    "Prioritise accounts with declining executive engagement. "
                    "Surface references ahead of Q4 pipeline acceleration."
                ),
            },
        ),
    ]


def _theme(tokens: Mapping[str, Any], background: str) -> Mapping[str, Any]:
    return {
        "tokens": dict(tokens),
        "style": {
            "background": background,
            "color-scheme": "light",
            "color": "var(--le-color-text-primary)",
        },
    }


def create_manifest() -> Mapping[str, Any]:
    registry = build_default_registry()
    registry.override(
        "viz:metric:kpi",
        defaults={
            "sparkline": False,
            "format": "compact",
            "theme": {"tokens": {"accent": "#1fb6a6"}},
        },
    )

    overview_layout = _overview_layout()
    accounts_layout = _accounts_layout()

    overview_tiles = _overview_tiles()
    accounts_tiles = _accounts_tiles()

    manifest = quick_manifest_from_table(
        overview_layout,
        Viewport(width=1280, height=960),
        overview_tiles,
        atoms_registry=registry,
        version="2025.06",
    )
    payload = to_plain_dict(manifest)

    overview_vm = quick_view_model_from_table(
        overview_layout,
        Viewport(width=1280, height=960),
        overview_tiles,
        atoms_registry=registry,
    )
    accounts_vm = quick_view_model_from_table(
        accounts_layout,
        Viewport(width=1280, height=960),
        accounts_tiles,
        atoms_registry=registry,
    )

    overview_theme_tokens = {
        "color-surface": "#f4fffb",
        "color-surface-elevated": "#ffffff",
        "color-surface-muted": "#ebfaf5",
        "color-border": "#c9f1e8",
        "color-border-strong": "#9fe4d5",
        "color-text-primary": "#113a3a",
        "color-text-subtle": "#305856",
        "color-text-muted": "#4a6f6c",
        "color-accent": "#1fb6a6",
        "color-accent-soft": "#c6f4ec",
        "density": 0.94,
    }
    accounts_theme_tokens = {
        **overview_theme_tokens,
        "color-accent": "#ff8a4c",
        "color-accent-soft": "#ffe1d0",
    }

    overview_page = {
        "id": "overview",
        "label": "Customer Success Overview",
        "slug": "overview",
        "viewport": dict(overview_vm["viewport"]),
        "grid": dict(overview_vm["grid"]),
        "tiles": list(overview_vm["tiles"]),
        "theme": _theme(
            overview_theme_tokens,
            "linear-gradient(135deg, #f4fffb 0%, #d3f8f2 65%)",
        ),
    }
    accounts_page = {
        "id": "accounts",
        "label": "Key Accounts",
        "slug": "accounts",
        "viewport": dict(accounts_vm["viewport"]),
        "grid": dict(accounts_vm["grid"]),
        "tiles": list(accounts_vm["tiles"]),
        "theme": _theme(
            accounts_theme_tokens,
            "linear-gradient(135deg, #fff7ed 0%, #f4fffb 60%)",
        ),
    }

    payload["pages"] = [overview_page, accounts_page]
    payload["tiles"] = list(overview_vm["tiles"])
    payload["theme"] = _theme(
        overview_theme_tokens,
        "linear-gradient(135deg, #f4fffb 0%, #d3f8f2 65%)",
    )

    payload_without_etag = dict(payload)
    payload_without_etag.pop("etag", None)
    payload["etag"] = compute_etag(payload_without_etag)

    return payload


__all__ = ["create_manifest"]
