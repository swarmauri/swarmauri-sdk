"""Offline package and documented request-contract tests."""

import importlib

from importlib.metadata import entry_points, metadata, version

from packaging.version import Version


import httpx

import pytest

from swarmauri_tts_polly import PollyTTS, __version__

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

    assert __version__ == version("swarmauri_tts_polly")

    assert Version(__version__).is_prerelease

    info = metadata("swarmauri_tts_polly")

    assert "Development Status :: 3 - Alpha" in info.get_all("Classifier")

    assert not any(
        "swarmauri_standard" in req or "swarmauri-standard" in req
        for req in info.get_all("Requires-Dist", [])
    )

    point = next(
        p for p in entry_points(group="swarmauri.tts") if p.name == "PollyTTS"
    )

    assert point.load() is PollyTTS

    assert issubclass(PollyTTS, TTSBase)


def test_file_request_contract(transport, tmp_path):

    provider = PollyTTS(
        **{
            "access_key_id": "offline-access",
            "secret_access_key": "offline-secret",
        }
    )

    path = tmp_path / "speech.mp3"

    assert provider.predict("hello", str(path)) == str(path.resolve())

    assert path.read_bytes() == b"audio"

    assert len(transport) == 1

    assert "offline-access" not in repr(provider)

    assert "offline-secret" not in repr(provider)


@pytest.mark.asyncio
async def test_async_file_and_batches(transport, tmp_path):

    provider = PollyTTS(
        **{
            "access_key_id": "offline-access",
            "secret_access_key": "offline-secret",
        }
    )

    path = str(tmp_path / "speech.mp3")

    assert await provider.apredict("hello", path) == path

    assert provider.batch({"hello": path}) == [path]

    assert await provider.abatch({"hello": path}, max_concurrent=1) == [path]

    assert len(transport) == 3


def test_import_is_available_without_standard_package():

    module = importlib.import_module("swarmauri_tts_polly")

    assert module.PollyTTS is PollyTTS


@pytest.mark.parametrize(
    "settings",
    [
        {"name": ""},
        {"timeout": 0},
        {"base_url": "https://other.example"},
        {"name": "not-engine"},
        {"access_key_id": ""},
        {"region": "cn-north-1"},
        {"region": "us-gov-west-1"},
        {"region": "evil.example"},
        {"response_format": "json"},
        {"response_format": "pcm", "sample_rate": 24000},
        {"response_format": "ogg_opus", "sample_rate": 16000},
        {"response_format": "mulaw", "sample_rate": 16000},
    ],
)
def test_invalid_settings_fail_before_requests(transport, settings):

    with pytest.raises(ValueError):
        PollyTTS(
            **(
                {
                    "access_key_id": "offline-access",
                    "secret_access_key": "offline-secret",
                }
                | settings
            )
        )

    assert transport == []


def test_sigv4_signs_exact_transmitted_bytes(transport, tmp_path):

    import hashlib

    import hmac

    import json

    provider = PollyTTS(
        access_key_id="offline-access",
        secret_access_key="offline-secret",
        session_token="offline-token",
        region="eu-west-1",
        response_format="pcm",
        sample_rate=16000,
        language_code="en-US",
    )

    provider.predict("Hello café <break/>", str(tmp_path / "speech.pcm"))

    request = transport[0]

    assert (
        str(request.url) == "https://polly.eu-west-1.amazonaws.com/v1/speech"
    )

    assert json.loads(request.content) == {
        "Engine": "neural",
        "VoiceId": "Joanna",
        "Text": "Hello café <break/>",
        "TextType": "text",
        "OutputFormat": "pcm",
        "SampleRate": "16000",
        "LanguageCode": "en-US",
    }

    assert "café".encode() in request.content

    assert request.headers["content-type"] == "application/json"

    assert request.headers["x-amz-security-token"] == "offline-token"

    auth = request.headers["authorization"]

    assert auth.startswith("AWS4-HMAC-SHA256 Credential=offline-access/")

    credential, signed_headers, signature = auth.split(" ", 1)[1].split(", ")

    scope = credential.split("/", 1)[1]

    assert scope.endswith("/eu-west-1/polly/aws4_request")

    names = signed_headers.split("=", 1)[1]

    canonical_headers = "".join(
        f"{name}:{request.headers[name]}\n" for name in names.split(";")
    )

    canonical = "\n".join(
        [
            "POST",
            "/v1/speech",
            "",
            canonical_headers,
            names,
            hashlib.sha256(request.content).hexdigest(),
        ]
    )

    date = request.headers["x-amz-date"]

    to_sign = "\n".join(
        [
            "AWS4-HMAC-SHA256",
            date,
            scope,
            hashlib.sha256(canonical.encode()).hexdigest(),
        ]
    )

    key = b"AWS4offline-secret"

    for value in [date[:8], "eu-west-1", "polly", "aws4_request"]:
        key = hmac.new(key, value.encode(), hashlib.sha256).digest()

    expected = hmac.new(key, to_sign.encode(), hashlib.sha256).hexdigest()

    assert signature == "Signature=" + expected

    assert "offline-token" not in repr(provider)


def test_no_session_token_and_no_credential_discovery(
    transport, monkeypatch, tmp_path
):

    import botocore.session

    def unexpected():

        raise AssertionError("Credential discovery must not run")

    monkeypatch.setattr(botocore.session, "get_session", unexpected)

    provider = PollyTTS(
        access_key_id="offline-access", secret_access_key="offline-secret"
    )

    provider.predict("hello", str(tmp_path / "speech.mp3"))

    assert "x-amz-security-token" not in transport[0].headers

    assert "SampleRate" not in __import__("json").loads(transport[0].content)


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
        PollyTTS(
            access_key_id="offline-access", secret_access_key="offline-secret"
        ).predict("hello", str(path))

    assert path.read_bytes() == b"existing"

    assert len(requests) == 1
