"""Define the text-to-speech component contract."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator, Mapping
from typing import Any


class ITextToSpeech(ABC):
    """Define synchronous, asynchronous, streaming, and batch TTS methods."""

    @abstractmethod
    def predict(self, text: str, audio_path: str = "output.mp3") -> str:
        """Synthesize text and save the generated audio."""
        pass

    @abstractmethod
    async def apredict(self, text: str, audio_path: str = "output.mp3") -> str:
        """Asynchronously synthesize text and save the generated audio."""
        pass

    @abstractmethod
    def stream(self, text: str, **kwargs: Any) -> Iterator[bytes]:
        """Stream synthesized audio chunks for text."""
        pass

    @abstractmethod
    async def astream(self, text: str, **kwargs: Any) -> AsyncIterator[bytes]:
        """Asynchronously stream synthesized audio chunks for text."""
        pass

    @abstractmethod
    def batch(self, text_path_dict: Mapping[str, str]) -> list[str]:
        """Synthesize multiple text and output-path pairs."""
        pass

    @abstractmethod
    async def abatch(
        self,
        text_path_dict: Mapping[str, str],
        max_concurrent: int = 5,
    ) -> list[str]:
        """Asynchronously synthesize multiple text and output-path pairs."""
        pass
