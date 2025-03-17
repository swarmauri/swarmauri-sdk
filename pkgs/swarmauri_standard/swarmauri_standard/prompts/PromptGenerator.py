from typing import Literal
from swarmauri_base.prompts.PromptGeneratorBase import PromptGeneratorBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(PromptGeneratorBase, "PromptGenerator")
class PromptGenerator(PromptGeneratorBase):
    type: Literal["PromptGenerator"] = "PromptGenerator"
