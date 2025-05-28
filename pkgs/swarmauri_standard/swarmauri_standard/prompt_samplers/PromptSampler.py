from typing import Literal, Sequence
import random

from swarmauri_base.prompt_samplers.PromptSamplerBase import PromptSamplerBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(PromptSamplerBase, "PromptSampler")
class PromptSampler(PromptSamplerBase):
    """Sample a random prompt from a sequence."""

    type: Literal["PromptSampler"] = "PromptSampler"

    def sample(self, prompts: Sequence[str], *args, **kwargs) -> str:
        return random.choice(list(prompts)) if prompts else ""
