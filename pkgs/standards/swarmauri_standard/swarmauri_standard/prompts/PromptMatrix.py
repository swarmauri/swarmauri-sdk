from typing import Literal
from swarmauri_base.prompts.PromptMatrixBase import PromptMatrixBase

class PromptMatrix(PromptMatrixBase):
    type: Literal['PromptMatrix'] = 'PromptMatrix'