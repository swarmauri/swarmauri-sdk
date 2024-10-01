from typing import List, Tuple, Optional, Any, Literal
from pydantic import Field, ConfigDict
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.prompts.IPromptMatrix import IPromptMatrix

class PromptMatrixBase(IPromptMatrix, ComponentBase):
    matrix: List[List[str]] = []
    resource: Optional[str] =  Field(default=ResourceTypes.PROMPT.value)
    type: Literal['PromptMatrixBase'] = 'PromptMatrixBase'    

    @property
    def shape(self) -> Tuple[int, int]:
        """Get the shape (number of agents, sequence length) of the prompt matrix."""
        if self.matrix:
            return len(self.matrix), len(self.matrix[0])
        return 0, 0

    def add_prompt_sequence(self, sequence: List[Optional[str]]) -> None:
        if not self.matrix or (self.matrix and len(sequence) == len(self.matrix[0])):
            self.matrix.append(sequence)
        else:
            raise ValueError("Sequence length does not match the prompt matrix dimensions.")

    def remove_prompt_sequence(self, index: int) -> None:
        if 0 <= index < len(self.matrix):
            self.matrix.pop(index)
        else:
            raise IndexError("Index out of range.")

    def get_prompt_sequence(self, index: int) -> List[Optional[str]]:
        if 0 <= index < len(self._matrix):
            return self.matrix[index]
        else:
            raise IndexError("Index out of range.")

    def show(self) -> List[List[Optional[str]]]:
        return self.matrix