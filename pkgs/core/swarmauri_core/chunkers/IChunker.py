from abc import ABC, abstractmethod
from typing import Any, List, Union


class IChunker(ABC):
    """
    Interface for chunking text into smaller pieces.

    This interface defines abstract methods for chunking texts. Implementing
    classes
    should provide concrete implementations for these methods tailored to their
    specific
    chunking algorithms.
    """

    @abstractmethod
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> list[Any]:
        pass
