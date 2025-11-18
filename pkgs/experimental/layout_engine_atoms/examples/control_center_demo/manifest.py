"""Manifest helpers for the Control Center UiEvents demo."""

from __future__ import annotations

from typing import Any, TypedDict

from layout_engine_atoms.manifest import create_registry, quick_manifest_from_table, tile
from layout_engine.structure import block, col, row, table


class FiltersState(TypedDict, total=False):
    time_range: str
    segment: str
    search: str
    history: list[dict[str, Any]]


class KPIState(TypedDict, total=False):
    cards: list[dict[str, Any]]
    last_event: dict[str, Any] | None


class IncidentRecord(TypedDict, total=False):
    id: str
    title: str
    owner: str
    severity: str
    status: str


class IncidentState(TypedDict, total=False):
    records: list[IncidentRecord]
    selected_id: str | None
    log: list[dict[str, Any]]


class ExperimentEntry(TypedDict, total=False):
    id: str
    name: str
    rollout: int
    status: str


class ExperimentState(TypedDict, total=False):
    items: list[ExperimentEntry]
    history: list[dict[str, Any]]


class NotificationState(TypedDict, total=False):
    alerts: list[dict[str, Any]]
    activity: list[dict[str, Any]]


class ControlCenterState(TypedDict):
    filters: FiltersState
    kpis: KPIState
    incidents: IncidentState
    experiments: ExperimentState
    notifications: NotificationState


DEFAULT_STATE: ControlCenterState = {
    "filters": {
        "time_range": "Last 7 days",
        "segment": "Enterprise",
        "search": "",
        "history": [],
    },
    "kpis": {
        "cards": [
            {
                "title": "Open Incidents",
                "value": "5",
                "accent": "critical",
                "description": "Across all regions",
            },
            {
                "title": "Experiments Running",
                "value": "3",
                "accent": "info",
                "description": "Growth umbrella",
            },
            {
                "title": "Conversion %",
                "value": "4.6%",
                "accent": "success",
                "description": "30-day median",
            },
            {
                "title": "Customer NPS",
                "value": "62",
                "accent": "neutral",
                "description": "Last sync",
            },
        ],
        "last_event": None,
    },
    "incidents": {
        "records": [
            {
                "id": "INC-1048",
                "title": "Checkout latency spike",
                "owner": "A. Rivera",
                "severity": "high",
                "status": "open",
            },
            {
                "id": "INC-1049",
                "title": "Invoice export failures",
                "owner": "N. Patel",
                "severity": "medium",
                "status": "in-progress",
            },
            {
                "id": "INC-1050",
                "title": "Region EU load balancer",
                "owner": "Unassigned",
                "severity": "critical",
                "status": "open",
            },
        ],
        "selected_id": "INC-1048",
        "log": [],
    },
    "experiments": {
        "items": [
            {
                "id": "EXP-701",
                "name": "Checkout redesign",
                "rollout": 35,
                "status": "running",
            },
            {
                "id": "EXP-702",
                "name": "Pricing A/B",
                "rollout": 60,
                "status": "running",
            },
            {
                "id": "EXP-703",
                "name": "Onboarding email",
                "rollout": 20,
                "status": "paused",
            },
        ],
        "history": [],
    },
    "notifications": {
        "alerts": [
            {
                "title": "System Alert",
                "description": "Synthetic monitor degraded",
                "variant": "warning",
            }
        ],
        "activity": [
            {"title": "03:42 UTC", "description": "Filters synced from API"},
            {"title": "02:05 UTC", "description": "Incident INC-1047 resolved"},
        ],
    },
}


def _filters_cards(filters: FiltersState) -> list[dict[str, str]]:
    return [
        {
            "title": "Time Range",
            "description": filters.get("time_range", "Last 24 hours"),
        },
        {"title": "Segment", "description": filters.get("segment", "All customers")},
        {"title": "Search", "description": filters.get("search", "No filter applied")},
    ]


