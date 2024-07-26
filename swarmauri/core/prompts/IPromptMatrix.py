from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any

class IPromptMatrix(ABC):

    @property
    @abstractmethod
    def shape(self) -> Tuple[int, int]:
        """Get the shape (number of agents, sequence length) of the prompt matrix."""
        pass

    @abstractmethod
    def add_prompt_sequence(self, sequence: List[Optional[str]]) -> None:
        """Add a new prompt sequence to the matrix."""
        pass

    @abstractmethod
    def remove_prompt_sequence(self, index: int) -> None:
        """Remove a prompt sequence from the matrix by index."""
        pass

    @abstractmethod
    def get_prompt_sequence(self, index: int) -> List[Optional[str]]:
        """Get a prompt sequence from the matrix by index."""
        pass

    @abstractmethod
    def show(self) -> List[List[Optional[str]]]:
        """Show the entire prompt matrix."""
        pass