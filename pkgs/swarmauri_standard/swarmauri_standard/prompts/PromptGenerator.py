from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.prompts.PromptGeneratorBase import PromptGeneratorBase


@ComponentBase.register_type(PromptGeneratorBase, "PromptGenerator")
class PromptGenerator(PromptGeneratorBase):
    type: Literal["PromptGenerator"] = "PromptGenerator"
