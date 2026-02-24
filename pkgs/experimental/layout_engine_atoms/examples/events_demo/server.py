"""FastAPI demo showcasing UiEvents + realtime bindings."""

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

app = FastAPI(title="Layout Engine UiEvents Demo")

_state = {"counter": 0}


def _manifest_builder(_: Request):
    return build_manifest(counter_value=_state["counter"])


async def _increment_event(_: Request, payload):
    delta = payload.get("delta", 1) if isinstance(payload, dict) else 1
    try:
        offset = int(delta)
    except (TypeError, ValueError):
        offset = 1
    _state["counter"] = max(0, _state["counter"] + offset)
    value = _state["counter"]
    return UiEventResult(
        body={"value": value},
        channel="demo.counter",
        payload={"value": value},
    )


increment_event = UiEvent(
    id="ui.increment",
    handler=_increment_event,
    description="Increment the server-side counter and broadcast the latest value.",
    default_channel="demo.counter",
)

realtime = RealtimeOptions(
    path="/ws/events",
    channels=(RealtimeChannel(id="demo.counter", description="Counter updates"),),
    bindings=(
        RealtimeBinding(
            channel="demo.counter",
            tile_id="metric",
            fields={"progress": "value"},
        ),
    ),
)

mount_layout_app(
    app,
    manifest_builder=_manifest_builder,
    base_path="/",
    title="SwarmaKit Events Demo",
    realtime=realtime,
    events=(increment_event,),
)
