from typing import Any, ClassVar, FrozenSet, List, Literal

import httpx
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_standard.tool_llms.ToolLLM import ToolLLM


@ComponentBase.register_type()
class NvidiaNIMToolModel(ToolLLM):
    """Tool-calling adapter for an NVIDIA NIM for LLMs deployment."""

    type: Literal["NvidiaNIMToolModel"] = "NvidiaNIMToolModel"
    base_url: str = "http://localhost:8000"
    name: str = "meta/llama-3.1-8b-instruct"
    discover_models: bool = False
    capabilities: ClassVar[FrozenSet[str]] = ToolLLM.capabilities

    def _api_root(self) -> str:
        root = self.base_url.rstrip("/")
        return root if root.endswith("/v1") else f"{root}/v1"

    def _build_endpoint(self) -> str:
        return f"{self._api_root()}/chat/completions"

    def _get_models(self) -> List[str]:
        if not self.discover_models:
            return [self.name] if self.name else []
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self._api_root()}/models", headers=self._build_headers()
            )
            response.raise_for_status()
        data: List[dict[str, Any]] = response.json().get("data") or []
        return [model["id"] for model in data if model.get("id")]
