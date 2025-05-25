from random import choice
from typing import Any, Dict, List, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.prompt_templates.PromptTemplateBase import PromptTemplateBase


@ComponentBase.register_type(PromptTemplateBase, "PromptTemplateSampler")
class PromptTemplateSampler(PromptTemplateBase):
    """Select a random template and render it with provided variables."""

    templates: List[str] = Field(default_factory=list)
    resource: str = Field(default=ResourceTypes.PROMPT.value, frozen=True)
    type: Literal["PromptTemplateSampler"] = "PromptTemplateSampler"

    def sample(self, variables: Dict[str, Any] | None = None) -> str:
        if not self.templates:
            return ""
        self.set_template(choice(self.templates))
        return self.fill(variables or {})

    def __call__(self, variables: Dict[str, Any] | None = None) -> str:
        return self.sample(variables)
