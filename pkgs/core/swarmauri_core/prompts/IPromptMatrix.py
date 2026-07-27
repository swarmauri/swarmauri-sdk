from abc import ABC, abstractmethod
from typing import List, Optional, Tuple


class IPromptMatrix(ABC):
    @property
    @abstractmethod
    def shape(self) -> tuple[int, int]:
        """Get the shape (number of agents, sequence length) of the prompt
        matrix."""

    @abstractmethod
    def add_prompt_sequence(self, sequence: list[str | None]) -> None:
        """Add a new prompt sequence to the matrix."""

    @abstractmethod
    def remove_prompt_sequence(self, index: int) -> None:
        """Remove a prompt sequence from the matrix by index."""

    @abstractmethod
    def get_prompt_sequence(self, index: int) -> list[str | None]:
        """Get a prompt sequence from the matrix by index."""

    @abstractmethod
    def show(self) -> list[list[str | None]]:
        """Show the entire prompt matrix."""
