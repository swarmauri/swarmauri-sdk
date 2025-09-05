from abc import ABC, abstractmethod


class IRateLimit(ABC):
    """Interface for rate limiting mechanisms."""

    @abstractmethod
    def allow(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens and return whether the request is allowed."""

    @abstractmethod
    def available_tokens(self) -> int:
        """Return the number of currently available tokens."""

    @abstractmethod
    def refill(self) -> None:
        """Refill tokens based on elapsed time or other strategy."""