def _filter_controls(filters: FiltersState) -> list[dict[str, Any]]:
    return [
        {
            "key": "timeRange",
            "label": "Time Range",
            "type": "dropdown",
            "options": ["Last 24 hours", "Last 7 days", "Last 30 days"],
            "value": filters.get("time_range", "Last 7 days"),
        },
        {
            "key": "segment",
            "label": "Segment",
            "type": "dropdown",
            "options": ["All", "Enterprise", "SMB", "Self-serve"],
            "value": filters.get("segment", "All"),
        },
        {
            "key": "search",
            "label": "Search",
            "type": "text",
            "value": filters.get("search", ""),
        },
    ]


def _incident_table_rows(state: IncidentState) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in state.get("records", []):
        rows.append(
            {
                "id": record["id"],
                "title": record["title"],
                "owner": record["owner"],
                "severity": record["severity"],
                "status": record["status"],
            }
        )
    return rows


def _incident_columns() -> list[dict[str, str]]:
    return [
        {"id": "id", "label": "Incident"},
        {"id": "title", "label": "Title"},
        {"id": "owner", "label": "Owner"},
        {"id": "severity", "label": "Severity"},
        {"id": "status", "label": "Status"},
    ]


def _experiment_cards(state: ExperimentState) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for entry in state.get("items", []):
        cards.append(
            {
                "title": entry["name"],
                "description": f"Rollout {entry['rollout']}% · {entry['status'].title()}",
            }
        )
    return cards


def _activity_cards(state: NotificationState) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for alert in state.get("alerts", []):
        cards.append(
            {
                "title": alert.get("title", "Alert"),
                "description": alert.get("description", ""),
            }
        )
    for entry in state.get("activity", []):
        cards.append(
            {
                "title": entry.get("title", "Activity"),
                "description": entry.get("description", ""),
            }
        )
    return cards


def _selected_incident(state: IncidentState) -> IncidentRecord | None:
    selected_id = state.get("selected_id")
    if not selected_id:
        return None
    for record in state.get("records", []):
        if record["id"] == selected_id:
            return record
    return None


def _incident_detail_cards(state: IncidentState) -> list[dict[str, Any]]:
    record = _selected_incident(state)
    if not record:
        return [
            {
                "title": "No incident selected",
                "description": "Click a row to inspect incident metadata.",
            }
        ]
    return [
        {
            "title": record["title"],
            "description": f"Owner: {record['owner']} · Severity: {record['severity']} · Status: {record['status']}",
        }
    ]


def _primary_experiment(state: ExperimentState) -> ExperimentEntry | None:
    items = state.get("items", [])
    return items[0] if items else None


def _experiment_slider_view(state: ExperimentState) -> dict[str, Any]:
    primary = _primary_experiment(state)
    if not primary:
        return {
            "id": "EXP-000",
            "label": "Experiment rollout %",
            "value": 0,
        }
    return {
        "id": primary["id"],
        "label": f"{primary['name']} rollout %",
        "value": primary["rollout"],
    }


def _card_style() -> dict[str, str]:
    return {
        "color": "var(--cc-card-fg, #0f172a)",
        "--card-bg": "var(--cc-card-bg, #ffffff)",
        "--card-hover-bg": "var(--cc-card-hover-bg, #f8fafc)",
    }


def _actionable_list_style() -> dict[str, str]:
    return {
        "color": "#e2e8f0",
        "backgroundColor": "rgba(15, 23, 42, 0.78)",
        "border": "1px solid rgba(148, 163, 184, 0.4)",
        "borderRadius": "0.75rem",
        "--actionable-list-item-border-bottom": "1px solid rgba(148, 163, 184, 0.25)",
        "--actionable-list-item-hover-bg": "rgba(56, 189, 248, 0.12)",
        "--action-button-bg": "#38bdf8",
        "--action-button-color": "#0f172a",
        "--action-button-hover-bg": "#0ea5e9",
    }


