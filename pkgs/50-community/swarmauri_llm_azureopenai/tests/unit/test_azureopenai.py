from contextlib import asynccontextmanager, contextmanager
from importlib.metadata import entry_points

import pytest
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

from swarmauri_llm_azureopenai import (
    AzureOpenAIChatRetryPolicy,
    AzureOpenAIModel,
    AzureOpenAIToolModel,
)


class Response:
    def __init__(self, status_code=200, payload=None, headers=None):
        self.status_code = status_code
        self.payload = payload or {"data": [{"id": "deployment"}]}
        self.headers = headers or {}

    def read(self):
        return b"{}"

    async def aread(self):
        return self.read()

    def json(self):
        return self.payload

    def raise_for_status(self):
        return None


class FakeClient(IHttpClient):
    def __init__(self, responses=None):
        self.requests = []
        self.responses = iter(responses or [Response()])

    def request(self, method, path, **kwargs):
        self.requests.append((method, path, kwargs))
        return next(self.responses)

    async def arequest(self, method, path, **kwargs):
        return self.request(method, path, **kwargs)

    @contextmanager
    def stream(self, method, path, **kwargs):
        yield self.request(method, path, **kwargs)

    @asynccontextmanager
    async def astream(self, method, path, **kwargs):
        yield await self.arequest(method, path, **kwargs)


@pytest.mark.unit
def test_models_directly_use_base_contracts_and_v1_endpoint():
    model = AzureOpenAIModel(
        endpoint="https://resource.openai.azure.com",
        api_key="key",
        name="deployment",
    )
    tool_model = AzureOpenAIToolModel(
        endpoint="https://resource.openai.azure.com/openai/v1",
        api_key="key",
        name="deployment",
    )
    assert isinstance(model, LLMBase)
    assert isinstance(tool_model, ToolLLMBase)
    assert model._build_endpoint().endswith("/openai/v1/chat/completions")
    assert tool_model._build_headers()["api-key"] == "key"


@pytest.mark.unit
def test_entra_provider_refreshes_and_is_not_serialized():
    tokens = iter(["token-1", "token-2"])
    model = AzureOpenAIModel(
        endpoint="https://resource.openai.azure.com",
        token_provider=lambda: next(tokens),
        name="deployment",
    )
    assert model._build_headers()["Authorization"] == "Bearer token-1"
    assert model._build_headers()["Authorization"] == "Bearer token-2"
    serialized = model.model_dump_json()
    assert "token_provider" not in serialized
    assert "token-" not in serialized


@pytest.mark.unit
def test_model_discovery_uses_injected_client():
    client = FakeClient()
    model = AzureOpenAIModel(
        endpoint="https://resource.openai.azure.com",
        api_key="key",
        name="deployment",
        discover_models=True,
        http_client=client,
    )
    assert model.allowed_models == ["deployment"]
    assert client.requests[0][1].endswith("/openai/v1/models")
    assert client.requests[0][2]["headers"]["api-key"] == "key"


@pytest.mark.unit
def test_rate_limited_chat_retries_through_injected_client():
    client = FakeClient(
        [
            Response(429, headers={"Retry-After": "0"}),
            Response(
                payload={
                    "choices": [{"message": {"content": "recovered"}}],
                    "usage": {},
                }
            ),
        ]
    )
    model = AzureOpenAIModel(
        endpoint="https://resource.openai.azure.com",
        api_key="key",
        name="deployment",
        http_client=client,
        retry_policy=AzureOpenAIChatRetryPolicy(max_attempts=2, base_delay=0),
    )
    conversation = Conversation(messages=[HumanMessage(content="hello")])

    model.predict(conversation)

    assert len(client.requests) == 2
    assert conversation.get_last().content == "recovered"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_chat_uses_injected_client():
    client = FakeClient(
        [
            Response(
                payload={
                    "choices": [{"message": {"content": "async"}}],
                    "usage": {},
                }
            )
        ]
    )
    model = AzureOpenAIModel(
        endpoint="https://resource.openai.azure.com",
        api_key="key",
        name="deployment",
        http_client=client,
    )
    conversation = Conversation(messages=[HumanMessage(content="hello")])

    await model.apredict(conversation)

    assert client.requests[0][0] == "POST"
    assert conversation.get_last().content == "async"


@pytest.mark.unit
def test_entry_points_are_registered():
    assert "AzureOpenAIModel" in {
        entry.name for entry in entry_points(group="swarmauri.llms")
    }
    assert "AzureOpenAIToolModel" in {
        entry.name for entry in entry_points(group="swarmauri.tool_llms")
    }
