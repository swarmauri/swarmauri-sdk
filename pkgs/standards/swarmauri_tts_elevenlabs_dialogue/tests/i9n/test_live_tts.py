"""Opt-in billable verification; private credentials alone never opt in."""

import asyncio
import os
import pytest
from swarmauri_tts_elevenlabs_dialogue import (
    DialogueTurn,
    ElevenLabsDialogueTTS,
)

pytestmark = [
    pytest.mark.i9n,
    pytest.mark.skipif(
        os.getenv("SWARMAURI_LIVE_TTS") != "1",
        reason="Explicit live-test opt-in required",
    ),
]


@pytest.mark.parametrize(
    "operation",
    ["predict", "apredict", "stream", "astream", "batch", "abatch"],
)
def test_live_component(operation, tmp_path):
    if operation not in os.getenv(
        "SWARMAURI_LIVE_TTS_OPERATIONS", "predict"
    ).split(","):
        pytest.skip("Operation not explicitly selected")
    key = os.getenv("ELEVENLABS_API_KEY")
    first = os.getenv("SWARMAURI_TTS_VOICE")
    second = os.getenv("SWARMAURI_TTS_SECOND_VOICE")
    if not key or not first or not second:
        pytest.skip("Private API key and two accessible voice IDs required")
    provider = ElevenLabsDialogueTTS(
        api_key=key, name=os.getenv("SWARMAURI_TTS_MODEL", "eleven_v4")
    )
    turns = (
        DialogueTurn(text="Hello from Swarmauri.", voice_id=first),
        DialogueTurn(text="Hello back.", voice_id=second),
    )
    path = str(tmp_path / "dialogue.mp3")
    if operation == "predict":
        provider.predict(turns, path)
    elif operation == "apredict":
        asyncio.run(provider.apredict(turns, path))
    elif operation == "stream":
        assert b"".join(provider.stream(turns))
        return
    elif operation == "astream":

        async def collect():
            return b"".join([chunk async for chunk in provider.astream(turns)])

        assert asyncio.run(collect())
        return
    else:
        another = (
            DialogueTurn(text="Another short verification.", voice_id=first),
        )
        paths = {turns: path, another: str(tmp_path / "second.mp3")}
        if operation == "batch":
            provider.batch(paths)
        else:
            asyncio.run(provider.abatch(paths, max_concurrent=1))
        assert (tmp_path / "second.mp3").stat().st_size > 0
    assert (tmp_path / "dialogue.mp3").stat().st_size > 0
