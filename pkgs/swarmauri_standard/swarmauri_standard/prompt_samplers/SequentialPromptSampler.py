from typing import Literal, Sequence

from swarmauri_base.prompt_samplers.PromptSamplerBase import PromptSamplerBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(PromptSamplerBase, "SequentialPromptSampler")
class SequentialPromptSampler(PromptSamplerBase):
    """Cycle through prompts sequentially."""

    type: Literal["SequentialPromptSampler"] = "SequentialPromptSampler"
    index: int = 0

    def sample(self, prompts: Sequence[str], *args, **kwargs) -> str:
        if not prompts:
            return ""
        prompt = prompts[self.index % len(prompts)]
        self.index += 1
        return prompt
