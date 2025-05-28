from typing import Optional, Literal
from pydantic import Field

from swarmauri_core.prompt_samplers.IPromptSampler import IPromptSampler
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class PromptSamplerBase(IPromptSampler, ComponentBase):
    """Abstract base class for prompt samplers."""

    resource: Optional[str] = Field(default=ResourceTypes.PROMPT_SAMPLER.value, frozen=True)
    type: Literal["PromptSamplerBase"] = "PromptSamplerBase"

    def sample(self, *args, **kwargs) -> str:  # pragma: no cover - base method
        raise NotImplementedError
