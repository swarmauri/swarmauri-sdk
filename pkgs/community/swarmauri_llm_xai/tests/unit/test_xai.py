from importlib.metadata import entry_points
from contextlib import asynccontextmanager, contextmanager

import pytest
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_provider_xai import XAIProvider
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

from swarmauri_llm_xai import XAIChatRetryPolicy, XAIModel, XAIToolModel


class Response:
    def __init__(self, status_code=200, payload=None, headers=None):
        self.status_code = status_code
        self.payload = payload or {"models": [{"id": "grok-discovered"}]}
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
def test_models_directly_use_base_contracts():
    model = XAIModel(api_key="key")
    tool_model = XAIToolModel(api_key="key")
    assert isinstance(model, LLMBase)
    assert isinstance(tool_model, ToolLLMBase)
    assert model._build_endpoint() == "https://api.x.ai/v1/chat/completions"
    assert tool_model._build_headers()["Authorization"] == "Bearer key"


@pytest.mark.unit
def test_credentials_are_not_serialized():
    model = XAIModel(api_key="secret")
    serialized = model.model_dump_json()
    assert "api_key" not in serialized
    assert "secret" not in serialized


@pytest.mark.unit
def test_explicit_provider_and_client_drive_model_discovery():
    client = FakeClient()
    provider = XAIProvider(api_key="provider-secret")
    model = XAIModel(
        provider=provider,
        http_client=client,
        discover_models=True,
        name="grok-discovered",
    )

    assert model.allowed_models == ["grok-discovered"]
    assert client.requests[0][1] == "https://api.x.ai/v1/language-models"
    assert (
        client.requests[0][2]["headers"]["Authorization"]
        == "Bearer provider-secret"
    )


@pytest.mark.unit
def test_concrete_xai_policy_retries_rate_limited_chat_once():
    client = FakeClient(
        [
            Response(429, headers={"Retry-After": "0"}),
            Response(
                200,
                payload={
                    "choices": [{"message": {"content": "recovered"}}],
                    "usage": {},
                },
            ),
        ]
    )
    model = XAIModel(
        provider=XAIProvider(api_key="provider-secret"),
        http_client=client,
        retry_policy=XAIChatRetryPolicy(max_attempts=2, base_delay=0),
    )
    conversation = Conversation(messages=[HumanMessage(content="hello")])

    model.predict(conversation)

    assert len(client.requests) == 2
    assert conversation.get_last().content == "recovered"


@pytest.mark.unit
def test_entry_points_are_registered():
    assert "XAIModel" in {
        entry.name for entry in entry_points(group="swarmauri.llms")
    }
    assert "XAIToolModel" in {
        entry.name for entry in entry_points(group="swarmauri.tool_llms")
    }