def _parse_numeric_value(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    raw = str(value).strip()
    if not raw:
        return None
    sanitized = raw.replace("%", "").replace(",", "")
    try:
        return float(sanitized)
    except ValueError:
        return None


def _kpi_table_columns() -> list[dict[str, str]]:
    return [
        {"id": "title", "label": "Metric"},
        {"id": "value", "label": "Value"},
        {"id": "description", "label": "Notes"},
    ]


def _kpi_table_rows(cards: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not cards:
        return rows
    for card in cards:
        rows.append(
            {
                "id": card.get("title", ""),
                "title": card.get("title", ""),
                "value": card.get("value", ""),
                "description": card.get("description", ""),
            }
        )
    return rows


def build_manifest(state: ControlCenterState | None = None) -> dict:
    """Return the Control Center manifest using provided state."""

    state = state or DEFAULT_STATE
    registry = create_registry(catalog="vue")

    filter_controls = _filter_controls(state["filters"])
    incident_detail_cards = _incident_detail_cards(state["incidents"])
    slider_view = _experiment_slider_view(state["experiments"])

    tiles = [
        tile(
            "filter-bar",
            "swarmakit:vue:data-filter-panel",
            span="full",
            props={
                "filters": filter_controls,
                "events": {
                    "timeRange": {
                        "id": "ui.filter.time_range.change",
                        "payload": {"value": state["filters"]["time_range"]},
                    },
                    "segment": {
                        "id": "ui.filter.segment.change",
                        "payload": {"value": state["filters"]["segment"]},
                    },
                    "search": {
                        "id": "ui.filter.search.change",
                        "payload": {"value": state["filters"]["search"]},
                    },
                },
            },
        ),
        tile(
            "filter-panel",
            "swarmakit:vue:cardbased-list",
            span="full",
            props={
                "title": "Active Filters",
                "cards": _filters_cards(state["filters"]),
                "style": _card_style(),
            },
        ),
        tile(
            "kpi-summary",
            "swarmakit:vue:data-table",
            span="full",
            props={
                "title": "Command Center KPIs",
                "columns": _kpi_table_columns(),
                "rows": _kpi_table_rows(state["kpis"].get("cards")),
                "style": _card_style(),
            },
        ),
        tile(
            "kpi-actions",
            "swarmakit:vue:actionable-list",
            span="half",
            props={
                "style": _actionable_list_style(),
                "items": [
                    {
                        "label": "Refocus the KPI deck",
                        "actionLabel": "Focus",
                        "events": [{"id": "ui.kpi.focus", "trigger": "click"}],
                    },
                    {
                        "label": "Pin the top KPI",
                        "actionLabel": "Pin",
                        "events": [{"id": "ui.kpi.pin", "trigger": "click"}],
                    },
                    {
                        "label": "Toggle the conversion series",
                        "actionLabel": "Toggle",
                        "events": [
                            {"id": "ui.chart.series.toggle", "trigger": "click"}
                        ],
                    },
                    {
                        "label": "Annotate the KPI stack",
                        "actionLabel": "Annotate",
                        "events": [
                            {"id": "ui.chart.annotation.add", "trigger": "click"}
                        ],
                    },
                ],
            },
        ),
        tile(
            "incident-table",
            "swarmakit:vue:data-table",
            span="full",
            props={
                "title": "Incident Desk",
                "columns": _incident_columns(),
                "rows": _incident_table_rows(state["incidents"]),
                "events": {
                    "rowClick": {
                        "id": "ui.kpi.focus",
                        "payload": {"source": "incidents"},
                    }
                },
            },
        ),
        tile(
            "incident-detail",
            "swarmakit:vue:cardbased-list",
            span="half",
            props={
                "title": "Incident Detail",
                "cards": incident_detail_cards,
                "style": _card_style(),
            },
        ),
        tile(
            "incident-actions",
            "swarmakit:vue:actionable-list",
            span="half",
            props={
                "style": _actionable_list_style(),
                "items": [
                    {
                        "label": "Assign a new owner",
                        "actionLabel": "Assign",
                        "events": [{"id": "ui.incident.assign", "trigger": "click"}],
                    },
                    {
                        "label": "Adjust incident severity",
                        "actionLabel": "Severity",
                        "events": [
                            {"id": "ui.incident.severity.change", "trigger": "click"}
                        ],
                    },
                    {
                        "label": "Acknowledge every open incident",
                        "actionLabel": "Ack All",
                        "events": [{"id": "ui.incident.bulk_ack", "trigger": "click"}],
                    },
                ],
            },
        ),
        tile(
            "experiment-deck",
            "swarmakit:vue:cardbased-list",
            span="half",
            props={
                "title": "Experiments",
                "cards": _experiment_cards(state["experiments"]),
                "style": _card_style(),
            },
        ),
        tile(
            "experiment-rollout",
            "swarmakit:vue:slider-poll",
            span="half",
            props={
                "question": slider_view["label"],
                "min": 0,
                "max": 100,
                "value": slider_view["value"],
                "showResults": False,
                "style": {
                    "width": "100%",
                },
                "events": {
                    "update:value": {
                        "id": "ui.experiment.rollout.change",
                        "payload": {
                            "id": slider_view["id"],
                        },
                    }
                },
            },
        ),
        tile(
            "experiment-actions",
            "swarmakit:vue:actionable-list",
            span="half",
            props={
                "style": _actionable_list_style(),
                "items": [
                    {
                        "label": "Define a new experiment",
                        "actionLabel": "Create",
                        "events": [{"id": "ui.experiment.create", "trigger": "click"}],
                    },
                    {
                        "label": "Update the primary rollout",
                        "actionLabel": "Adjust",
                        "events": [
                            {"id": "ui.experiment.rollout.change", "trigger": "click"}
                        ],
                    },
                    {
                        "label": "Promote a variant to 100%",
                        "actionLabel": "Promote",
                        "events": [{"id": "ui.experiment.promote", "trigger": "click"}],
                    },
                ],
            },
        ),
        tile(
            "filter-actions",
            "swarmakit:vue:actionable-list",
            span="half",
            props={
                "style": _actionable_list_style(),
                "items": [
                    {
                        "label": "Reset every filter",
                        "actionLabel": "Reset",
                        "events": [{"id": "ui.filter.reset", "trigger": "click"}],
                    },
                    {
                        "label": "Pull fresh data",
                        "actionLabel": "Refresh",
                        "events": [{"id": "ui.global.refresh", "trigger": "click"}],
                    },
                ],
            },
        ),
        tile(
            "activity-log",
            "swarmakit:vue:cardbased-list",
            span="full",
            props={
                "title": "Notifications & Activity",
                "cards": _activity_cards(state["notifications"]),
                "style": _card_style(),
            },
        ),
    ]

    layout = table(
        row(col(block("filter-bar", row_span=2))),
        row(
            col(block("filter-panel")),
            col(block("kpi-summary")),
            height_rows=2,
        ),
        row(
            col(block("kpi-actions")),
            col(block("incident-table")),
            height_rows=2,
        ),
        row(col(block("incident-detail")), col(block("incident-actions"))),
        row(col(block("experiment-deck")), col(block("experiment-actions"))),
        row(col(block("experiment-rollout"))),
        row(col(block("filter-actions"))),
        row(col(block("activity-log")), height_rows=2),
    )
    manifest = quick_manifest_from_table(
        layout,
        tiles,
        registry=registry,
        row_height=220,
        channels=[
            {"id": "control_center.filters", "scope": "page", "topic": "filters"},
            {"id": "control_center.kpis", "scope": "page", "topic": "kpis"},
            {"id": "control_center.incidents", "scope": "page", "topic": "incidents"},
            {
                "id": "control_center.experiments",
                "scope": "page",
                "topic": "experiments",
            },
            {
                "id": "control_center.notifications",
                "scope": "page",
                "topic": "notifications",
            },
        ],
        ws_routes=[
            {
                "path": "/ws/control-center",
                "channels": [
                    "control_center.filters",
                    "control_center.kpis",
                    "control_center.incidents",
                    "control_center.experiments",
                    "control_center.notifications",
                ],
            }
        ],
    )

    manifest_dict = manifest.model_dump()
    manifest_dict.setdefault("meta", {}).setdefault(
        "page",
        {
            "title": "Layout Engine Control Center",
            "description": "Skeleton dashboard for experimenting with generalized UiEvents and realtime channels.",
        },
    )
    return manifest_dict
