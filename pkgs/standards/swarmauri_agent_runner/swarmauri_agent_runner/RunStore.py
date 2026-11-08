from typing import Protocol, runtime_checkable

from .RunState import RunState


@runtime_checkable
class RunStore(Protocol):
    """Persist checkpoints with optimistic concurrency."""

    def create(self, state: RunState) -> None: ...

    def load(self, run_id: str) -> RunState: ...

    def save(self, state: RunState) -> RunState: ...
