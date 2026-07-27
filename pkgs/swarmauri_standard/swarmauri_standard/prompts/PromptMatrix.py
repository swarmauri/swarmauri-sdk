from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.prompts.PromptMatrixBase import PromptMatrixBase


@ComponentBase.register_type(PromptMatrixBase, "PromptMatrix")
class PromptMatrix(PromptMatrixBase):
    type: Literal["PromptMatrix"] = "PromptMatrix"
