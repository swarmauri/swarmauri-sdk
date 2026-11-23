from __future__ import annotations

import pytest

from layout_engine.events import (
    ValidationError,
    clear_channels,
    register_channels,
    route_topic,
    validate_envelope,
)


def test_event_channel_validation_and_routing() -> None:
    clear_channels()
    register_channels(
        [
            {
                "id": "ui.events",
                "scope": "page",
                "topic": "page:{page_id}:ui",
            }
        ]
    )

    envelope_dict = {
        "scope": "page",
        "type": "page:load",
        "page_id": "home",
        "slot": None,
        "tile_id": None,
        "ts": "2024-01-01T00:00:00Z",
        "request_id": "req-1",
        "target": {},
        "payload": {},
        "channel": "ui.events",
    }

    env = validate_envelope(envelope_dict)
    assert env.channel == "ui.events"
    topic = route_topic(env)
    assert topic == "page:home:ui"

    with pytest.raises(ValidationError):
        validate_envelope({**envelope_dict, "channel": "unknown"})

    clear_channels()
