from typing import Literal
from swarmauri.prompts.base.PromptGeneratorBase import PromptGeneratorBase

class PromptGenerator(PromptGeneratorBase):
    type: Literal['PromptGenerator'] = 'PromptGenerator'