from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.prompts.PromptBase import PromptBase


@ComponentBase.register_type(PromptBase, "Prompt")
class Prompt(PromptBase):
    type: Literal["Prompt"] = "Prompt"
