from typing import Any, Callable, ClassVar, FrozenSet, List, Literal, Optional

import httpx
from pydantic import Field, PrivateAttr
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
class AzureOpenAIModel(LLMBase):
    """Provider-native Azure OpenAI chat-completions model."""

    type: Literal["AzureOpenAIModel"] = "AzureOpenAIModel"
    endpoint: str = Field(min_length=1)
    api_version: str = "v1"
    name: str = Field(min_length=1)
    discover_models: bool = False
    capabilities: ClassVar[FrozenSet[str]] = frozenset(
        {"chat_completions", "structured_output", "streaming", "tools"}
    )
    _token_provider: Optional[Callable[[], Any]] = PrivateAttr(default=None)

    predict = predict_chat
    apredict = apredict_chat
    stream = stream_chat
    astream = astream_chat
    batch = batch_chat
    abatch = abatch_chat

    def __init__(
        self,
        *,
        token_provider: Optional[Callable[[], Any]] = None,
        **data: Any,
    ) -> None:
        super().__init__(**data)
        self._token_provider = token_provider
        if self.api_key is None and self._token_provider is None:
            raise ValueError("api_key or token_provider is required")
        self.allowed_models = self.allowed_models or self._get_models()

    def _api_root(self) -> str:
        root = self.endpoint.rstrip("/")
        suffix = f"/openai/{self.api_version}"
        return root if root.endswith(suffix) else f"{root}{suffix}"

    def _build_endpoint(self) -> str:
        return f"{self._api_root()}/chat/completions"

    def _build_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key is not None:
            headers["api-key"] = self.api_key.get_secret_value()
        else:
            token = self._token_provider()
            headers["Authorization"] = (
                f"Bearer {getattr(token, 'token', token)}"
            )
        return headers

    def _get_models(self) -> List[str]:
        if not self.discover_models:
            return [self.name]
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self._api_root()}/models", headers=self._build_headers()
            )
            response.raise_for_status()
        return [
            item["id"]
            for item in response.json().get("data", [])
            if item.get("id")
        ]
