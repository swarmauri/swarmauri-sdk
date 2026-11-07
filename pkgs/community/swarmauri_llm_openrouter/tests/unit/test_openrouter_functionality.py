"""Exercise every public OpenRouter execution path with deterministic I/O."""

import base64
import json
from collections import deque
from contextlib import asynccontextmanager, contextmanager

import pytest
from swarmauri_core.transports.i_http_client import IHttpClient
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
    def __init__(self, payload=None, *, content=b"", events=()):
        self.payload = payload or {}
        self.content = content
        self.events = list(events)
        self.status_code = 200
        self.headers = {}

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
    def __init__(self, payloads=(), stream_events=(), download=b"downloaded"):
        self.responses = deque(Response(payload) for payload in payloads)
        self.stream_events = list(stream_events)
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
        yield Response(events=self.stream_events)

    @asynccontextmanager
    async def astream(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        yield Response(events=self.stream_events)


def conversation(content="hello"):
    item = Conversation()
    item.add_message(HumanMessage(content=content))
    return item


def chat_response(content="answer"):
    return {"choices": [{"message": {"content": content}}]}


def tool_response():
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
    value = Toolkit()
    value.add_tool(CalculatorTool())
    return value


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llm_async_stream_and_batch_paths():
    client = QueueClient(
        payloads=[chat_response("async")],
        stream_events=[
            {"choices": [{"delta": {"content": "a"}}]},
            {"choices": [{"delta": {"content": "sync"}}]},
        ],
    )
    model = OpenRouterModel(
        api_key="key", allowed_models=["*"], http_client=client
    )
    item = await model.apredict(conversation(), temperature=0)
    assert item.get_last().content == "async"
    streamed = conversation()
    assert [part async for part in model.astream(streamed)] == ["a", "sync"]
    assert streamed.get_last().content == "async"

    client = QueueClient(payloads=[chat_response("one"), chat_response("two")])
    model = OpenRouterModel(
        api_key="key", allowed_models=["*"], http_client=client
    )
    assert [
        item.get_last().content
        for item in model.batch([conversation(), conversation()])
    ] == ["one", "two"]

    client = QueueClient(
        payloads=[chat_response("three"), chat_response("four")]
    )
    model = OpenRouterModel(
        api_key="key", allowed_models=["*"], http_client=client
    )
    results = await model.abatch([conversation(), conversation()])
    assert sorted(item.get_last().content for item in results) == [
        "four",
        "three",
    ]


@pytest.mark.unit
def test_tool_model_executes_local_tool_and_completes_round_trip():
    client = QueueClient(
        payloads=[tool_response(), chat_response("The answer is 5.")]
    )
    model = OpenRouterToolModel(
        api_key="key", allowed_models=["*"], http_client=client
    )
    result = model.predict(conversation(), toolkit())
    assert result.get_last().content == "The answer is 5."
    assert result.history[-2].role == "tool"
    assert '"calculated_result": "5"' in result.history[-2].content
    tool_schema = client.calls[0][2]["json"]["tools"][0]
    assert tool_schema["type"] == "function"
    assert tool_schema["function"]["name"] == "CalculatorTool"
    assert (
        client.calls[1][2]["json"]["messages"][-1]["tool_call_id"] == "call-1"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_tool_model_async_stream_and_batch_paths():
    client = QueueClient(
        payloads=[tool_response(), chat_response("async tool")]
    )
    model = OpenRouterToolModel(
        api_key="key", allowed_models=["*"], http_client=client
    )
    result = await model.apredict(conversation(), toolkit())
    assert result.get_last().content == "async tool"
    assert result.history[-2].role == "tool"

    client = QueueClient(
        payloads=[tool_response()],
        stream_events=[{"choices": [{"delta": {"content": "streamed"}}]}],
    )
    model = OpenRouterToolModel(
        api_key="key", allowed_models=["*"], http_client=client
    )
    streamed = conversation()
    assert [part async for part in model.astream(streamed, toolkit())] == [
        "streamed"
    ]
    assert streamed.get_last().content == "streamed"

    client = QueueClient(payloads=[chat_response("one"), chat_response("two")])
    model = OpenRouterToolModel(
        api_key="key", allowed_models=["*"], http_client=client
    )
    assert [
        item.get_last().content
        for item in model.batch([conversation(), conversation()], toolkit=None)
    ] == ["one", "two"]

    client = QueueClient(
        payloads=[chat_response("three"), chat_response("four")]
    )
    model = OpenRouterToolModel(
        api_key="key", allowed_models=["*"], http_client=client
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
    client = QueueClient(payloads=[chat_response("seen")])
    model = OpenRouterVLM(
        api_key="key", allowed_models=["*"], http_client=client
    )
    result = await model.apredict_vision(conversation(multimodal))
    assert result.get_last().content == "seen"
    assert client.calls[0][2]["json"]["messages"][0]["content"] == multimodal

    client = QueueClient(payloads=[chat_response("one"), chat_response("two")])
    model = OpenRouterVLM(
        api_key="key", allowed_models=["*"], http_client=client
    )
    assert [
        item.get_last().content
        for item in model.batch(
            [conversation(multimodal), conversation(multimodal)]
        )
    ] == ["one", "two"]

    client = QueueClient(
        payloads=[chat_response("three"), chat_response("four")]
    )
    model = OpenRouterVLM(
        api_key="key", allowed_models=["*"], http_client=client
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
    client = QueueClient(
        payloads=[{"data": [{"b64_json": encoded}, {"url": "https://image"}]}]
    )
    model = OpenRouterImgGenModel(
        api_key="key", allowed_models=["*"], http_client=client
    )
    assert model.generate_image("tiger") == [b"image", b"downloaded"]

    client = QueueClient(payloads=[{"data": [{"b64": encoded}]}])
    model = OpenRouterImgGenModel(
        api_key="key", allowed_models=["*"], http_client=client
    )
    assert await model.agenerate_image("tiger") == b"image"

    client = QueueClient(
        payloads=[{"data": [{"b64": encoded}]}, {"data": [{"b64": encoded}]}]
    )
    model = OpenRouterImgGenModel(
        api_key="key", allowed_models=["*"], http_client=client
    )
    assert model.batch_generate(["one", "two"]) == [b"image", b"image"]

    client = QueueClient(
        payloads=[{"data": [{"b64": encoded}]}, {"data": [{"b64": encoded}]}]
    )
    model = OpenRouterImgGenModel(
        api_key="key", allowed_models=["*"], http_client=client
    )
    assert await model.abatch_generate(["one", "two"]) == [b"image", b"image"]
