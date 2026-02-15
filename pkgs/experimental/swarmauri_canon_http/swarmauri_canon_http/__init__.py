from __future__ import annotations

from importlib import metadata
from typing import Any

from .http_client import HttpClient


TRANSPORT_ENTRYPOINT_GROUP = "swarmauri_transport"


def _get_transport_entry_points() -> list[metadata.EntryPoint]:
    """Return all registered ``swarmauri_transport`` entry points."""
    entry_points = metadata.entry_points()
    if hasattr(entry_points, "select"):
        return list(entry_points.select(group=TRANSPORT_ENTRYPOINT_GROUP))

    return list(entry_points.get(TRANSPORT_ENTRYPOINT_GROUP, []))


def load_registered_transports() -> dict[str, Any]:
    """Import all registered transport entry points and return loaded objects."""
    loaded_transports: dict[str, Any] = {}
    for entry_point in _get_transport_entry_points():
        loaded_transports[entry_point.name] = entry_point.load()
    return loaded_transports


REGISTERED_TRANSPORTS = load_registered_transports()


__all__ = [
    "HttpClient",
    "REGISTERED_TRANSPORTS",
    "TRANSPORT_ENTRYPOINT_GROUP",
    "load_registered_transports",
]
