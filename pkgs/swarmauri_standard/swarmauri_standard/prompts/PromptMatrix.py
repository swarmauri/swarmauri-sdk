import warnings

from typing import Literal
from swarmauri_base.prompts.PromptMatrixBase import PromptMatrixBase
from swarmauri_base.ComponentBase import ComponentBase


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_type(PromptMatrixBase, "PromptMatrix")
class PromptMatrix(PromptMatrixBase):
    type: Literal["PromptMatrix"] = "PromptMatrix"
