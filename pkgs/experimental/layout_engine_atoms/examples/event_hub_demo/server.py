"""Server wiring the UiEvents command center demo."""

from __future__ import annotations

from fastapi import FastAPI, Request

from layout_engine_atoms.runtime.vue import (
    RealtimeBinding,
    RealtimeChannel,
    RealtimeOptions,
    UiEvent,
    UiEventResult,
    mount_layout_app,
)

from .manifest import build_manifest

app = FastAPI(title="UiEvents Command Center")

_state = {
    "counter": 0,
    "entries": [],
    "online": True,
}


def _snapshot(message: str) -> dict:
    return {
        "value": _state["counter"],
        "label": f"Ops processed · {_state['counter']}",
        "message": message,
        "online": _state["online"],
        "entries": list(_state["entries"]),
    }


def _append_entry(title: str, description: str) -> None:
    _state["entries"] = [
        {"title": title, "description": description},
        *_state["entries"],
    ][:8]


def _manifest_builder(_: Request):
    return build_manifest(
        counter_value=_state["counter"],
        entries=_state["entries"],
    )


async def _increment_event(_: Request, payload: dict | None = None):
    payload = payload or {}
    delta = payload.get("delta", 1)
    try:
        increment = int(delta)
    except (TypeError, ValueError):
        increment = 1
    _state["counter"] = max(0, _state["counter"] + increment)
    source = payload.get("source") or "Manual trigger"
    _append_entry(
        f"{source}",
        f"Processed {increment} tasks · total {_state['counter']}",
    )
    snapshot = _snapshot(f"{source} completed")
    return UiEventResult(
        body=snapshot,
        channel="event.hub",
        payload=snapshot,
    )


async def _reset_event(_: Request, __: dict | None = None):
    _state["counter"] = 0
    _append_entry("Reset", "Counter cleared to zero.")
    snapshot = _snapshot("Queue flushed")
    return UiEventResult(
        body=snapshot,
        channel="event.hub",
        payload=snapshot,
    )


async def _broadcast_event(_: Request, payload: dict | None = None):
    message = (payload or {}).get("message") or "Broadcast received."
    _append_entry("Broadcast", message)
    snapshot = _snapshot(message)
    return UiEventResult(
        body=snapshot,
        channel="event.hub",
        payload=snapshot,
    )


async def _toggle_status(_: Request, payload: dict | None = None):
    desired = (payload or {}).get("checked")
    if isinstance(desired, bool):
        _state["online"] = desired
    else:
        _state["online"] = not _state["online"]
    state_label = "Online" if _state["online"] else "Offline"
    _append_entry("Status toggle", f"Status changed to {state_label}.")
    snapshot = _snapshot(f"Status: {state_label}")
    return UiEventResult(
        body=snapshot,
        channel="event.hub",
        payload=snapshot,
    )


realtime = RealtimeOptions(
    path="/ws/events",
    channels=(
        RealtimeChannel(
            id="event.hub",
            description="Counter values and activity feed",
            topic="page:events",
        ),
    ),
    bindings=(
        RealtimeBinding(
            channel="event.hub",
            tile_id="metric",
            fields={
                "progress": "value",
                "label": "label",
            },
        ),
        RealtimeBinding(
            channel="event.hub",
            tile_id="status",
            fields={"message": "message"},
        ),
        RealtimeBinding(
            channel="event.hub",
            tile_id="toggle",
            fields={"checked": "online"},
        ),
        RealtimeBinding(
            channel="event.hub",
            tile_id="activity",
            fields={"cards": "entries"},
        ),
    ),
)

events = (
    UiEvent(id="ui.increment", handler=_increment_event, default_channel="event.hub"),
    UiEvent(id="ui.reset", handler=_reset_event, default_channel="event.hub"),
    UiEvent(id="ui.broadcast", handler=_broadcast_event, default_channel="event.hub"),
    UiEvent(id="ui.toggle_status", handler=_toggle_status, default_channel="event.hub"),
)

mount_layout_app(
    app,
    manifest_builder=_manifest_builder,
    base_path="/",
    title="UiEvents Command Center",
    realtime=realtime,
    events=events,
)
