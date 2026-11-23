import httpx
import pytest
from swarmauri_tts_polly import PollyTTS

pytestmark = pytest.mark.unit


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
                headers={"content-type": "audio/mpeg"},
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


def test_stream_yields_incrementally_and_closes_on_cancel(mock_sse):
    audio, requests = mock_sse([b"first", b"second"])
    provider = PollyTTS(
        **{
            "access_key_id": "offline-access",
            "secret_access_key": "offline-secret",
        }
    )
    stream = provider.stream("hello")
    assert next(stream) == b"first"
    assert audio.read_count == 1
    assert not audio.closed
    stream.close()
    assert audio.closed
    assert len(requests) == 1
    assert str(requests[0].url) == provider._speech_endpoint(True)


@pytest.mark.asyncio
async def test_async_stream_and_cancel(mock_sse):
    audio, requests = mock_sse([b"first", b"second"])
    provider = PollyTTS(
        **{
            "access_key_id": "offline-access",
            "secret_access_key": "offline-secret",
        }
    )
    stream = provider.astream("hello")
    assert await anext(stream) == b"first"
    assert audio.read_count == 1
    await stream.aclose()
    assert audio.closed
    audio, requests = mock_sse([b"first", b"second"])
    assert (
        b"".join([chunk async for chunk in provider.astream("hello")])
        == b"firstsecond"
    )
    assert audio.closed


@pytest.mark.parametrize("chunks", [[], [b""]])
def test_empty_stream_raises_and_closes(mock_sse, chunks):
    audio, _ = mock_sse(chunks)
    with pytest.raises(ValueError):
        list(
            PollyTTS(
                **{
                    "access_key_id": "offline-access",
                    "secret_access_key": "offline-secret",
                }
            ).stream("hello")
        )
    assert audio.closed
