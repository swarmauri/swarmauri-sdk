from typing import Literal
from swarmauri_base.prompts.PromptMatrixBase import PromptMatrixBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(PromptMatrixBase, "PromptMatrix")
class PromptMatrix(PromptMatrixBase):
    type: Literal["PromptMatrix"] = "PromptMatrix"
