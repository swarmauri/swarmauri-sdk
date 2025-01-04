from typing import Literal
from swarmauri_base.prompts.PromptTemplateBase import PromptTemplateBase
from swarmauri_core.ComponentBase import ComponentBase

@ComponentBase.register_type(PromptTemplateBase, 'PromptTemplate')
class PromptTemplate(PromptTemplateBase):
    type: Literal['PromptTemplate'] = 'PromptTemplate'