"""Helper functions for mounting apps with auto-registered events."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI

from .decorators import EventRegistry
from ..runtime.vue import mount_layout_app


def mount_with_auto_events(
    app: "FastAPI",
    manifest_builder,
    **kwargs,
) -> None:
    """Mount layout app with automatically registered events from decorators.

    This function discovers all events registered via @ui_event decorator
    and combines them with any manually provided events before mounting.

    Args:
        app: FastAPI application instance
        manifest_builder: Function that returns manifest dict
        **kwargs: Additional arguments passed to mount_layout_app

    Example:
        >>> from layout_engine_atoms.patterns import mount_with_auto_events
        >>>
        >>> # Import handlers to trigger decorator registration
        >>> from . import handlers
        >>>
        >>> mount_with_auto_events(
        ...     app,
        ...     manifest_builder=build_manifest,
        ...     realtime=RealtimeOptions(...),
        ... )
    """
    # Get all decorated events
    auto_events = EventRegistry.get_all()

    # Merge with any manually provided events
    provided_events = kwargs.pop("events", [])
    if isinstance(provided_events, dict):
        provided_events = list(provided_events.values())

    all_events = list(provided_events) + auto_events

    # Mount with combined events
    mount_layout_app(
        app,
        manifest_builder,
        events=all_events,
        **kwargs,
    )
