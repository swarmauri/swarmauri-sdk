"""Hook type definitions shared by canon mapping modules."""

from __future__ import annotations

from tigrbl_atoms import HookPhase, HookPhases, HookPredicate, StepFn

# Canon hook phase set consumed by mapping composition.
PHASES = (
    "PRE_TX_BEGIN",
    "START_TX",
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "PRE_COMMIT",
    "END_TX",
    "POST_COMMIT",
    "POST_RESPONSE",
    "ON_ERROR",
    "ON_PRE_TX_BEGIN_ERROR",
    "ON_START_TX_ERROR",
    "ON_PRE_HANDLER_ERROR",
    "ON_HANDLER_ERROR",
    "ON_POST_HANDLER_ERROR",
    "ON_PRE_COMMIT_ERROR",
    "ON_END_TX_ERROR",
    "ON_POST_COMMIT_ERROR",
    "ON_POST_RESPONSE_ERROR",
    "ON_ROLLBACK",
    "FINAL",
)

__all__ = ["HookPhase", "HookPhases", "PHASES", "StepFn", "HookPredicate"]
