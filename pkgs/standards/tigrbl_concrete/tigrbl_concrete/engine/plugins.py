"""Engine plugin loading and built-in concrete registrations."""

from __future__ import annotations

from tigrbl_core._spec.plugins import load_engine_plugins


def register() -> None:
    """Backward-compatible registration hook for concrete engines."""
    from . import _register_concrete_defaults

    _register_concrete_defaults()


__all__ = ["load_engine_plugins", "register"]
