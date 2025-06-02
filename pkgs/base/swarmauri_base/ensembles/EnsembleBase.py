from typing import Any, Dict, Optional, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_core.ensembles.IEnsemble import IEnsemble


@ComponentBase.register_model()
class EnsembleBase(IEnsemble, ComponentBase):
    """Base implementation for routing prompts to multiple LLMs."""

    resource: Optional[str] = Field(default=ResourceTypes.ENSEMBLE.value)
    type: Literal["EnsembleBase"] = "EnsembleBase"

    llms: Dict[str, LLMBase] = Field(default_factory=dict)

    def add_model(self, name: str, model: LLMBase) -> None:
        if name in self.llms:
            raise ValueError(f"Model '{name}' already exists")
        self.llms[name] = model

    def remove_model(self, name: str) -> bool:
        removed = name in self.llms
        if removed:
            self.llms.pop(name)
        return removed

    def list_models(self) -> Dict[str, LLMBase]:
        return self.llms

    def route_by_provider(self, provider: str, prompt: str, **kwargs: Any) -> Any:
        llm = self.llms.get(provider)
        if not llm:
            raise ValueError(f"Provider '{provider}' not found")
        return llm.predict(prompt, **kwargs)

    async def aroute_by_provider(
        self, provider: str, prompt: str, **kwargs: Any
    ) -> Any:
        llm = self.llms.get(provider)
        if not llm:
            raise ValueError(f"Provider '{provider}' not found")
        return await llm.apredict(prompt, **kwargs)

    def _choose_provider(self) -> Optional[str]:
        return next(iter(self.llms), None)

    def route(self, prompt: str, **kwargs: Any) -> Any:
        provider = self._choose_provider()
        if provider is None:
            return None
        return self.route_by_provider(provider, prompt, **kwargs)

    async def aroute(self, prompt: str, **kwargs: Any) -> Any:
        provider = self._choose_provider()
        if provider is None:
            return None
        return await self.aroute_by_provider(provider, prompt, **kwargs)

    def broadcast(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        return {name: llm.predict(prompt, **kwargs) for name, llm in self.llms.items()}

    async def abroadcast(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        responses: Dict[str, Any] = {}
        for name, llm in self.llms.items():
            responses[name] = await llm.apredict(prompt, **kwargs)
        return responses
