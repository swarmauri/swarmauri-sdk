"""Backward-compatible registry exports backed by core registry."""

from tigrbl_core._spec.registry import (  # noqa: F401
    EngineRegistration,
    get_engine_registration,
    known_engine_kinds,
    register_engine,
)

__all__ = [
    "EngineRegistration",
    "register_engine",
    "get_engine_registration",
    "known_engine_kinds",
]
