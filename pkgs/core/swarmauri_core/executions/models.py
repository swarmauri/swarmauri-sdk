"""Driver-neutral execution control records."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExecutionCapabilities:
    """Describe cooperative control supported by an execution driver."""

    pause: bool = True
    resume: bool = True
    stop: bool = True


@dataclass(frozen=True)
class ExecutionSnapshot:
    """Persist scheduling state, lifecycle intent and a driver identity."""

    execution_id: str
    task_id: str
    driver: str
    status: str = "ready"
    state: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: str | None = None
    revision: int = 0
    parent_id: str | None = None

    def __post_init__(self):
        if self.status not in {
            "ready",
            "running",
            "pausing",
            "paused",
            "stopping",
            "stopped",
            "waiting",
            "completed",
            "failed",
        }:
            raise ValueError("Invalid execution status")


@dataclass(frozen=True)
class DriverStep:
    """Return the next durable scheduling boundary."""

    state: dict[str, Any]
    completed: bool = False
    waiting: bool = False
    result: Any = None
