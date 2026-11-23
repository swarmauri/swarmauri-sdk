from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence

from swarmauri_core.messages.IMessage import IMessage

CountInputTokens = Callable[[Sequence[IMessage]], int]


class IAgentCompaction(ABC):
    @abstractmethod
    def compact(self, *, count_input_tokens: CountInputTokens) -> bool:
        """Summarize eligible history and apply it if it reduces input size."""
        pass

    @abstractmethod
    async def acompact(self, *, count_input_tokens: CountInputTokens) -> bool:
        """Asynchronously summarize and apply eligible history."""
        pass

    @abstractmethod
    def compact_if_needed(
        self, *, count_input_tokens: CountInputTokens
    ) -> bool:
        """Compact when the input meets the configured threshold."""
        pass

    @abstractmethod
    async def acompact_if_needed(
        self, *, count_input_tokens: CountInputTokens
    ) -> bool:
        """Asynchronously compact when the input meets the threshold."""
        pass
