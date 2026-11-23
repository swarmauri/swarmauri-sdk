from typing import Any, ClassVar, Literal

from pydantic import Field, PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_core.transports.i_http_retry_policy import IHttpRetryPolicy
from swarmauri_core.transports.i_managed_http_client import IManagedHttpClient
from swarmauri_standard.schema_converters.OpenAISchemaConverter import (
    OpenAISchemaConverter,
)
from swarmauri_standard.utils.provider_chat_transport import (
    abatch_tools,
    apredict_tools,
    astream_tools,
    batch_tools,
    format_messages,
    predict_tools,
    stream_tools,
)

from ._client import build_cloudflare_client


@ComponentBase.register_type()
class CloudflareWorkersAIToolModel(ToolLLMBase):
    """Tool-calling adapter for Cloudflare Workers AI."""

    type: Literal["CloudflareWorkersAIToolModel"] = (
        "CloudflareWorkersAIToolModel"
    )
    account_id: str = Field(min_length=1)
    name: str = "@cf/openai/gpt-oss-20b"
    base_url: str = "https://api.cloudflare.com/client/v4"
    discover_models: bool = False
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"chat_completions", "streaming", "tools"}
    )
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
        http_client: IHttpClient | None = None,
        retry_policy: IHttpRetryPolicy | None = None,
        **data: Any,
    ) -> None:
        selected_name = data.get(
            "name", self.__class__.model_fields["name"].default
        )
        data.setdefault("allowed_models", [selected_name])
        super().__init__(**data)
        self._http_client = build_cloudflare_client(
            base_url=self.base_url,
            timeout=self.timeout,
            max_attempts=self.max_retries,
            http_client=http_client,
            retry_policy=retry_policy,
        )
        if self.discover_models:
            self.allowed_models = self._get_models()

    def get_schema_converter(self):
        return OpenAISchemaConverter()

    def _format_messages(self, messages):
        return format_messages(messages)

    def _account_root(self) -> str:
        return f"{self.base_url.rstrip('/')}/accounts/{self.account_id}/ai"

    def _build_endpoint(self) -> str:
        return f"{self._account_root()}/v1/chat/completions"

    def _build_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key is not None:
            headers["Authorization"] = (
                f"Bearer {self.api_key.get_secret_value()}"
            )
        return headers

    def _get_models(self) -> list[str]:
        if not self.discover_models:
            return [self.name] if self.name else []
        response = self._http_client.request(
            "GET",
            f"{self._account_root()}/models/search",
            headers=self._build_headers(),
            params={"task": "Text Generation", "per_page": 100},
        )
        response.raise_for_status()
        result: list[dict[str, Any]] = response.json().get("result") or []
        return [
            model_name
            for model in result
            if (model_name := model.get("name") or model.get("id"))
        ]

    def close(self) -> None:
        if isinstance(self._http_client, IManagedHttpClient):
            self._http_client.close()

    async def aclose(self) -> None:
        if isinstance(self._http_client, IManagedHttpClient):
            await self._http_client.aclose()
