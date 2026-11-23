from contextlib import asynccontextmanager, contextmanager
from importlib.metadata import entry_points

import pytest
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

from swarmauri_llm_cloudflare import (
    CloudflareChatRetryPolicy,
    CloudflareWorkersAIModel,
    CloudflareWorkersAIToolModel,
)


class Response:
    def __init__(self, status_code=200, payload=None, headers=None):
        self.status_code = status_code
        self.payload = payload or {"result": [{"name": "@cf/model"}]}
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
def test_models_build_account_scoped_endpoints_without_network_on_init():
    model = CloudflareWorkersAIModel(
        account_id="acct", api_key="token", name="@cf/model"
    )
    tool_model = CloudflareWorkersAIToolModel(
        account_id="acct", api_key="token", name="@cf/tool-model"
    )

    expected = (
        "https://api.cloudflare.com/client/v4/accounts/acct/ai/v1/"
        "chat/completions"
    )
    assert isinstance(model, LLMBase)
    assert isinstance(tool_model, ToolLLMBase)
    assert model._build_endpoint() == expected
    assert tool_model._build_endpoint() == expected
    assert model.allowed_models == ["@cf/model"]
    assert "tools" in tool_model.capabilities


@pytest.mark.unit
def test_model_discovery_uses_injected_client():
    client = FakeClient()
    model = CloudflareWorkersAIModel(
        account_id="acct",
        api_key="token",
        name="@cf/default",
        discover_models=True,
        http_client=client,
    )
    assert model.allowed_models == ["@cf/model"]
    method, path, kwargs = client.requests[0]
    assert method == "GET"
    assert path.endswith("/ai/models/search")
    assert kwargs["headers"]["Authorization"] == "Bearer token"
    assert kwargs["params"]["task"] == "Text Generation"


@pytest.mark.unit
def test_rate_limited_chat_retries_through_injected_client():
    client = FakeClient(
        [
            Response(429, headers={"Retry-After": "0"}),
            Response(
                payload={
                    "choices": [{"message": {"content": "edge"}}],
                    "usage": {},
                }
            ),
        ]
    )
    model = CloudflareWorkersAIModel(
        account_id="acct",
        api_key="token",
        name="@cf/model",
        http_client=client,
        retry_policy=CloudflareChatRetryPolicy(max_attempts=2, base_delay=0),
    )
    conversation = Conversation(messages=[HumanMessage(content="hello")])

    model.predict(conversation)

    assert len(client.requests) == 2
    assert conversation.get_last().content == "edge"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_chat_uses_injected_client():
    client = FakeClient(
        [
            Response(
                payload={
                    "choices": [{"message": {"content": "async edge"}}],
                    "usage": {},
                }
            )
        ]
    )
    model = CloudflareWorkersAIModel(
        account_id="acct",
        api_key="token",
        name="@cf/model",
        http_client=client,
    )
    conversation = Conversation(messages=[HumanMessage(content="hello")])

    await model.apredict(conversation)

    assert client.requests[0][0] == "POST"
    assert conversation.get_last().content == "async edge"


@pytest.mark.unit
def test_credentials_are_not_serialized():
    model = CloudflareWorkersAIModel(
        account_id="acct", api_key="secret", name="@cf/model"
    )
    assert "secret" not in model.model_dump_json()


@pytest.mark.unit
def test_entry_points_are_registered():
    llms = {entry.name for entry in entry_points(group="swarmauri.llms")}
    tool_llms = {
        entry.name for entry in entry_points(group="swarmauri.tool_llms")
    }
    assert "CloudflareWorkersAIModel" in llms
    assert "CloudflareWorkersAIToolModel" in tool_llms
