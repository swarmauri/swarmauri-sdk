"""Opt-in billable live verification; no calls run by default."""

import asyncio
import os

import pytest
from swarmauri_tts_deepinfra_qwen3 import DeepInfraQwen3TTS

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
    if operation in {"stream", "astream"}:
        pytest.skip("Native streaming framing is not implemented")
    key = os.getenv("DEEPINFRA_API_KEY")
    if not key:
        pytest.skip("Private DEEPINFRA_API_KEY is required")
    provider = DeepInfraQwen3TTS(
        api_key=key,
        name=os.getenv("SWARMAURI_TTS_MODEL", "Qwen/Qwen3-TTS"),
        voice=os.getenv("SWARMAURI_TTS_VOICE", "Vivian"),
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
