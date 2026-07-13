from typing import Any, ClassVar, FrozenSet, List, Literal

import httpx
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_standard.llms.LLM import LLM


@ComponentBase.register_type()
class CloudflareWorkersAIModel(LLM):
    """Chat adapter for Cloudflare Workers AI."""

    type: Literal["CloudflareWorkersAIModel"] = "CloudflareWorkersAIModel"
    account_id: str = Field(min_length=1)
    name: str = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
    base_url: str = "https://api.cloudflare.com/client/v4"
    discover_models: bool = False
    capabilities: ClassVar[FrozenSet[str]] = LLM.capabilities | {"tools"}

    def _account_root(self) -> str:
        return f"{self.base_url.rstrip('/')}/accounts/{self.account_id}/ai"

    def _build_endpoint(self) -> str:
        return f"{self._account_root()}/v1/chat/completions"

    def _get_models(self) -> List[str]:
        if not self.discover_models:
            return [self.name] if self.name else []
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self._account_root()}/models/search",
                headers=self._build_headers(),
                params={"task": "Text Generation", "per_page": 100},
            )
            response.raise_for_status()
        result: List[dict[str, Any]] = response.json().get("result") or []
        return [
            model_name
            for model in result
            if (model_name := model.get("name") or model.get("id"))
        ]
