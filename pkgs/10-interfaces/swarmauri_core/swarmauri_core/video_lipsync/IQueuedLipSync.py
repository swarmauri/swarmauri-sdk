"""Define observable queued lip-sync provider capabilities."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Any

from swarmauri_core.video_lipsync.types import LipSyncJobEvent


class IQueuedLipSync(ABC):
    """Expose job submission and normalized progress observation."""

    @abstractmethod
    def submit(self, video: str, audio: str, **kwargs: Any) -> str:
        """Submit a lip-sync job and return its provider job identifier."""
        raise NotImplementedError

    @abstractmethod
    def get_status(self, job_id: str) -> LipSyncJobEvent:
        """Return the current normalized state for ``job_id``."""
        raise NotImplementedError

    @abstractmethod
    def iter_events(self, job_id: str) -> Iterator[LipSyncJobEvent]:
        """Yield changed job states until the job reaches a terminal state."""
        raise NotImplementedError

    @abstractmethod
    async def aiter_events(
        self, job_id: str
    ) -> AsyncIterator[LipSyncJobEvent]:
        """Asynchronously yield changed states until the job terminates."""
        raise NotImplementedError
