from typing import List, Optional, Literal
import random
from pydantic import Field

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
        """Return a random template from the sampler."""
        if not self.templates:
            return None
        return random.choice(self.templates)

    def add_template(self, template: PromptTemplateBase) -> None:
        """Add a single prompt template to the sampler."""
        self.templates.append(template)

    def add_templates(self, templates: List[PromptTemplateBase]) -> None:
        """Add multiple prompt templates to the sampler."""
        self.templates.extend(templates)

    def remove_template(self, index: int) -> None:
        """Remove the prompt template at the specified index."""
        if 0 <= index < len(self.templates):
            self.templates.pop(index)
        else:
            raise IndexError("Index out of range.")

    def clear_templates(self) -> None:
        """Delete all prompt templates from the sampler."""
        self.templates = []
