from typing import Literal
from swarmauri.standard.prompts.base.PromptTemplateBase import PromptTemplateBase

class PromptTemplate(PromptTemplateBase):
    type: Literal['PromptTemplate'] = 'PromptTemplate'