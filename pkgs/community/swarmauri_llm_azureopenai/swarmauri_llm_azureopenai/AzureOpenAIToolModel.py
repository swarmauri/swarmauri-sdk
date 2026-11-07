from typing import Any, Callable, ClassVar, FrozenSet, List, Literal, Optional

from pydantic import Field, PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_core.transports.i_http_retry_policy import IHttpRetryPolicy
from swarmauri_core.transports.i_managed_http_client import IManagedHttpClient
from swarmauri_standard.schema_converters.OpenAISchemaConverter import (
    OpenAISchemaConverter,
)

from ._client import build_azure_openai_client
from swarmauri_standard.utils.provider_chat_transport import (
    abatch_tools,
    apredict_tools,
    astream_tools,
    batch_tools,
    format_messages,
    predict_tools,
    stream_tools,
)


@ComponentBase.register_type()
class AzureOpenAIToolModel(ToolLLMBase):
    """Provider-native Azure OpenAI tool-calling model."""

    type: Literal["AzureOpenAIToolModel"] = "AzureOpenAIToolModel"
    endpoint: str = Field(min_length=1)
    api_version: str = "v1"
    name: str = Field(min_length=1)
    discover_models: bool = False
    capabilities: ClassVar[FrozenSet[str]] = frozenset(
        {"chat_completions", "streaming", "tools"}
    )
    _token_provider: Optional[Callable[[], Any]] = PrivateAttr(default=None)
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
        token_provider: Optional[Callable[[], Any]] = None,
        http_client: IHttpClient | None = None,
        retry_policy: IHttpRetryPolicy | None = None,
        **data: Any,
    ) -> None:
        selected_name = data.get("name")
        if selected_name:
            data.setdefault("allowed_models", [selected_name])
        super().__init__(**data)
        self._token_provider = token_provider
        if self.api_key is None and self._token_provider is None:
            raise ValueError("api_key or token_provider is required")
        self._http_client = build_azure_openai_client(
            base_url=self._api_root(),
            timeout=self.timeout,
            max_attempts=self.max_retries,
            http_client=http_client,
            retry_policy=retry_policy,
        )
        if self.discover_models:
            self.allowed_models = self._get_models()
        elif not self.allowed_models:
            self.allowed_models = [self.name]

    def get_schema_converter(self):
        return OpenAISchemaConverter()

    def _format_messages(self, messages):
        return format_messages(messages)

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
        response = self._http_client.request(
            "GET",
            f"{self._api_root()}/models",
            headers=self._build_headers(),
        )
        response.raise_for_status()
        return [
            item["id"]
            for item in response.json().get("data", [])
            if item.get("id")
        ]

    def close(self) -> None:
        if isinstance(self._http_client, IManagedHttpClient):
            self._http_client.close()

    async def aclose(self) -> None:
        if isinstance(self._http_client, IManagedHttpClient):
            await self._http_client.aclose()
