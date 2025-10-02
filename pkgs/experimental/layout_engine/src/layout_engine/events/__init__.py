"""Events subsystem: envelope, validation, topic routing, and in-proc bus.

Scopes:
  - site | slot | page | grid | tile | component

Use:
  from layout_engine.events import (
      EventEnvelope, ValidationError, validate_envelope, is_allowed, allowed_types_for,
      route_topic, InProcEventBus, EventRouter, utc_now_iso, make_ack, make_error
  )
"""
from .spec import EventEnvelope, utc_now_iso, make_ack, make_error
from .validators import (
    ValidationError, validate_envelope, route_topic, is_allowed, allowed_types_for,
    ALLOW, SITE, SLOT, PAGE, GRID, TILE, COMPONENT
)
from .ws import InProcEventBus, EventRouter

__all__ = [
    "EventEnvelope", "ValidationError",
    "validate_envelope", "route_topic", "is_allowed", "allowed_types_for",
    "ALLOW", "SITE", "SLOT", "PAGE", "GRID", "TILE", "COMPONENT",
    "InProcEventBus", "EventRouter",
    "utc_now_iso", "make_ack", "make_error",
]
