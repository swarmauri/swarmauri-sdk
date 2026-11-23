from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.prompt_templates.PromptTemplateBase import (
    PromptTemplateBase,
)


@ComponentBase.register_type(PromptTemplateBase, "PromptTemplate")
class PromptTemplate(PromptTemplateBase):
    type: Literal["PromptTemplate"] = "PromptTemplate"
