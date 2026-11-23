"""Test OpenRouter family conformance and provider/transport composition."""

import base64
import json
from collections import deque
from contextlib import asynccontextmanager, contextmanager
from importlib.metadata import entry_points

import pytest
from swarmauri_base.image_gens.ImageGenBase import ImageGenBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_base.vlms.VLMBase import VLMBase
from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_provider_openrouter import (
    OpenRouterProvider,
    OpenRouterProviderPreferences,
)
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

from swarmauri_llm_openrouter import (
    OpenRouterImgGenModel,
    OpenRouterModel,
    OpenRouterRetryPolicy,
    OpenRouterToolModel,
    OpenRouterVLM,
)


class Response:
    def __init__(
        self,
        payload=None,
        *,
        content=b"",
        status_code=200,
        headers=None,
        events=(),
    ):
        self.payload = payload or {}
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
        self.events = list(events)

    def read(self):
        return self.content

    async def aread(self):
        return self.content

    def json(self):
        return self.payload

    def raise_for_status(self):
        return None

    def iter_lines(self):
        for event in self.events:
            yield f"data: {json.dumps(event)}"
        yield "data: [DONE]"

    async def aiter_lines(self):
        for line in self.iter_lines():
            yield line


class QueueClient(IHttpClient):
    def __init__(self, responses=(), *, events=(), download=b"downloaded"):
        self.responses = deque(responses)
        self.events = list(events)
        self.download = download
        self.calls = []

    def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        if self.responses:
            return self.responses.popleft()
        return Response(content=self.download)

    async def arequest(self, method, path, **kwargs):
        return self.request(method, path, **kwargs)

    @contextmanager
    def stream(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        yield Response(events=self.events)

    @asynccontextmanager
    async def astream(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        yield Response(events=self.events)


def conversation(content="hello"):
    result = Conversation()
    result.add_message(HumanMessage(content=content))
    return result


@pytest.mark.unit
def test_empty_allowlist_denies_model_construction():
    with pytest.raises(ValueError, match="openrouter/auto"):
        OpenRouterModel(api_key="key")


@pytest.mark.unit
def test_exact_and_glob_policies_are_inherited_from_base():
    exact = OpenRouterModel(
        api_key="key",
        name="anthropic/claude-sonnet-4",
        allowed_models=["anthropic/claude-sonnet-4"],
    )
    globbed = OpenRouterModel(
        api_key="key",
        name="anthropic/claude-opus-4",
        allowed_models=["anthropic/**"],
    )
    assert exact.name == "anthropic/claude-sonnet-4"
    assert globbed.name == "anthropic/claude-opus-4"
    with pytest.raises(ValueError, match="openai/gpt-4o"):
        OpenRouterModel(
            api_key="key",
            name="openai/gpt-4o",
            allowed_models=["anthropic/**"],
        )


@pytest.mark.unit
def test_provider_catalog_is_refreshed_by_injected_model_client():
    client = QueueClient(
        [
            Response(
                {
                    "data": [
                        {"id": "anthropic/claude"},
                        {"id": "openai/gpt-4o"},
                    ]
                }
            )
        ]
    )
    provider = OpenRouterProvider(api_key="provider-key")
    model = OpenRouterModel(
        provider=provider,
        http_client=client,
        allowed_models=["*"],
    )

    model.refresh_catalog()

    assert model.catalog.list_model_ids() == [
        "anthropic/claude",
        "openai/gpt-4o",
    ]
    assert client.calls[0][1] == "https://openrouter.ai/api/v1/models"
    assert client.calls[0][2]["headers"]["Authorization"] == (
        "Bearer provider-key"
    )


@pytest.mark.unit
def test_family_inheritance_resources_and_provider_authentication():
    provider = OpenRouterProvider(api_key="provider-key")
    instances = [
        (
            OpenRouterModel(provider=provider, allowed_models=["*"]),
            LLMBase,
            "LLM",
        ),
        (
            OpenRouterToolModel(provider=provider, allowed_models=["*"]),
            ToolLLMBase,
            "ToolLLM",
        ),
        (
            OpenRouterVLM(provider=provider, allowed_models=["*"]),
            VLMBase,
            "VLM",
        ),
        (
            OpenRouterImgGenModel(provider=provider, allowed_models=["*"]),
            ImageGenBase,
            "ImageGen",
        ),
    ]
    for instance, parent, resource in instances:
        assert isinstance(instance, parent)
        assert instance.resource == resource
        assert "provider-key" not in instance.model_dump_json()


@pytest.mark.unit
def test_chat_payload_routing_response_and_headers():
    client = QueueClient(
        [
            Response(
                {
                    "choices": [{"message": {"content": "answer"}}],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 2},
                }
            )
        ]
    )
    model = OpenRouterModel(
        provider=OpenRouterProvider(
            api_key="key",
            app_name="app",
            site_url="https://example.com",
        ),
        routing=OpenRouterProviderPreferences(order=["OpenAI"]),
        http_client=client,
        allowed_models=["*"],
    )

    result = model.predict(conversation(), temperature=0)

    sent = client.calls[0][2]
    assert result.get_last().content == "answer"
    assert sent["json"]["temperature"] == 0
    assert sent["json"]["provider"]["order"] == ["OpenAI"]
    assert sent["headers"]["X-OpenRouter-Title"] == "app"
    assert sent["headers"]["HTTP-Referer"] == "https://example.com"


@pytest.mark.unit
def test_chat_stream_uses_injected_client_and_appends_complete_message():
    client = QueueClient(
        events=[
            {"choices": [{"delta": {"content": "hel"}}]},
            {"choices": [{"delta": {"content": "lo"}}]},
        ]
    )
    model = OpenRouterModel(
        api_key="key", allowed_models=["*"], http_client=client
    )
    item = conversation()

    assert "".join(model.stream(item)) == "hello"
    assert item.get_last().content == "hello"
    assert client.calls[0][0] == "POST"


@pytest.mark.unit
def test_vision_preserves_structured_content():
    client = QueueClient(
        [Response({"choices": [{"message": {"content": "seen"}}]})]
    )
    model = OpenRouterVLM(
        api_key="key", allowed_models=["*"], http_client=client
    )
    item = conversation(
        [
            {"type": "text", "text": "describe"},
            {
                "type": "image_url",
                "image_url": {"url": "https://x.test/a.png"},
            },
        ]
    )

    model.predict_vision(item)

    sent = client.calls[0][2]["json"]["messages"][0]["content"]
    assert sent[1]["type"] == "image_url"


@pytest.mark.unit
def test_image_generation_decodes_base64_and_downloads_urls():
    client = QueueClient(
        [
            Response(
                {
                    "data": [
                        {"b64_json": base64.b64encode(b"image").decode()},
                        {"url": "https://image.test/output"},
                    ]
                }
            )
        ],
        download=b"downloaded",
    )
    model = OpenRouterImgGenModel(
        api_key="key", allowed_models=["*"], http_client=client
    )

    assert model.generate_image("tiger") == [b"image", b"downloaded"]
    assert client.calls[1][1] == "https://image.test/output"


@pytest.mark.unit
def test_rate_limited_submission_retries_without_replaying_server_errors():
    client = QueueClient(
        [
            Response(status_code=429, headers={"Retry-After": "0"}),
            Response({"choices": [{"message": {"content": "recovered"}}]}),
        ]
    )
    model = OpenRouterModel(
        api_key="key",
        allowed_models=["*"],
        http_client=client,
        retry_policy=OpenRouterRetryPolicy(max_attempts=2, base_delay=0),
    )

    result = model.predict(conversation())

    assert result.get_last().content == "recovered"
    assert len(client.calls) == 2


@pytest.mark.unit
def test_installed_entry_points_load_public_classes():
    expected = {
        "swarmauri.llms": "OpenRouterModel",
        "swarmauri.tool_llms": "OpenRouterToolModel",
        "swarmauri.vlms": "OpenRouterVLM",
        "swarmauri.image_gens": "OpenRouterImgGenModel",
    }
    for group, name in expected.items():
        matches = [ep for ep in entry_points(group=group) if ep.name == name]
        assert len(matches) == 1
        assert matches[0].load().__name__ == name
