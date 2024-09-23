from typing import Literal
from swarmauri.prompts.base.PromptMatrixBase import PromptMatrixBase

class PromptMatrix(PromptMatrixBase):
    type: Literal['PromptMatrix'] = 'PromptMatrix'