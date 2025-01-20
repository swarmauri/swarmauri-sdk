from typing import Literal
from swarmauri_base.prompts.PromptBase import PromptBase
from swarmauri_core.ComponentBase import ComponentBase

@ComponentBase.register_type(PromptBase, 'Prompt')
class Prompt(PromptBase):
    type: Literal['Prompt'] = 'Prompt'