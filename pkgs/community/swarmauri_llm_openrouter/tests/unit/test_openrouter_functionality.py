"""Exercise every public OpenRouter execution path with deterministic I/O."""

import base64
from collections import deque

import pytest
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.tools.CalculatorTool import CalculatorTool

from swarmauri_llm_openrouter import (
    OpenRouterImgGenModel,
    OpenRouterModel,
    OpenRouterToolModel,
    OpenRouterVLM,
)


class Response:
    """Provide the subset of the HTTP response contract used by the models."""

    def __init__(self, payload=None, content=b""):
        self.payload = payload or {}
        self.content = content

    def json(self):
        """Return the configured JSON body."""
        return self.payload


class QueueTransport:
    """Record requests while returning queued responses and stream events."""

    def __init__(self, payloads=(), stream_events=(), download=b"downloaded"):
        self.payloads = deque(payloads)
        self.stream_events = list(stream_events)
        self.download = download
        self.calls = []

    def request(self, method, path, *, json_data=None):
        self.calls.append((method, path, json_data))
        if method == "GET":
            return Response(content=self.download)
        return Response(self.payloads.popleft())

    async def arequest(self, method, path, *, json_data=None):
        return self.request(method, path, json_data=json_data)

    def stream(self, path, payload):
        self.calls.append(("STREAM", path, payload))
        yield from self.stream_events

    async def astream(self, path, payload):
        for event in self.stream(path, payload):
            yield event


def conversation(content="hello"):
    """Build an isolated conversation for a model invocation."""
    item = Conversation()
    item.add_message(HumanMessage(content=content))
    return item


def chat_response(content="answer"):
    """Build a normalized OpenRouter chat response."""
    return {"choices": [{"message": {"content": content}}]}


def tool_response():
    """Build a request to execute the standard calculator tool."""
    return {
        "choices": [
            {
                "message": {
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call-1",
                            "type": "function",
                            "function": {
                                "name": "CalculatorTool",
                                "arguments": (
                                    '{"operation":"add","x":2,"y":3}'
                                ),
                            },
                        }
                    ],
                }
            }
        ]
    }


def toolkit():
    """Return a toolkit containing a deterministic local calculator."""
    value = Toolkit()
    value.add_tool(CalculatorTool())
    return value


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llm_async_stream_and_batch_paths():
    model = OpenRouterModel(api_key="key", allowed_models=["*"])
    model._transport = QueueTransport(
        payloads=[chat_response("async")],
        stream_events=[
            {"choices": [{"delta": {"content": "a"}}]},
            {"choices": [{"delta": {"content": "sync"}}]},
        ],
    )
    item = await model.apredict(conversation(), temperature=0)
    assert item.get_last().content == "async"
    streamed = conversation()
    assert [part async for part in model.astream(streamed)] == ["a", "sync"]
    assert streamed.get_last().content == "async"

    model._transport = QueueTransport(
        payloads=[chat_response("one"), chat_response("two")]
    )
    assert [
        item.get_last().content
        for item in model.batch([conversation(), conversation()])
    ] == ["one", "two"]

    model._transport = QueueTransport(
        payloads=[chat_response("three"), chat_response("four")]
    )
    results = await model.abatch([conversation(), conversation()])
    assert sorted(item.get_last().content for item in results) == [
        "four",
        "three",
    ]


@pytest.mark.unit
def test_tool_model_executes_local_tool_and_completes_round_trip():
    model = OpenRouterToolModel(api_key="key", allowed_models=["*"])
    model._transport = QueueTransport(
        payloads=[tool_response(), chat_response("The answer is 5.")]
    )
    result = model.predict(conversation(), toolkit())
    assert result.get_last().content == "The answer is 5."
    assert result.history[-2].role == "tool"
    assert '"calculated_result": "5"' in result.history[-2].content
    assert model._transport.calls[0][2]["tools"][0]["type"] == "function"
    assert (
        model._transport.calls[1][2]["messages"][-1]["tool_call_id"]
        == "call-1"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_tool_model_async_stream_and_batch_paths():
    model = OpenRouterToolModel(api_key="key", allowed_models=["*"])
    model._transport = QueueTransport(
        payloads=[tool_response(), chat_response("async tool")]
    )
    result = await model.apredict(conversation(), toolkit())
    assert result.get_last().content == "async tool"
    assert result.history[-2].role == "tool"

    model._transport = QueueTransport(
        payloads=[tool_response()],
        stream_events=[{"choices": [{"delta": {"content": "streamed"}}]}],
    )
    streamed = conversation()
    assert [part async for part in model.astream(streamed, toolkit())] == [
        "streamed"
    ]
    assert streamed.get_last().content == "streamed"

    model._transport = QueueTransport(
        payloads=[chat_response("one"), chat_response("two")]
    )
    assert [
        item.get_last().content
        for item in model.batch([conversation(), conversation()], toolkit=None)
    ] == ["one", "two"]

    model._transport = QueueTransport(
        payloads=[chat_response("three"), chat_response("four")]
    )
    results = await model.abatch(
        [conversation(), conversation()], toolkit=None
    )
    assert sorted(item.get_last().content for item in results) == [
        "four",
        "three",
    ]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_vlm_sync_async_and_batch_paths_preserve_multimodal_content():
    multimodal = [
        {"type": "text", "text": "describe"},
        {
            "type": "image_url",
            "image_url": {"url": "data:image/png;base64,AA=="},
        },
    ]
    model = OpenRouterVLM(api_key="key", allowed_models=["*"])
    model._transport = QueueTransport(payloads=[chat_response("seen")])
    result = await model.apredict_vision(conversation(multimodal))
    assert result.get_last().content == "seen"
    assert model._transport.calls[0][2]["messages"][0]["content"] == multimodal

    model._transport = QueueTransport(
        payloads=[chat_response("one"), chat_response("two")]
    )
    assert [
        item.get_last().content
        for item in model.batch(
            [conversation(multimodal), conversation(multimodal)]
        )
    ] == ["one", "two"]

    model._transport = QueueTransport(
        payloads=[chat_response("three"), chat_response("four")]
    )
    results = await model.abatch(
        [conversation(multimodal), conversation(multimodal)]
    )
    assert sorted(item.get_last().content for item in results) == [
        "four",
        "three",
    ]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_image_generation_sync_async_batch_multiple_and_url_paths():
    encoded = base64.b64encode(b"image").decode()
    model = OpenRouterImgGenModel(api_key="key", allowed_models=["*"])
    model._transport = QueueTransport(
        payloads=[{"data": [{"b64_json": encoded}, {"url": "https://image"}]}]
    )
    assert model.generate_image("tiger") == [b"image", b"downloaded"]

    model._transport = QueueTransport(payloads=[{"data": [{"b64": encoded}]}])
    assert await model.agenerate_image("tiger") == b"image"

    model._transport = QueueTransport(
        payloads=[{"data": [{"b64": encoded}]}, {"data": [{"b64": encoded}]}]
    )
    assert model.batch_generate(["one", "two"]) == [b"image", b"image"]

    model._transport = QueueTransport(
        payloads=[{"data": [{"b64": encoded}]}, {"data": [{"b64": encoded}]}]
    )
    assert await model.abatch_generate(["one", "two"]) == [b"image", b"image"]
