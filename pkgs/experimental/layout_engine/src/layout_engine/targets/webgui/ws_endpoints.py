from __future__ import annotations
from typing import Callable, Any, Tuple
import json

from ...events.ws import InProcEventBus
from ...events.validators import validate_envelope, route_topic, ValidationError

class InProcWSBridge:
    """A minimal WS-like bridge you can use in tests or simple apps.

    Usage:
        bus = InProcEventBus()
        ws = InProcWSBridge(bus)
        ws.on_receive_json({...event...})  # validates; publishes to derived topic
        unsub = ws.subscribe("page:dash", lambda msg: print(msg))
    """
    def __init__(self, bus: InProcEventBus):
        self.bus = bus

    # -- client -> server (receive) --
    def on_receive_json(self, event_dict: dict) -> Tuple[str, int]:
        ev = validate_envelope(event_dict)
        topic = route_topic(ev)
        delivered = self.bus.publish(topic, event_dict, retain=False)
        return topic, delivered

    # -- server -> client (send) --
    def subscribe(self, topic: str, callback: Callable[[dict], None]) -> Callable[[], None]:
        return self.bus.subscribe(topic, callback)

    def send_json(self, topic: str, payload: dict) -> int:
        return self.bus.publish(topic, payload, retain=False)
