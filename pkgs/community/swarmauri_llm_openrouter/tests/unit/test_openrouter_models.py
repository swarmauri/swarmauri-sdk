"""Test OpenRouter family conformance and request behavior."""

import base64
from importlib.metadata import entry_points

import pytest
from swarmauri_base.image_gens.ImageGenBase import ImageGenBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_base.vlms.VLMBase import VLMBase
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

from swarmauri_llm_openrouter import (
    OpenRouterImgGenModel,
    OpenRouterModel,
    OpenRouterModelCatalog,
    OpenRouterToolModel,
    OpenRouterVLM,
)


class Response:
    """Provide the response surface used by model tests."""

    content = b""

    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


class Transport:
    """Record requests and return deterministic provider responses."""

    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def request(self, method, path, *, json_data=None):
        self.calls.append((method, path, json_data))
        return Response(self.payload)

    async def arequest(self, method, path, *, json_data=None):
        return self.request(method, path, json_data=json_data)

    def stream(self, path, payload):
        self.calls.append(("STREAM", path, payload))
        yield {"choices": [{"delta": {"content": "hel"}}]}
        yield {"choices": [{"delta": {"content": "lo"}}]}

    async def astream(self, path, payload):
        for event in self.stream(path, payload):
            yield event


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
def test_catalog_ids_can_configure_a_concrete_policy():
    discovery = OpenRouterModel(api_key="key", allowed_models=["*"])
    discovery._transport = Transport(
        {"data": [{"id": "anthropic/claude"}, {"id": "openai/gpt-4o"}]}
    )
    available = discovery.catalog.list_model_ids()
    configured = OpenRouterModel(
        api_key="key",
        name="openai/gpt-4o",
        allowed_models=available,
    )
    assert configured.allowed_models == ["anthropic/claude", "openai/gpt-4o"]


@pytest.mark.unit
def test_standalone_catalog_can_run_before_model_construction():
    catalog = OpenRouterModelCatalog.from_api_key(
        "key",
        app_name="app",
        site_url="https://example.com",
    )
    assert catalog._transport.headers["Authorization"] == "Bearer key"
    assert catalog._transport.headers["X-OpenRouter-Title"] == "app"
    assert catalog._transport.headers["HTTP-Referer"] == "https://example.com"


@pytest.mark.unit
def test_family_inheritance_and_resources():
    instances = [
        (OpenRouterModel(api_key="key", allowed_models=["*"]), LLMBase, "LLM"),
        (
            OpenRouterToolModel(api_key="key", allowed_models=["*"]),
            ToolLLMBase,
            "ToolLLM",
        ),
        (OpenRouterVLM(api_key="key", allowed_models=["*"]), VLMBase, "VLM"),
        (
            OpenRouterImgGenModel(api_key="key", allowed_models=["*"]),
            ImageGenBase,
            "ImageGen",
        ),
    ]
    for instance, parent, resource in instances:
        assert isinstance(instance, parent)
        assert instance.resource == resource
        assert "api_key" not in instance.model_dump_json()


@pytest.mark.unit
def test_chat_payload_response_and_headers():
    model = OpenRouterModel(
        api_key="key",
        allowed_models=["*"],
        app_name="app",
        site_url="https://example.com",
    )
    transport = Transport(
        {
            "choices": [{"message": {"content": "answer"}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 2},
        }
    )
    model._transport = transport
    result = model.predict(conversation(), temperature=0)
    assert result.get_last().content == "answer"
    assert transport.calls[0][2]["temperature"] == 0
    assert model._request_headers()["X-OpenRouter-Title"] == "app"
    assert model._request_headers()["HTTP-Referer"] == "https://example.com"


@pytest.mark.unit
def test_chat_stream_appends_complete_message():
    model = OpenRouterModel(api_key="key", allowed_models=["*"])
    model._transport = Transport({})
    item = conversation()
    assert "".join(model.stream(item)) == "hello"
    assert item.get_last().content == "hello"


@pytest.mark.unit
def test_vision_preserves_structured_content():
    model = OpenRouterVLM(api_key="key", allowed_models=["*"])
    transport = Transport({"choices": [{"message": {"content": "seen"}}]})
    model._transport = transport
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
    sent = transport.calls[0][2]["messages"][0]["content"]
    assert sent[1]["type"] == "image_url"


@pytest.mark.unit
def test_image_generation_decodes_base64():
    model = OpenRouterImgGenModel(api_key="key", allowed_models=["*"])
    model._transport = Transport(
        {"data": [{"b64_json": base64.b64encode(b"image").decode()}]}
    )
    assert model.generate_image("tiger", size="1K") == b"image"


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
