from __future__ import annotations
from collections import defaultdict
from typing import Callable, Dict, List, Tuple

from .validators import validate_envelope, route_topic

Subscriber = Callable[[dict], None]


class InProcEventBus:
    """A tiny in-process pub/sub with optional retained last message per topic.

    This is intended for tests and lightweight servers; swap with a real broker in production.
    """

    def __init__(self):
        self._subs: Dict[str, List[Subscriber]] = defaultdict(list)
        self._retained: Dict[str, dict] = {}

    # ---- Subscription API ----
    def subscribe(
        self, topic: str, fn: Subscriber, *, replay_last: bool = False
    ) -> Callable[[], None]:
        self._subs[topic].append(fn)
        if replay_last and topic in self._retained:
            try:
                fn(self._retained[topic])
            except Exception:
                pass

        def _unsub():
            lst = self._subs.get(topic, [])
            if fn in lst:
                lst.remove(fn)

        return _unsub

    def unsubscribe(self, topic: str, fn: Subscriber) -> None:
        lst = self._subs.get(topic, [])
        if fn in lst:
            lst.remove(fn)

    # ---- Publish API ----
    def publish(self, topic: str, message: dict, *, retain: bool = False) -> int:
        if retain:
            self._retained[topic] = message
        count = 0
        for fn in list(self._subs.get(topic, [])):
            try:
                fn(message)
                count += 1
            except Exception:
                # best-effort: swallow subscriber errors
                pass
        return count

    def last(self, topic: str) -> dict | None:
        return self._retained.get(topic)


# -------- Router that validates + publishes --------


class EventRouter:
    """Validate envelopes and publish to topic derived from scope/page/slot/tile."""

    def __init__(self, bus: InProcEventBus):
        self.bus = bus

    def dispatch(self, envelope: dict) -> Tuple[str, int]:
        ev = validate_envelope(envelope)
        topic = route_topic(ev)
        # publish the validated envelope as-is
        delivered = self.bus.publish(topic, envelope, retain=False)
        return topic, delivered
