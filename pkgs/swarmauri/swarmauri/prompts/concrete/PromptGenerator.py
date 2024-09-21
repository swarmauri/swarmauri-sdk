from typing import Literal
from swarmauri.standard.prompts.base.PromptGeneratorBase import PromptGeneratorBase

class PromptGenerator(PromptGeneratorBase):
    type: Literal['PromptGenerator'] = 'PromptGenerator'