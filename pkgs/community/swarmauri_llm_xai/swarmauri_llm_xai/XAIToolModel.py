from typing import Any, ClassVar, Literal

from pydantic import PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_core.transports.i_http_retry_policy import IHttpRetryPolicy
from swarmauri_provider_xai import XAIProvider, XAIToolSchemaConverter
from swarmauri_standard.utils.provider_chat_transport import (
    abatch_tools,
    apredict_tools,
    astream_tools,
    batch_tools,
    format_messages,
    predict_tools,
    stream_tools,
)

from ._client import build_xai_client


@ComponentBase.register_type()
class XAIToolModel(ToolLLMBase):
    """Provider-native xAI tool-calling model."""

    type: Literal["XAIToolModel"] = "XAIToolModel"
    base_url: str = "https://api.x.ai/v1"
    name: str = "grok-4.3"
    discover_models: bool = False
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"chat_completions", "streaming", "tools"}
    )
    _provider: XAIProvider = PrivateAttr()
    _http_client: IHttpClient = PrivateAttr()
    _retry_owned_by_transport: bool = PrivateAttr(default=True)

    predict = predict_tools
    apredict = apredict_tools
    stream = stream_tools
    astream = astream_tools
    batch = batch_tools
    abatch = abatch_tools

    def __init__(
        self,
        *,
        provider: XAIProvider | None = None,
        http_client: IHttpClient | None = None,
        retry_policy: IHttpRetryPolicy | None = None,
        **data: Any,
    ) -> None:
        selected_name = data.get(
            "name", self.__class__.model_fields["name"].default
        )
        data.setdefault("allowed_models", [selected_name])
        super().__init__(**data)
        if self.api_key is None:
            if provider is None or provider.api_key is None:
                raise ValueError(
                    "api_key or an authenticated provider is required"
                )
        self._provider = provider or XAIProvider(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )
        self.base_url = self._provider.base_url or self.base_url
        self._http_client = build_xai_client(
            provider=self._provider,
            http_client=http_client,
            retry_policy=retry_policy,
        )
        if self.discover_models:
            self.allowed_models = self._get_models()
        elif not self.allowed_models:
            self.allowed_models = [self.name]

    def get_schema_converter(self):
        return XAIToolSchemaConverter()

    def _format_messages(self, messages):
        return format_messages(messages)

    def _build_endpoint(self) -> str:
        config = self._provider.connection_config(
            "chat.completions", model=self.name
        )
        return str(config.endpoint)

    def _build_headers(self) -> dict[str, str]:
        config = self._provider.connection_config(
            "chat.completions", model=self.name
        )
        return self._provider.authorize(config)

    def _get_models(self) -> list[str]:
        if not self.discover_models:
            return [self.name]
        config = self._provider.connection_config("models.list")
        response = self._http_client.request(
            "GET",
            str(config.endpoint),
            headers=self._provider.authorize(config),
        )
        response.raise_for_status()
        return [
            item["id"]
            for item in response.json().get("models", [])
            if item.get("id")
        ]
