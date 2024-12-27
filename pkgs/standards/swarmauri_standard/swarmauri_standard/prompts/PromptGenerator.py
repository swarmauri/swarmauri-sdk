from typing import Literal
from swarmauri_base.prompts.PromptGeneratorBase import PromptGeneratorBase

class PromptGenerator(PromptGeneratorBase):
    type: Literal['PromptGenerator'] = 'PromptGenerator'