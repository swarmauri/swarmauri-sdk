from abc import ABC, abstractmethod
from typing import Any

class IPromptTemplateSampler(ABC):
    """Interface for classes that sample prompt templates."""

    @abstractmethod
    def sample(self, *args, **kwargs) -> Any:
        """Return a sampled prompt template."""
        pass
