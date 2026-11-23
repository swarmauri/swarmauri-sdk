"""Opt-in billable live verification; no calls run by default."""

import asyncio
import os

import pytest
from swarmauri_tts_gemini import GeminiTTS

pytestmark = [
    pytest.mark.i9n,
    pytest.mark.skipif(
        os.getenv("SWARMAURI_LIVE_TTS") != "1",
        reason="Set SWARMAURI_LIVE_TTS=1 to authorize billable live tests.",
    ),
]


@pytest.mark.parametrize(
    "operation",
    ["predict", "apredict", "stream", "astream", "batch", "abatch"],
)
def test_live_component(operation, tmp_path):
    selected = os.getenv("SWARMAURI_LIVE_TTS_OPERATIONS", "predict").split(",")
    if operation not in selected:
        pytest.skip("Operation not explicitly selected")
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        pytest.skip("Private GEMINI_API_KEY is required")
    provider = GeminiTTS(
        api_key=key,
        name=os.getenv("SWARMAURI_TTS_MODEL", "gemini-3.8-flash-tts"),
        voice=os.getenv("SWARMAURI_TTS_VOICE", "Kore"),
    )
    path = str(tmp_path / "speech.wav")
    text = "Swarmauri live speech verification."
    if operation == "predict":
        provider.predict(text, path)
    elif operation == "apredict":
        asyncio.run(provider.apredict(text, path))
    elif operation == "stream":
        assert b"".join(provider.stream(text))
        return
    elif operation == "astream":

        async def collect():
            return b"".join([chunk async for chunk in provider.astream(text)])

        assert asyncio.run(collect())
        return
    else:
        paths = {
            text: path,
            "A second short verification.": str(tmp_path / "second.wav"),
        }
        if operation == "batch":
            provider.batch(paths)
        else:
            asyncio.run(provider.abatch(paths, max_concurrent=1))
    assert (tmp_path / "speech.wav").stat().st_size > 0
    if operation in {"batch", "abatch"}:
        assert (tmp_path / "second.wav").stat().st_size > 0
