from typing import Literal
from swarmauri.prompts.base.PromptTemplateBase import PromptTemplateBase

class PromptTemplate(PromptTemplateBase):
    type: Literal['PromptTemplate'] = 'PromptTemplate'