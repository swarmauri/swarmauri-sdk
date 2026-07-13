from types import SimpleNamespace

import httpx
import pytest

from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.FunctionMessage import FunctionMessage
from swarmauri_standard.utils.provider_chat_transport import (
    apredict_chat,
    astream_chat,
    predict_chat,
    predict_tools,
    stream_chat,
)


def _model():
    return SimpleNamespace(
        name="model",
        include_usage=True,
        timeout=1,
        max_retries=1,
        retry_delay=0,
        retryable_status_codes={429, 500},
        _build_endpoint=lambda: "https://provider.test/v1/chat/completions",
        _build_headers=lambda: {"Authorization": "Bearer secret"},
    )


@pytest.mark.unit
def test_predict_and_stream_use_provider_hooks(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer secret"
        body = request.read().decode()
        if '"stream":true' in body:
            return httpx.Response(
                200,
                text=(
                    'data: {"choices":[{"delta":{"content":"hel"}}]}\n\n'
                    'data: {"choices":[{"delta":{"content":"lo"}}]}\n\n'
                    "data: [DONE]\n\n"
                ),
            )
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "hello"}}],
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "total_tokens": 2,
                },
            },
        )

    original_client = httpx.Client
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(handler), **kwargs
        ),
    )
    conversation = Conversation(messages=[HumanMessage(content="hi")])
    predict_chat(_model(), conversation)
    assert conversation.get_last().content == "hello"

    streaming = Conversation(messages=[HumanMessage(content="hi")])
    assert "".join(stream_chat(_model(), streaming)) == "hello"
    assert streaming.get_last().content == "hello"


@pytest.mark.unit
def test_tool_round_trip_records_function_history(monkeypatch):
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "call-1",
                                        "type": "function",
                                        "function": {
                                            "name": "double",
                                            "arguments": '{"value": 4}',
                                        },
                                    }
                                ],
                            }
                        }
                    ]
                },
            )
        assert '"role":"tool"' in request.read().decode()
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "8"}}]}
        )

    original_client = httpx.Client
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(handler), **kwargs
        ),
    )
    model = _model()
    model._schema_convert_tools = lambda tools: []
    toolkit = SimpleNamespace(
        tools={"double": object()},
        get_tool_by_name=lambda name: lambda value: value * 2,
    )
    conversation = Conversation(messages=[HumanMessage(content="double 4")])

    predict_tools(model, conversation, toolkit)

    assert calls == 2
    assert isinstance(conversation.history[-2], FunctionMessage)
    assert conversation.history[-2].role == "tool"
    assert conversation.get_last().content == "8"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_async_predict_and_stream_use_provider_hooks(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if '"stream":true' in request.read().decode():
            return httpx.Response(
                200,
                text=(
                    'data: {"choices":[{"delta":{"content":"ok"}}]}\n\n'
                    "data: [DONE]\n\n"
                ),
            )
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "ok"}}]},
        )

    original_client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(handler), **kwargs
        ),
    )
    conversation = Conversation(messages=[HumanMessage(content="hi")])
    await apredict_chat(_model(), conversation)
    assert conversation.get_last().content == "ok"

    streaming = Conversation(messages=[HumanMessage(content="hi")])
    chunks = [chunk async for chunk in astream_chat(_model(), streaming)]
    assert chunks == ["ok"]
    assert streaming.get_last().content == "ok"
