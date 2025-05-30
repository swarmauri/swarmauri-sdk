from typing import Sequence, Optional, List, Literal
from pydantic import Field

from swarmauri_core.prompt_samplers.IPromptSampler import IPromptSampler
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class PromptSamplerBase(IPromptSampler, ComponentBase):
    """Abstract base class for prompt samplers."""

    prompts: Optional[List[str]] = None
    resource: Optional[str] = Field(default=ResourceTypes.PROMPT_SAMPLER.value, frozen=True)
    type: Literal["PromptSamplerBase"] = "PromptSamplerBase"

    def sample(self, prompts: Optional[Sequence[str]] = None) -> str:  # pragma: no cover - base method
        raise NotImplementedError

    def set_prompts(self, prompts: Sequence[str]) -> None:
        self.prompts = list(prompts)

    def add_prompt(self, prompt: str) -> None:
        if self.prompts is None:
            self.prompts = [prompt]
        else:
            self.prompts.append(prompt)

    def add_prompts(self, prompts: Sequence[str]) -> None:
        if self.prompts is None:
            self.prompts = list(prompts)
        else:
            self.prompts.extend(prompts)

    def remove_prompt(self, prompt: str) -> None:
        if not self.prompts:
            raise ValueError("No prompts stored.")
        try:
            self.prompts.remove(prompt)
        except ValueError as exc:
            raise ValueError(f"Prompt '{prompt}' not found.") from exc

    def clear_prompts(self) -> None:
        self.prompts = None

    def show(self) -> Sequence[str]:
        return self.prompts or []
