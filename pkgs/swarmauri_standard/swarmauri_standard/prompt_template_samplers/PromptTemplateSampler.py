from typing import Literal

from swarmauri_base.prompt_template_samplers.PromptTemplateSamplerBase import PromptTemplateSamplerBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(PromptTemplateSamplerBase, "PromptTemplateSampler")
class PromptTemplateSampler(PromptTemplateSamplerBase):
    type: Literal["PromptTemplateSampler"] = "PromptTemplateSampler"
