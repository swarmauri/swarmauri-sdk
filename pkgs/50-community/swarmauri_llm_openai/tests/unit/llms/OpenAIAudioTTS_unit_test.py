"""Check deprecated LLM speech imports without a billable API request."""

import importlib

import httpx
import pytest
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_tts_openai import OpenaiTTS

pytestmark = pytest.mark.unit


def test_legacy_llm_import_warns_and_preserves_shape():
    with pytest.warns(FutureWarning, match="swarmauri_tts_openai"):
        module = importlib.import_module("swarmauri_llm_openai.OpenAIAudioTTS")
        importlib.reload(module)
    model = module.OpenAIAudioTTS(api_key="offline-key")
    assert isinstance(model, LLMBase)
    assert isinstance(model, OpenaiTTS)
    assert model.type == "OpenAIAudioTTS"
    assert model.resource == "LLM"
    assert model.timeout == 600.0
    assert (
        module.OpenAIAudioTTS.model_validate_json(model.model_dump_json()).id
        == model.id
    )


def test_legacy_llm_predict_uses_canonical_transport(monkeypatch, tmp_path):
    from swarmauri_llm_openai.OpenAIAudioTTS import OpenAIAudioTTS

    requests = []
    real_client = httpx.Client

    def respond(request):
        requests.append(request)
        assert str(request.url) == "https://api.openai.com/v1/audio/speech"
        assert request.headers["authorization"] == "Bearer offline-key"
        return httpx.Response(200, content=b"legacy-audio")

    transport = httpx.MockTransport(respond)
    monkeypatch.setattr(
        httpx, "Client", lambda **kw: real_client(transport=transport, **kw)
    )
    path = tmp_path / "speech.mp3"
    model = OpenAIAudioTTS(api_key="offline-key")
    assert model.predict("hello", str(path)) == str(path)
    assert path.read_bytes() == b"legacy-audio"
    assert len(requests) == 1
