# swarmauri/standard/prompts/base/BasePromptMatrix.py
from typing import List, Tuple, Optional, Any
from swarmauri.core.prompts.IPromptMatrix import IPromptMatrix

class BasePromptMatrix(IPromptMatrix):
    def __init__(self, matrix: List[List[str]] = []):
        self._matrix = matrix

    @property
    def matrix(self) -> List[List[Optional[str]]]:
        return self._matrix

    @matrix.setter
    def matrix(self, value: List[List[Optional[str]]]) -> None:
        self._matrix = value

    @property
    def shape(self) -> Tuple[int, int]:
        """Get the shape (number of agents, sequence length) of the prompt matrix."""
        if self._matrix:
            return len(self._matrix), len(self._matrix[0])
        return 0, 0

    def add_prompt_sequence(self, sequence: List[Optional[str]]) -> None:
        if not self._matrix or (self._matrix and len(sequence) == len(self._matrix[0])):
            self._matrix.append(sequence)
        else:
            raise ValueError("Sequence length does not match the prompt matrix dimensions.")

    def remove_prompt_sequence(self, index: int) -> None:
        if 0 <= index < len(self._matrix):
            self._matrix.pop(index)
        else:
            raise IndexError("Index out of range.")

    def get_prompt_sequence(self, index: int) -> List[Optional[str]]:
        if 0 <= index < len(self._matrix):
            return self._matrix[index]
        else:
            raise IndexError("Index out of range.")

    def show(self) -> List[List[Optional[str]]]:
        return self._matrix