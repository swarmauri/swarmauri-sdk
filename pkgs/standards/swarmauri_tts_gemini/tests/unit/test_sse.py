import base64
import json
import httpx
import pytest
from swarmauri_tts_gemini import GeminiTTS

pytestmark = pytest.mark.unit


def event(audio):
    return (
        "data: "
        + json.dumps(
            {
                "event_type": "step.delta",
                "delta": {
                    "type": "audio",
                    "mime_type": "audio/l16",
                    "data": base64.b64encode(audio).decode(),
                },
            }
        )
        + "\n\n"
    ).encode()


DONE = b'data: {"event_type":"interaction.completed"}\n\n'


class EventStream(httpx.SyncByteStream, httpx.AsyncByteStream):
    def __init__(self, chunks):
        self.chunks = chunks
        self.read_count = 0
        self.closed = False

    def __iter__(self):
        for chunk in self.chunks:
            assert not self.closed
            self.read_count += 1
            yield chunk

    async def __aiter__(self):
        for chunk in self:
            yield chunk

    def close(self):
        self.closed = True

    async def aclose(self):
        self.close()


@pytest.fixture
def mock_sse(monkeypatch):
    real_sync, real_async = httpx.Client, httpx.AsyncClient

    def install(chunks):
        stream = EventStream(chunks)
        requests = []

        def respond(request):
            requests.append(request)
            return httpx.Response(
                200,
                stream=stream,
                headers={"content-type": "text/event-stream; charset=utf-8"},
            )

        transport = httpx.MockTransport(respond)
        monkeypatch.setattr(
            httpx, "Client", lambda **kw: real_sync(transport=transport, **kw)
        )
        monkeypatch.setattr(
            httpx,
            "AsyncClient",
            lambda **kw: real_async(transport=transport, **kw),
        )
        return stream, requests

    return install


def test_fragmented_sse_decodes_and_stops_at_completion(mock_sse):
    first = event(b"first")
    audio, requests = mock_sse(
        [
            b": ping\n\n",
            first[:9],
            first[9:],
            event(b"second"),
            DONE,
            event(b"unreachable"),
        ]
    )
    stream = GeminiTTS(api_key="offline-key").stream("hello")
    assert next(stream) == b"first"
    assert audio.read_count == 3
    assert not audio.closed
    assert b"".join(stream) == b"second"
    assert audio.closed
    assert audio.read_count == 5
    payload = json.loads(requests[0].content)
    assert payload["stream"] is True
    assert payload["store"] is False
    assert payload["response_format"] == {
        "type": "audio",
        "mime_type": "audio/l16",
        "sample_rate": 24000,
    }


@pytest.mark.asyncio
async def test_async_sse_and_cancel(mock_sse):
    audio, _ = mock_sse([event(b"first"), event(b"second"), DONE])
    provider = GeminiTTS(api_key="offline-key")
    stream = provider.astream("hello")
    assert await anext(stream) == b"first"
    assert audio.read_count == 1
    await stream.aclose()
    assert audio.closed
    audio, _ = mock_sse([event(b"first"), event(b"second"), DONE])
    assert (
        b"".join([chunk async for chunk in provider.astream("hello")])
        == b"firstsecond"
    )
    assert audio.closed


@pytest.mark.parametrize(
    "data",
    [
        b"data: not-json\n\n",
        b'data: {"event_type":"step.delta"'
        b',"delta":{"type":"audio","data":"%%%"}}\n\n',
        b'data: {"event_type":"error","error":{}}\n\n',
        b'data: {"event_type":"step.delta"'
        b',"delta":{"type":"audio","mime_type":null}}\n\n',
        b'data: {"event_type":"step.delta"'
        b',"delta":{"type":"audio","mime_type":"audio/mpeg","data":"YQ=="}}\n\n',
        b'data: {"event_type":"interaction.completed"'
        b',"interaction":{"status":"failed"}}\n\n',
        event(b"partial"),
        DONE,
    ],
)
def test_invalid_truncated_or_empty_stream_raises(mock_sse, data):
    audio, requests = mock_sse([data])
    with pytest.raises((ValueError, RuntimeError)):
        list(GeminiTTS(api_key="offline-key").stream("hello"))
    assert audio.closed
    assert len(requests) == 1
