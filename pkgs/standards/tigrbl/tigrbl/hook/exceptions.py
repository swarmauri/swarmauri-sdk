"""Compatibility exports for hook exceptions now hosted under runtime."""

from __future__ import annotations

from ..runtime.exceptions import InvalidHookPhaseError

__all__ = ["InvalidHookPhaseError"]
