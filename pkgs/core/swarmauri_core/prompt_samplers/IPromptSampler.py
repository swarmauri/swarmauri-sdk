from abc import ABC, abstractmethod
from typing import Sequence, Optional


class IPromptSampler(ABC):
    """Interface for sampling prompts from a collection."""

    @abstractmethod
    def sample(self, prompts: Optional[Sequence[str]] = None) -> str:
        """Return a sampled prompt from the provided sequence or internal store."""
        pass

    @abstractmethod
    def set_prompts(self, prompts: Sequence[str]) -> None:
        """Replace the internal prompt collection with a new list."""
        pass

    @abstractmethod
    def add_prompt(self, prompt: str) -> None:
        """Add a single prompt to the internal collection."""
        pass

    @abstractmethod
    def add_prompts(self, prompts: Sequence[str]) -> None:
        """Extend the internal collection with multiple prompts."""
        pass

    @abstractmethod
    def remove_prompt(self, prompt: str) -> None:
        """Remove a prompt from the internal collection."""
        pass

    @abstractmethod
    def clear_prompts(self) -> None:
        """Remove all stored prompts."""
        pass

    @abstractmethod
    def show(self) -> Sequence[str]:
        """Return all stored prompts."""
        pass
