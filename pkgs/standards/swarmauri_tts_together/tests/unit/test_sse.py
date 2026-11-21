import base64
import json

import httpx
import pytest

from swarmauri_tts_together import TogetherTTS

pytestmark = pytest.mark.unit


def event(audio):
    return (
        "data: "
        + json.dumps(
            {
                "type": "conversation.item.audio_output.delta",
                "delta": base64.b64encode(audio).decode(),
            }
        )
        + "\n\n"
    ).encode()


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
            requests.append(json.loads(request.content))
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


def test_fragmented_sse_decodes_audio_and_stops_at_done(mock_sse):
    first = event(b"first")
    audio, requests = mock_sse(
        [
            b": ping\n\n",
            first[:8],
            first[8:],
            b'data: {"type":"conversation.item.word_timestamps"}\n\n',
            event(b"second"),
            b"data: [DONE]\n\n",
            event(b"unreachable"),
        ]
    )
    stream = TogetherTTS(api_key="offline-key").stream("hello")
    assert next(stream) == b"first"
    assert audio.read_count == 3
    assert not audio.closed
    assert b"".join(stream) == b"second"
    assert audio.closed
    assert audio.read_count == 6
    assert requests[0]["stream"] is True
    assert requests[0]["response_format"] == "raw"
    assert requests[0]["response_encoding"] == "pcm_s16le"


@pytest.mark.asyncio
async def test_async_sse_closes_on_cancel(mock_sse):
    audio, _ = mock_sse(
        [event(b"first"), event(b"second"), b"data: [DONE]\n\n"]
    )
    stream = TogetherTTS(api_key="offline-key").astream("hello")
    assert await anext(stream) == b"first"
    assert audio.read_count == 1
    await stream.aclose()
    assert audio.closed


@pytest.mark.asyncio
async def test_async_sse_yields_decoded_bytes(mock_sse):
    audio, _ = mock_sse(
        [event(b"first"), event(b"second"), b"data: [DONE]\n\n"]
    )
    provider = TogetherTTS(api_key="offline-key")
    assert (
        b"".join([chunk async for chunk in provider.astream("hello")])
        == b"firstsecond"
    )
    assert audio.closed


@pytest.mark.parametrize(
    "data",
    [
        b"data: not-json\n\n",
        b'data: {"type":"conversation.item.audio_output.delta",'
        b'"delta":"%%%"}\n\n',
        b'data: {"type":"error","error":"failed"}\n\n',
        event(b"partial"),
    ],
)
def test_bad_or_truncated_stream_raises_and_closes(mock_sse, data):
    audio, requests = mock_sse([data])
    with pytest.raises((ValueError, RuntimeError)):
        list(TogetherTTS(api_key="offline-key").stream("hello"))
    assert audio.closed
    assert len(requests) == 1
