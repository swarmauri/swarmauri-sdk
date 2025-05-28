from typing import List, Optional, Literal
from pydantic import Field
import random

from swarmauri_core.prompt_template_samplers.IPromptTemplateSampler import IPromptTemplateSampler
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.prompt_templates.PromptTemplateBase import PromptTemplateBase


@ComponentBase.register_model()
class PromptTemplateSamplerBase(IPromptTemplateSampler, ComponentBase):
    """Base class for sampling prompt templates."""

    templates: List[PromptTemplateBase] = []
    resource: Optional[str] = Field(default=ResourceTypes.PROMPT_TEMPLATE_SAMPLER.value, frozen=True)
    type: Literal["PromptTemplateSamplerBase"] = "PromptTemplateSamplerBase"

    def sample(self, **kwargs) -> Optional[PromptTemplateBase]:
        if not self.templates:
            return None
        return random.choice(self.templates)
