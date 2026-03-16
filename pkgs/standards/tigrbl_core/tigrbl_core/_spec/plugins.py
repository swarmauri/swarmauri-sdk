"""Engine plugin discovery helpers.

Plugins are loaded via the ``tigrbl.engine_plugins`` entry point group.
Each entry point may resolve to either:
- a callable that performs registration side effects, or
- a module/object exposing a ``register()`` callable.
"""

from __future__ import annotations

from importlib.metadata import entry_points
from typing import Any

_LOADED = False


def _invoke_plugin(obj: Any) -> None:
    if callable(obj):
        obj()
        return
    register = getattr(obj, "register", None)
    if callable(register):
        register()


def load_engine_plugins() -> None:
    """Load engine plugins once per process."""
    global _LOADED
    if _LOADED:
        return

    try:
        discovered = entry_points(group="tigrbl.engine_plugins")
    except TypeError:
        discovered = entry_points().get("tigrbl.engine_plugins", [])  # pragma: no cover

    for ep in discovered:
        try:
            _invoke_plugin(ep.load())
        except Exception:
            # EngineSpec handles missing registrations with explicit error text.
            continue

    _LOADED = True
