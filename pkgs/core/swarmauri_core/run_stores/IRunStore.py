from abc import ABC, abstractmethod

from .RunCheckpoint import RunCheckpoint


class IRunStore(ABC):
    """Persist checkpoints with atomic optimistic concurrency."""

    @abstractmethod
    def create(self, checkpoint: RunCheckpoint) -> None:
        """Insert revision zero or raise RunConflictError."""
        pass

    @abstractmethod
    def load(self, run_id: str) -> RunCheckpoint:
        """Load a checkpoint or raise KeyError."""
        pass

    @abstractmethod
    def save(self, checkpoint: RunCheckpoint) -> RunCheckpoint:
        """Atomically advance the expected revision or raise RunConflictError."""
        pass
