from typing import Literal

from pydantic import Field
from swarmauri_core.prompts.IPromptMatrix import IPromptMatrix

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


class PromptMatrixBase(IPromptMatrix, ComponentBase):
    matrix: list[list[str]] = []
    resource: str | None = Field(default=ResourceTypes.PROMPT.value)
    type: Literal["PromptMatrixBase"] = "PromptMatrixBase"

    @property
    def shape(self) -> tuple[int, int]:
        """Get the shape (number of agents, sequence length) of the prompt
        matrix."""
        if self.matrix:
            return len(self.matrix), len(self.matrix[0])
        return 0, 0

    def add_prompt_sequence(self, sequence: list[str | None]) -> None:
        if not self.matrix or (
            self.matrix and len(sequence) == len(self.matrix[0])
        ):
            self.matrix.append(sequence)
        else:
            raise ValueError(
                "Sequence length does not match the prompt matrix dimensions."
            )

    def remove_prompt_sequence(self, index: int) -> None:
        if 0 <= index < len(self.matrix):
            self.matrix.pop(index)
        else:
            raise IndexError("Index out of range.")

    def get_prompt_sequence(self, index: int) -> list[str | None]:
        if 0 <= index < len(self._matrix):
            return self.matrix[index]
        else:
            raise IndexError("Index out of range.")

    def show(self) -> list[list[str | None]]:
        return self.matrix
