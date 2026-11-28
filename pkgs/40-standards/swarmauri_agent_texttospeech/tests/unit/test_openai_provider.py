"""Check that the TTS agent accepts the standalone OpenAI speech provider."""

from pathlib import Path

import httpx
import pytest

from swarmauri_agent_texttospeech import TextToSpeechAgent
from swarmauri_tts_openai import OpenaiTTS

pytestmark = pytest.mark.unit


def test_agent_synthesizes_with_standalone_openai_provider(
    monkeypatch, tmp_path
):
    client = httpx.Client
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, content=b"audio")
    )
    monkeypatch.setattr(
        httpx, "Client", lambda **kwargs: client(transport=transport, **kwargs)
    )

    provider = OpenaiTTS(api_key="offline-key")
    agent = TextToSpeechAgent(
        tts=provider, output_path=str(tmp_path / "agent.mp3")
    )

    assert Path(agent.exec("hello")).read_bytes() == b"audio"
