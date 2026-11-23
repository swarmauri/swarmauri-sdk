"""Exercise actual dialogue providers through the existing stateless agent."""

import base64
import json
import httpx
import pytest
from swarmauri_agent_texttospeech import TextToSpeechAgent
from swarmauri_tts_elevenlabs_dialogue import (
    DialogueTurn,
    ElevenLabsDialogueTTS,
)
from swarmauri_tts_gemini_dialogue import GeminiDialogueTurn, GeminiDialogueTTS

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
@pytest.mark.parametrize("vendor", ["elevenlabs", "gemini"])
async def test_agent_preserves_typed_turns_across_all_execution_modes(
    monkeypatch, tmp_path, vendor
):
    requests = []
    real_sync, real_async = httpx.Client, httpx.AsyncClient
    wav = b"RIFF0000WAVEaudio"

    def respond(request):
        payload = json.loads(request.content)
        requests.append(payload)
        if vendor == "elevenlabs":
            assert payload["inputs"][0] == {"text": " First ", "voice_id": "a"}
            assert payload["inputs"][1]["voice_id"] == "b"
            return httpx.Response(
                200, content=b"audio", headers={"content-type": "audio/mpeg"}
            )
        assert payload["input"][0]["content"][0]["text"] == " First "
        assert (
            payload["input"][0]["content"][1]["annotations"][0]["speaker"]
            == "B"
        )
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [
                            {
                                "type": "audio",
                                "data": base64.b64encode(wav).decode(),
                            }
                        ],
                    }
                ],
            },
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
    if vendor == "elevenlabs":
        provider = ElevenLabsDialogueTTS(api_key="offline-key")
        turns = (
            DialogueTurn(text=" First ", voice_id="a"),
            DialogueTurn(text="Second", voice_id="b"),
        )
        extension = "mp3"
    else:
        provider = GeminiDialogueTTS(
            api_key="offline-key", speaker_voices={"A": "Puck", "B": "Kore"}
        )
        turns = (
            GeminiDialogueTurn(text=" First ", speaker="A"),
            GeminiDialogueTurn(text="Second", speaker="B"),
        )
        extension = "wav"
    path = str(tmp_path / ("dialogue." + extension))
    agent = TextToSpeechAgent(tts=provider, output_path=path)
    assert agent.exec(turns) == path
    assert await agent.aexec(turns) == path
    assert agent.batch([turns], audio_paths=[path]) == [path]
    assert await agent.abatch(
        [turns], audio_paths=[path], max_concurrent=1
    ) == [path]
    assert len(requests) == 4
