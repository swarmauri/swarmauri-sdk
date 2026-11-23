"""Offline package and documented request-contract tests."""

import importlib

from importlib.metadata import entry_points, metadata, version

from packaging.version import Version


import httpx

import pytest

from swarmauri_tts_azure import AzureTTS, __version__

from swarmauri_base.tts.TTSBase import TTSBase


pytestmark = pytest.mark.unit


@pytest.fixture
def transport(monkeypatch):

    real_sync, real_async = httpx.Client, httpx.AsyncClient

    requests = []

    def handler(request):

        requests.append(request)

        return httpx.Response(
            200, content=b"audio", headers={"content-type": "audio/mpeg"}
        )

    mock = httpx.MockTransport(handler)

    monkeypatch.setattr(
        httpx, "Client", lambda **kw: real_sync(transport=mock, **kw)
    )

    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: real_async(transport=mock, **kw)
    )

    return requests


def test_alpha_metadata_entrypoint_and_independent_dependencies():

    assert __version__ == version("swarmauri_tts_azure")

    assert Version(__version__).is_prerelease

    info = metadata("swarmauri_tts_azure")

    assert "Development Status :: 3 - Alpha" in info.get_all("Classifier")

    assert not any(
        "swarmauri_standard" in req or "swarmauri-standard" in req
        for req in info.get_all("Requires-Dist", [])
    )

    point = next(
        p for p in entry_points(group="swarmauri.tts") if p.name == "AzureTTS"
    )

    assert point.load() is AzureTTS

    assert issubclass(AzureTTS, TTSBase)


def test_file_request_contract(transport, tmp_path):

    provider = AzureTTS(**{"api_key": "offline-key"})

    path = tmp_path / "speech.mp3"

    assert provider.predict("hello", str(path)) == str(path.resolve())

    assert path.read_bytes() == b"audio"

    assert len(transport) == 1

    assert "offline-key" not in repr(provider)


@pytest.mark.asyncio
async def test_async_file_and_batches(transport, tmp_path):

    provider = AzureTTS(**{"api_key": "offline-key"})

    path = str(tmp_path / "speech.mp3")

    assert await provider.apredict("hello", path) == path

    assert provider.batch({"hello": path}) == [path]

    assert await provider.abatch({"hello": path}, max_concurrent=1) == [path]

    assert len(transport) == 3


def test_import_is_available_without_standard_package():

    module = importlib.import_module("swarmauri_tts_azure")

    assert module.AzureTTS is AzureTTS


@pytest.mark.parametrize(
    "settings",
    [
        {"name": ""},
        {"timeout": 0},
        {"base_url": "https://other.example"},
        {"name": "not-voice"},
        {"api_key": ""},
        {"region": "eastus.evil.test"},
        {"output_format": "json"},
        {"locale": 'en-US" evil="yes'},
    ],
)
def test_invalid_settings_fail_before_requests(transport, settings):

    with pytest.raises(ValueError):
        AzureTTS(**({"api_key": "offline-key"} | settings))

    assert transport == []


def test_ssml_contract_escapes_text(transport, tmp_path):

    from xml.etree.ElementTree import fromstring

    text = 'Hello <break time="10s"/> & café > "quoted"'

    provider = AzureTTS(
        api_key="offline-key",
        region="westeurope",
        output_format="riff-24khz-16bit-mono-pcm",
    )

    provider.predict(text, str(tmp_path / "speech.wav"))

    request = transport[0]

    assert (
        str(request.url)
        == "https://westeurope.tts.speech.microsoft.com/cognitiveservices/v1"
    )

    assert request.headers["ocp-apim-subscription-key"] == "offline-key"

    assert request.headers["content-type"] == "application/ssml+xml"

    assert (
        request.headers["x-microsoft-outputformat"]
        == "riff-24khz-16bit-mono-pcm"
    )

    assert request.headers["user-agent"] == "swarmauri_tts_azure/0.1.0a1"

    assert "authorization" not in request.headers

    root = fromstring(request.content)

    assert root.tag == "{http://www.w3.org/2001/10/synthesis}speak"

    assert root.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "en-US"

    assert len(root) == 1

    voice = root[0]

    assert voice.tag.endswith("}voice")

    assert voice.attrib["name"] == "en-US-JennyNeural"

    assert voice.text == text

    assert len(voice) == 0


@pytest.mark.parametrize(
    "text",
    ["", "  ", "bad\x00text", "bad\x01text", "bad\ud800text", "bad\ufffftext"],
)
def test_invalid_xml_or_empty_input_fails_before_request(
    transport, tmp_path, text
):

    with pytest.raises(ValueError):
        AzureTTS(api_key="offline-key").predict(
            text, str(tmp_path / "speech.mp3")
        )

    assert not transport


@pytest.mark.parametrize(
    "status, content, mime",
    [
        (403, b"denied", "text/plain"),
        (429, b"limited", "text/plain"),
        (200, b"{}", "application/json"),
        (200, b"", "audio/mpeg"),
    ],
)
def test_bad_response_preserves_file_and_is_not_retried(
    monkeypatch, tmp_path, status, content, mime
):

    real = httpx.Client

    requests = []

    def handler(request):

        requests.append(request)

        return httpx.Response(
            status, content=content, headers={"content-type": mime}
        )

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kw: real(transport=httpx.MockTransport(handler), **kw),
    )

    path = tmp_path / "speech.mp3"

    path.write_bytes(b"existing")

    with pytest.raises((ValueError, httpx.HTTPStatusError)):
        AzureTTS(api_key="offline-key").predict("hello", str(path))

    assert path.read_bytes() == b"existing"

    assert len(requests) == 1
