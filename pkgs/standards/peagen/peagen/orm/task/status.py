"""
peagen.orm.task.status
=========================

Canonical enumeration of TaskRun lifecycle states.
"""

from __future__ import annotations

from enum import Enum
from typing import FrozenSet


class Status(str, Enum):
    queued = "queued"
    waiting = "waiting"
    input_required = "input_required"
    auth_required = "auth_required"
    approved = "approved"
    rejected = "rejected"
    dispatched = "dispatched"
    running = "running"
    paused = "paused"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"

    # ─────────────────────────────────────────────────────────
    @classmethod
    def is_terminal(cls, state: str | "Status") -> bool:
        """Return True if *state* represents completion."""
        terminal: FrozenSet[str] = frozenset(
            {"success", "failed", "cancelled", "rejected"}
        )
        value = state.value if isinstance(state, Status) else state
        return value in terminal
