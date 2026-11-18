"""Opt-in billable verification; private credentials alone never opt in."""

import asyncio
import os
import pytest
from swarmauri_tts_gemini_dialogue import (
    GeminiDialogueTurn,
    GeminiDialogueTTS,
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
    key = os.getenv("GEMINI_API_KEY")
    first = os.getenv("SWARMAURI_TTS_VOICE", "Puck")
    second = os.getenv("SWARMAURI_TTS_SECOND_VOICE", "Kore")
    if not key or not first or not second:
        pytest.skip("Private API key and two accessible voice IDs required")
    provider = GeminiDialogueTTS(
        api_key=key,
        speaker_voices={"First": first, "Second": second},
        name=os.getenv("SWARMAURI_TTS_MODEL", "gemini-3.8-flash-tts"),
    )
    turns = (
        GeminiDialogueTurn(text="Hello from Swarmauri.", speaker="First"),
        GeminiDialogueTurn(text="Hello back.", speaker="Second"),
    )
    path = str(tmp_path / "dialogue.wav")
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
            GeminiDialogueTurn(
                text="Another short verification.", speaker="First"
            ),
        )
        paths = {turns: path, another: str(tmp_path / "second.wav")}
        if operation == "batch":
            provider.batch(paths)
        else:
            asyncio.run(provider.abatch(paths, max_concurrent=1))
        assert (tmp_path / "second.wav").stat().st_size > 0
    assert (tmp_path / "dialogue.wav").stat().st_size > 0
