"""FastAPI demo for the Control Center UiEvents showcase."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from fastapi import FastAPI, Request

from layout_engine_atoms.runtime.vue import (
    RealtimeBinding,
    RealtimeChannel,
    RealtimeOptions,
    UiEvent,
    UiEventResult,
    mount_layout_app,
)

from .manifest import (
    DEFAULT_STATE,
    ControlCenterState,
    build_manifest,
    _activity_cards,
    _experiment_cards,
    _experiment_slider_view,
    _filter_controls,
    _filters_cards,
    _incident_detail_cards,
    _incident_columns,
    _incident_table_rows,
)

app = FastAPI(title="Layout Engine Control Center Demo")

DOMAIN_CHANNELS = {
    "filters": "control_center.filters",
    "kpis": "control_center.kpis",
    "incidents": "control_center.incidents",
    "experiments": "control_center.experiments",
    "notifications": "control_center.notifications",
}


def _normalize_payload(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {}
    if isinstance(payload, dict):
        return payload
    return dict(payload)


def _coerce_str(value: Any, fallback: str) -> str:
    if value is None:
        return fallback
    return str(value)


def _coerce_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


STATE: ControlCenterState = deepcopy(DEFAULT_STATE)


def _snapshot_state() -> ControlCenterState:
    """Return a shallow copy of the global state."""

    return {
        "filters": deepcopy(STATE["filters"]),
        "kpis": deepcopy(STATE["kpis"]),
        "incidents": deepcopy(STATE["incidents"]),
        "experiments": deepcopy(STATE["experiments"]),
        "notifications": deepcopy(STATE["notifications"]),
    }


def _manifest_builder(_: Request):
    return build_manifest(state=_snapshot_state())


def _log_activity(event_id: str, payload: Mapping[str, Any]) -> None:
    notifications = STATE["notifications"]
    notifications.setdefault("activity", []).insert(
        0, {"title": event_id, "description": str(dict(payload))}
    )


def _refresh_kpi_cards() -> None:
    cards = deepcopy(STATE["kpis"].get("cards", []))
    incidents = STATE["incidents"].get("records", [])
    experiments = STATE["experiments"].get("items", [])
    open_incidents = sum(
        1 for record in incidents if record.get("status") not in {"resolved", "closed"}
    )
    running_experiments = sum(
        1 for entry in experiments if entry.get("status") == "running"
    )
    if cards:
        cards[0]["value"] = str(open_incidents)
    if len(cards) > 1:
        cards[1]["value"] = str(running_experiments)
    STATE["kpis"]["cards"] = cards


def _update_filters(event_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    filters = STATE["filters"]
    if event_id == "ui.filter.time_range.change":
        allowed = {"Last 24 hours", "Last 7 days", "Last 30 days"}
        value = _coerce_str(
            payload.get("value"), filters.get("time_range", "Last 7 days")
        )
        filters["time_range"] = value if value in allowed else filters["time_range"]
    elif event_id == "ui.filter.segment.change":
        allowed = {"All", "Enterprise", "SMB", "Self-serve"}
        value = _coerce_str(payload.get("value"), filters.get("segment", "All"))
        filters["segment"] = value if value in allowed else filters["segment"]
    elif event_id == "ui.filter.search.change":
        filters["search"] = _coerce_str(payload.get("value", ""), "")
    elif event_id == "ui.filter.reset":
        filters.update(
            {
                "time_range": DEFAULT_STATE["filters"]["time_range"],
                "segment": DEFAULT_STATE["filters"]["segment"],
                "search": "",
            }
        )
    filters.setdefault("history", []).append({"event": event_id, "payload": payload})
    return deepcopy(filters)


def _touch_kpis(event_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    kpis = STATE["kpis"]
    kpis["last_event"] = {"event": event_id, "payload": payload}
    _refresh_kpi_cards()
    return deepcopy(kpis)


def _find_incident(record_id: str | None) -> dict[str, Any] | None:
    if not record_id:
        return None
    for record in STATE["incidents"].get("records", []):
        if record["id"] == record_id:
            return record
    return None


def _next_incident_id() -> str:
    return f"INC-{1048 + len(STATE['incidents'].get('records', []))}"


def _update_incidents(event_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    incidents = STATE["incidents"]
    record_id = payload.get("id")
    record = _find_incident(record_id)
    if event_id == "ui.incident.create":
        new_id = record_id or _next_incident_id()
        incidents.setdefault("records", []).append(
            {
                "id": new_id,
                "title": _coerce_str(payload.get("title"), "New incident"),
                "owner": _coerce_str(payload.get("owner"), "Unassigned"),
                "severity": _coerce_str(payload.get("severity"), "medium"),
                "status": "open",
            }
        )
        incidents["selected_id"] = new_id
    elif event_id == "ui.incident.assign" and record:
        record["owner"] = _coerce_str(payload.get("owner"), record["owner"])
    elif event_id == "ui.incident.severity.change" and record:
        allowed = {"low", "medium", "high", "critical"}
        severity = _coerce_str(payload.get("severity"), record["severity"])
        record["severity"] = severity if severity in allowed else record["severity"]
    elif event_id == "ui.incident.status.change" and record:
        allowed = {"open", "in-progress", "resolved", "acknowledged"}
        status = _coerce_str(payload.get("status"), record["status"])
        record["status"] = status if status in allowed else record["status"]
        incidents["selected_id"] = record["id"]
    elif event_id == "ui.incident.comment.add" and record:
        incidents.setdefault("log", []).append(
            {
                "event": event_id,
                "payload": {
                    "id": record["id"],
                    "comment": _coerce_str(payload.get("comment"), ""),
                },
            }
        )
    elif event_id == "ui.incident.bulk_ack":
        for rec in incidents.get("records", []):
            if rec.get("status") == "open":
                rec["status"] = "acknowledged"
    incidents.setdefault("log", []).append({"event": event_id, "payload": payload})
    _refresh_kpi_cards()
    return deepcopy(incidents)


def _find_experiment(entry_id: str | None) -> dict[str, Any] | None:
    if not entry_id:
        return None
    for entry in STATE["experiments"].get("items", []):
        if entry["id"] == entry_id:
            return entry
    return None


def _next_experiment_id() -> str:
    base = 700 + len(STATE["experiments"].get("items", []))
    return f"EXP-{base}"


def _update_experiments(event_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    experiments = STATE["experiments"]
    entry_id = payload.get("id")
    entry = _find_experiment(entry_id)
    if event_id == "ui.experiment.create":
        new_id = entry_id or _next_experiment_id()
        experiments.setdefault("items", []).append(
            {
                "id": new_id,
                "name": _coerce_str(payload.get("name"), f"Experiment {new_id}"),
                "rollout": _clamp(_coerce_int(payload.get("rollout", 0), 0), 0, 100),
                "status": _coerce_str(payload.get("status"), "running"),
            }
        )
    elif event_id == "ui.experiment.rollout.change" and entry:
        entry["rollout"] = _clamp(
            _coerce_int(payload.get("rollout", entry["rollout"]), entry["rollout"]),
            0,
            100,
        )
    elif event_id == "ui.experiment.pause" and entry:
        entry["status"] = "paused"
    elif event_id == "ui.experiment.resume" and entry:
        entry["status"] = "running"
    elif event_id == "ui.experiment.promote" and entry:
        entry["status"] = "completed"
        entry["rollout"] = 100
    experiments.setdefault("history", []).append(
        {"event": event_id, "payload": payload}
    )
    _refresh_kpi_cards()
    return deepcopy(experiments)


def _update_notifications(_: str, __: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(STATE["notifications"])


DOMAIN_HANDLERS: dict[str, Callable[[str, dict[str, Any]], dict[str, Any]]] = {
    "filters": _update_filters,
    "kpis": _touch_kpis,
    "incidents": _update_incidents,
    "experiments": _update_experiments,
    "notifications": _update_notifications,
}


def _filters_view(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "cards": _filters_cards(state),
        "controls": _filter_controls(state),
    }


def _kpi_view(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "cards": deepcopy(state.get("cards", [])),
        "last_event": deepcopy(state.get("last_event")),
    }


def _incident_view(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "rows": _incident_table_rows(state),
        "detail_cards": _incident_detail_cards(state),
        "columns": _incident_columns(),
    }


def _experiment_view(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "cards": _experiment_cards(state),
        "slider": _experiment_slider_view(state),
    }


def _notification_view(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "cards": _activity_cards(state),
    }


DOMAIN_VIEWS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "filters": _filters_view,
    "kpis": _kpi_view,
    "incidents": _incident_view,
    "experiments": _experiment_view,
    "notifications": _notification_view,
}


@dataclass(frozen=True)
class DomainEventDefinition:
    id: str
    domain: str
    description: str


class DomainEventDispatcher:
    """Helper that wires UiEvents to per-domain handlers and channels."""

    def __init__(
        self,
        domain_handlers: Mapping[str, Callable[[str, dict[str, Any]], dict[str, Any]]],
        channel_map: Mapping[str, str],
        view_builders: Mapping[str, Callable[[dict[str, Any]], dict[str, Any]]]
        | None = None,
    ) -> None:
        self._domain_handlers = domain_handlers
        self._channel_map = channel_map
        self._view_builders = view_builders or {}

    def build_events(
        self, definitions: list[DomainEventDefinition]
    ) -> tuple[UiEvent, ...]:
        return tuple(self._build_event(definition) for definition in definitions)

    def _build_event(self, definition: DomainEventDefinition) -> UiEvent:
        handler = self._domain_handlers[definition.domain]

        async def _handle(_: Request, payload: Mapping[str, Any] | None = None):
            normalized = _normalize_payload(payload)
            domain_state = handler(definition.id, normalized)
            view_builder = self._view_builders.get(definition.domain)
            view_payload = view_builder(domain_state) if view_builder else None
            _log_activity(definition.id, normalized)
            result_payload: dict[str, Any] = {
                definition.domain: domain_state,
                "state": domain_state,
                "domain": definition.domain,
            }
            if view_payload is not None:
                result_payload["view"] = view_payload
            return UiEventResult(
                body={
                    "status": "accepted",
                    "event": definition.id,
                    "domain": definition.domain,
                },
                channel=self._channel_map[definition.domain],
                payload=result_payload,
            )

        return UiEvent(
            id=definition.id,
            handler=_handle,
            description=definition.description,
            default_channel=self._channel_map[definition.domain],
        )


EVENT_DEFINITIONS = [
    DomainEventDefinition(
        id="ui.global.refresh",
        domain="filters",
        description="Refresh every tile using the current filter state.",
    ),
    DomainEventDefinition(
        id="ui.filter.time_range.change",
        domain="filters",
        description="Update the dashboard time range filter.",
    ),
    DomainEventDefinition(
        id="ui.filter.segment.change",
        domain="filters",
        description="Update the segment filter.",
    ),
    DomainEventDefinition(
        id="ui.filter.search.change",
        domain="filters",
        description="Update the global search query.",
    ),
    DomainEventDefinition(
        id="ui.filter.reset",
        domain="filters",
        description="Reset all filters to their defaults.",
    ),
    DomainEventDefinition(
        id="ui.kpi.focus",
        domain="kpis",
        description="Focus the KPI deck on a particular metric.",
    ),
    DomainEventDefinition(
        id="ui.kpi.pin",
        domain="kpis",
        description="Pin or favorite a KPI card.",
    ),
    DomainEventDefinition(
        id="ui.chart.series.toggle",
        domain="kpis",
        description="Toggle a chart series from the KPI stack.",
    ),
    DomainEventDefinition(
        id="ui.chart.annotation.add",
        domain="kpis",
        description="Add an annotation to a KPI or chart.",
    ),
    DomainEventDefinition(
        id="ui.incident.create",
        domain="incidents",
        description="Create a new incident from the control center.",
    ),
    DomainEventDefinition(
        id="ui.incident.assign",
        domain="incidents",
        description="Assign the current incident to an owner.",
    ),
    DomainEventDefinition(
        id="ui.incident.severity.change",
        domain="incidents",
        description="Change an incident severity.",
    ),
    DomainEventDefinition(
        id="ui.incident.status.change",
        domain="incidents",
        description="Change an incident lifecycle status.",
    ),
    DomainEventDefinition(
        id="ui.incident.comment.add",
        domain="incidents",
        description="Append a comment to the incident log.",
    ),
    DomainEventDefinition(
        id="ui.incident.bulk_ack",
        domain="incidents",
        description="Acknowledge all open incidents.",
    ),
    DomainEventDefinition(
        id="ui.experiment.create",
        domain="experiments",
        description="Create a new experiment definition.",
    ),
    DomainEventDefinition(
        id="ui.experiment.rollout.change",
        domain="experiments",
        description="Adjust experiment rollout percentage.",
    ),
    DomainEventDefinition(
        id="ui.experiment.pause",
        domain="experiments",
        description="Pause a running experiment.",
    ),
    DomainEventDefinition(
        id="ui.experiment.resume",
        domain="experiments",
        description="Resume a paused experiment.",
    ),
    DomainEventDefinition(
        id="ui.experiment.promote",
        domain="experiments",
        description="Promote a variant to full rollout.",
    ),
]

dispatcher = DomainEventDispatcher(DOMAIN_HANDLERS, DOMAIN_CHANNELS, DOMAIN_VIEWS)
EVENTS = dispatcher.build_events(EVENT_DEFINITIONS)

realtime = RealtimeOptions(
    path="/ws/control-center",
    channels=tuple(
        RealtimeChannel(
            id=channel_id,
            description=f"{domain.title()} updates",
        )
        for domain, channel_id in DOMAIN_CHANNELS.items()
    ),
    bindings=(
        RealtimeBinding(
            channel="control_center.filters",
            tile_id="filter-panel",
            fields={"cards": "view.cards"},
        ),
        RealtimeBinding(
            channel="control_center.filters",
            tile_id="filter-bar",
            fields={"filters": "view.controls"},
        ),
        RealtimeBinding(
            channel="control_center.kpis",
            tile_id="kpi-summary",
            fields={"data": "view.cards"},
        ),
        RealtimeBinding(
            channel="control_center.incidents",
            tile_id="incident-table",
            fields={"rows": "view.rows", "columns": "view.columns"},
        ),
        RealtimeBinding(
            channel="control_center.incidents",
            tile_id="incident-detail",
            fields={"cards": "view.detail_cards"},
        ),
        RealtimeBinding(
            channel="control_center.experiments",
            tile_id="experiment-deck",
            fields={"cards": "view.cards"},
        ),
        RealtimeBinding(
            channel="control_center.experiments",
            tile_id="experiment-rollout",
            fields={"value": "view.slider.value"},
        ),
        RealtimeBinding(
            channel="control_center.notifications",
            tile_id="activity-log",
            fields={"cards": "view.cards"},
        ),
    ),
)

mount_layout_app(
    app,
    manifest_builder=_manifest_builder,
    base_path="/",
    title="Control Center Demo",
    realtime=realtime,
    events=EVENTS,
)
