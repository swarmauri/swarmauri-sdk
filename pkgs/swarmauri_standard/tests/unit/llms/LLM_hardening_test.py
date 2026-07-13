import json

import httpx
import pytest

from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.llms.LLM import LLM
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.HumanMessage import HumanMessage


def _llm(**overrides):
    values = {
        "api_key": "secret",
        "BASE_URL": "https://provider.test/v1/chat/completions",
        "name": "provider-model",
        "allowed_models": ["provider-model"],
        "retry_delay": 0,
    }
    values.update(overrides)
    return LLM(**values)


def test_formats_assistant_history_without_reusing_previous_message():
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="question"))
    conversation.add_message(AgentMessage(content="answer"))

    formatted = _llm()._format_messages(conversation.history)

    assert formatted == [
        {"content": "question", "role": "user"},
        {"content": "answer", "role": "assistant"},
    ]


def test_provider_hooks_and_capabilities_are_not_serialized():
    class ProviderLLM(LLM):
        capabilities = frozenset({"chat_completions"})

        def _build_headers(self):
            return {"X-Provider-Key": self.api_key.get_secret_value()}

        def _build_endpoint(self):
            return "https://override.test/chat"

    llm = ProviderLLM(
        **_llm().model_dump(exclude={"type"}), api_key="secret"
    )

    assert llm._build_endpoint() == "https://override.test/chat"
    assert llm._build_headers() == {"X-Provider-Key": "secret"}
    serialized = llm.model_dump()
    assert "_headers" not in serialized
    assert "capabilities" not in serialized
    assert "api_key" not in serialized
    assert "secret" not in llm.model_dump_json()


def test_model_name_is_allowed_when_provider_discovers_models_later():
    llm = LLM(
        api_key="secret",
        BASE_URL="https://provider.test/v1/chat/completions",
        name="runtime-model",
    )

    assert llm.name == "runtime-model"
    assert llm.allowed_models == []


def test_payload_and_stream_parser_are_provider_override_points():
    llm = _llm()
    payload = llm._build_payload(
        [{"role": "user", "content": "hello"}],
        temperature=0.2,
        max_tokens=10,
        top_p=0.9,
        enable_json=True,
        stop=None,
        stream=True,
    )

    assert payload["response_format"] == {"type": "json_object"}
    assert payload["stream_options"] == {"include_usage": True}
    content, usage = llm._parse_stream_chunk(
        "data: "
        + json.dumps(
            {
                "choices": [{"delta": {"content": "token"}}],
                "usage": {"total_tokens": 3},
            }
        )
    )
    assert content == "token"
    assert usage == {"total_tokens": 3}
    assert llm._parse_stream_chunk("data: [DONE]") == (None, {})


def test_predict_uses_configurable_retry_statuses(monkeypatch):
    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(503, request=request)
        return httpx.Response(
            200,
            request=request,
            json={
                "choices": [{"message": {"content": "ok"}}],
                "usage": {},
            },
        )

    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    def client_factory(**kwargs):
        return original_client(transport=transport, **kwargs)

    monkeypatch.setattr(
        "swarmauri_standard.llms.LLM.httpx.Client", client_factory
    )
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="hello"))

    result = _llm(max_retries=2).predict(conversation)

    assert attempts == 2
    assert result.get_last().content == "ok"


def test_stream_uses_streaming_transport(monkeypatch):
    request_body = None

    def handler(request):
        nonlocal request_body
        request_body = json.loads(request.content)
        events = (
            'data: {"choices":[{"delta":{"content":"a"}}]}\n\n'
            'data: {"choices":[{"delta":{"content":"b"}}]}\n\n'
            "data: [DONE]\n\n"
        )
        return httpx.Response(200, request=request, text=events)

    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    def client_factory(**kwargs):
        return original_client(transport=transport, **kwargs)

    monkeypatch.setattr(
        "swarmauri_standard.llms.LLM.httpx.Client", client_factory
    )
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="hello"))

    assert list(_llm().stream(conversation)) == ["a", "b"]
    assert request_body["stream"] is True
    assert conversation.get_last().content == "ab"


@pytest.mark.asyncio
async def test_astream_uses_streaming_transport(monkeypatch):
    def handler(request):
        events = (
            'data: {"choices":[{"delta":{"content":"async"}}]}\n\n'
            "data: [DONE]\n\n"
        )
        return httpx.Response(200, request=request, text=events)

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    def client_factory(**kwargs):
        return original_client(transport=transport, **kwargs)

    monkeypatch.setattr(
        "swarmauri_standard.llms.LLM.httpx.AsyncClient", client_factory
    )
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="hello"))

    chunks = [chunk async for chunk in _llm().astream(conversation)]

    assert chunks == ["async"]
    assert conversation.get_last().content == "async"
