"""Event handling patterns for rapid development at scale."""

from .decorators import ui_event, returns_update, EventRegistry
from .registry import mount_with_auto_events

__all__ = [
    "ui_event",
    "returns_update",
    "EventRegistry",
    "mount_with_auto_events",
]
