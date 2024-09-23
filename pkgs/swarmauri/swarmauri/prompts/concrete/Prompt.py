from typing import Literal
from swarmauri.prompts.base.PromptBase import PromptBase

class Prompt(PromptBase):
    type: Literal['Prompt'] = 'Prompt'