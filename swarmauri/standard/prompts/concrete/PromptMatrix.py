from typing import Literal
from swarmauri.standard.prompts.base.PromptMatrixBase import PromptMatrixBase

class PromptMatrix(PromptMatrixBase):
    type: Literal['PromptMatrix'] = 'PromptMatrix'