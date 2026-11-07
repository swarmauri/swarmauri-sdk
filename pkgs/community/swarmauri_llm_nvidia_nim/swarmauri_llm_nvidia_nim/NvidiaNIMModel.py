from typing import Any, ClassVar, Literal

from pydantic import PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_core.transports.i_http_retry_policy import IHttpRetryPolicy
from swarmauri_core.transports.i_managed_http_client import IManagedHttpClient
from swarmauri_standard.utils.provider_chat_transport import (
    abatch_chat,
    apredict_chat,
    astream_chat,
    batch_chat,
    predict_chat,
    stream_chat,
)

from ._client import build_nvidia_nim_client


@ComponentBase.register_type()
class NvidiaNIMModel(LLMBase):
    """Chat adapter for an NVIDIA NIM for LLMs deployment."""

    type: Literal["NvidiaNIMModel"] = "NvidiaNIMModel"
    base_url: str = "http://localhost:8000"
    name: str = "meta/llama-3.1-8b-instruct"
    discover_models: bool = False
    capabilities: ClassVar[frozenset[str]] = frozenset(
        {"chat_completions", "structured_output", "streaming", "tools"}
    )
    _http_client: IHttpClient = PrivateAttr()
    _retry_owned_by_transport: bool = PrivateAttr(default=True)

    predict = predict_chat
    apredict = apredict_chat
    stream = stream_chat
    astream = astream_chat
    batch = batch_chat
    abatch = abatch_chat

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
        self._http_client = build_nvidia_nim_client(
            base_url=self.base_url,
            timeout=self.timeout,
            max_attempts=self.max_retries,
            http_client=http_client,
            retry_policy=retry_policy,
        )
        if self.discover_models:
            self.allowed_models = self._get_models()

    def _api_root(self) -> str:
        root = self.base_url.rstrip("/")
        return root if root.endswith("/v1") else f"{root}/v1"

    def _build_endpoint(self) -> str:
        return f"{self._api_root()}/chat/completions"

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
            f"{self._api_root()}/models",
            headers=self._build_headers(),
        )
        response.raise_for_status()
        data: list[dict[str, Any]] = response.json().get("data") or []
        return [model["id"] for model in data if model.get("id")]

    def close(self) -> None:
        if isinstance(self._http_client, IManagedHttpClient):
            self._http_client.close()

    async def aclose(self) -> None:
        if isinstance(self._http_client, IManagedHttpClient):
            await self._http_client.aclose()
