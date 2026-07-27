from typing import Any, ClassVar, FrozenSet, List, Literal, Optional

from pydantic import Field
from swarmauri_provider_xai import XAIProvider
from swarmauri_transport_httpx import HttpxClient
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_standard.utils.provider_chat_transport import (
    abatch_chat,
    apredict_chat,
    astream_chat,
    batch_chat,
    predict_chat,
    stream_chat,
)


@ComponentBase.register_type()
class XAIModel(LLMBase):
    """Provider-native xAI chat-completions model."""

    type: Literal["XAIModel"] = "XAIModel"
    base_url: str = "https://api.x.ai/v1"
    name: str = "grok-4.3"
    discover_models: bool = False
    provider: Optional[XAIProvider] = None
    http_client: Any = Field(default_factory=HttpxClient, exclude=True)
    capabilities: ClassVar[FrozenSet[str]] = frozenset(
        {"chat_completions", "multimodal_input", "streaming", "tools"}
    )

    predict = predict_chat
    apredict = apredict_chat
    stream = stream_chat
    astream = astream_chat
    batch = batch_chat
    abatch = abatch_chat

    def __init__(self, **data: Any) -> None:
        provider = data.get("provider")
        if isinstance(provider, XAIProvider):
            data.setdefault("api_key", provider.api_key)
            data.setdefault("base_url", provider.base_url)
        selected_name = data.get(
            "name", self.__class__.model_fields["name"].default
        )
        data.setdefault("allowed_models", [selected_name])
        super().__init__(**data)
        self.http_client.base_url = self.base_url
        self.http_client.timeout = self.timeout
        if self.api_key is None:
            raise ValueError("api_key is required")
        self.allowed_models = self.allowed_models or self._get_models()

    def _build_endpoint(self) -> str:
        return f"{self.base_url.rstrip('/')}/chat/completions"

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

    def _get_models(self) -> List[str]:
        if not self.discover_models:
            return [self.name]
        response = self.http_client.request(
            "GET",
            f"{self.base_url.rstrip('/')}/language-models",
            headers=self._build_headers(),
        )
        response.raise_for_status()
        return [
            item["id"]
            for item in response.json().get("models", [])
            if item.get("id")
        ]
