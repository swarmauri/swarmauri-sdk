from random import choices, choice
from typing import List, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_type(ComponentBase, "PromptSampler")
class PromptSampler(ComponentBase):
    """Randomly sample prompts from a provided list."""

    prompts: List[str] = Field(default_factory=list)
    resource: str = Field(default=ResourceTypes.PROMPT.value, frozen=True)
    type: Literal["PromptSampler"] = "PromptSampler"

    def sample(self, count: int = 1) -> List[str]:
        """Return ``count`` random prompts."""
        if not self.prompts or count <= 0:
            return []
        if count == 1:
            return [choice(self.prompts)]
        return choices(self.prompts, k=count)

    def __call__(self, count: int = 1) -> List[str]:
        return self.sample(count)
