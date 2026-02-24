"""Hook-specific exceptions for Tigrbl v3."""

from __future__ import annotations

from collections.abc import Iterable


class InvalidHookPhaseError(ValueError):
    """Raised when a hook phase is not one of the supported runtime phases."""

    def __init__(self, *, phase: str, allowed_phases: Iterable[str]):
        self.phase = phase
        self.allowed_phases = tuple(allowed_phases)
        options = ", ".join(self.allowed_phases)
        super().__init__(f"Invalid hook phase '{phase}'. Valid phases are: {options}.")


__all__ = ["InvalidHookPhaseError"]
