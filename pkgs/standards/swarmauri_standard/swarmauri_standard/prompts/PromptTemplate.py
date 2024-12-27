from typing import Literal
from swarmauri_base.prompts.PromptTemplateBase import PromptTemplateBase

class PromptTemplate(PromptTemplateBase):
    type: Literal['PromptTemplate'] = 'PromptTemplate'