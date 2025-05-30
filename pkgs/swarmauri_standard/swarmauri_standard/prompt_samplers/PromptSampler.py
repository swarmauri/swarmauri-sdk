from typing import Literal, Sequence, Optional
import random

from swarmauri_base.prompt_samplers.PromptSamplerBase import PromptSamplerBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(PromptSamplerBase, "PromptSampler")
class PromptSampler(PromptSamplerBase):
    """Sample a random prompt from a sequence."""

    type: Literal["PromptSampler"] = "PromptSampler"

    def sample(self, prompts: Optional[Sequence[str]] = None) -> str:
        prompts = list(prompts) if prompts is not None else list(self.prompts or [])
        return random.choice(prompts) if prompts else ""
