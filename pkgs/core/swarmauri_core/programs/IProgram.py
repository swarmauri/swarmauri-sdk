from abc import ABC, abstractmethod
from typing import Any, Dict, TypeVar

T = TypeVar("T", bound="IProgram")
DiffType = Dict[str, Any]  # Type for diff representation


class IProgram(ABC):
    """
    Interface for programs under evolution.

    This abstract class defines the contract that all evolvable programs
    must implement, providing methods for comparing, modifying, and validating
    program representations.
    """

    @abstractmethod
    def diff(self, other: "IProgram") -> DiffType:
        """
        Calculate the difference between this program and another.

        Args:
            other: Another program to compare against

        Returns:
            A structured representation of the differences between programs

        Raises:
            TypeError: If the other program is not compatible for diffing
        """
        pass

    @abstractmethod
    def apply_diff(self, diff: DiffType) -> "IProgram":
        """
        Apply a diff to this program to create a new modified program.

        Args:
            diff: The diff structure to apply to this program

        Returns:
            A new program instance with the diff applied

        Raises:
            ValueError: If the diff cannot be applied to this program
            TypeError: If the diff is not in the expected format
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate that this program is well-formed and executable.

        Returns:
            True if the program is valid, False otherwise
        """
        pass

    @abstractmethod
    def clone(self) -> "IProgram":
        """
        Create a deep copy of this program.

        Returns:
            A new program instance with the same state
        """
        pass
