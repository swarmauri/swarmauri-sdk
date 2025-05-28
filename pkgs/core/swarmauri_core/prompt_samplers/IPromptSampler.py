from abc import ABC, abstractmethod


class IPromptSampler(ABC):
    """Interface for sampling prompts from a collection."""

    @abstractmethod
    def sample(self, *args, **kwargs) -> str:
        """Return a sampled prompt from the provided arguments."""
        pass
