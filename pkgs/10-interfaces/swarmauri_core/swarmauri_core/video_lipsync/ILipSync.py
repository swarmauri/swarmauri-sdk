"""Define the shared lip-sync component contract."""

from abc import ABC, abstractmethod
from typing import Any


class ILipSync(ABC):
    """Define synchronous and asynchronous lip-sync generation methods."""

    @abstractmethod
    def predict(
        self,
        video: str,
        audio: str,
        output_path: str = "output.mp4",
        **kwargs: Any,
    ) -> str:
        """Generate lip-synced video and save it to ``output_path``."""
        raise NotImplementedError

    @abstractmethod
    async def apredict(
        self,
        video: str,
        audio: str,
        output_path: str = "output.mp4",
        **kwargs: Any,
    ) -> str:
        """Asynchronously generate and save lip-synced video."""
        raise NotImplementedError
