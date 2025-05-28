import random
from typing import Literal, Sequence, Optional

from swarmauri_base.prompt_samplers.PromptSamplerBase import PromptSamplerBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(PromptSamplerBase, "WeightedPromptSampler")
class WeightedPromptSampler(PromptSamplerBase):
    """Sample prompts using optional weights."""

    type: Literal["WeightedPromptSampler"] = "WeightedPromptSampler"

    def sample(
        self,
        prompts: Sequence[str],
        *,
        weights: Optional[Sequence[float]] = None,
        **kwargs,
    ) -> str:
        if not prompts:
            return ""
        return random.choices(list(prompts), weights=weights, k=1)[0]
