from typing import Literal
from swarmauri_base.prompt_templates.PromptTemplateBase import PromptTemplateBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(PromptTemplateBase, "PromptTemplate")
class PromptTemplate(PromptTemplateBase):
    type: Literal["PromptTemplate"] = "PromptTemplate"
