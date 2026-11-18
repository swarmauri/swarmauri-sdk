import httpx
import pytest

from swarmauri_tts_openai import OpenaiTTS

pytestmark = pytest.mark.unit


def test_instructions_are_sent_only_to_supported_model(monkeypatch, tmp_path):
    import json

    real_client = httpx.Client
    requests = []

    def respond(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, content=b"audio")

    transport = httpx.MockTransport(respond)
    monkeypatch.setattr(
        httpx, "Client", lambda **kw: real_client(transport=transport, **kw)
    )
    model = OpenaiTTS(
        api_key="offline-key",
        name="gpt-4o-mini-tts",
        voice="coral",
        instructions="Speak calmly",
        response_format="wav",
        speed=0.9,
    )
    model.predict("hello", str(tmp_path / "speech.wav"))
    assert requests == [
        {
            "model": "gpt-4o-mini-tts",
            "voice": "coral",
            "input": "hello",
            "instructions": "Speak calmly",
            "response_format": "wav",
            "speed": 0.9,
        }
    ]
    with pytest.raises(ValueError, match="instructions"):
        OpenaiTTS(api_key="offline-key", instructions="Speak calmly")


@pytest.mark.parametrize("speed", [0, 0.24, 4.1])
def test_invalid_speed(speed):
    with pytest.raises(ValueError):
        OpenaiTTS(api_key="offline-key", speed=speed)
