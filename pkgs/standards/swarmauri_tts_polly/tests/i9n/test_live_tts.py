"""Opt-in billable live verification; no calls run by default."""

import asyncio
import os

import pytest
from swarmauri_tts_polly import PollyTTS

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
    access = os.getenv("AWS_ACCESS_KEY_ID")
    secret = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION")
    if not access or not secret or not region:
        pytest.skip("Explicit private AWS credentials and AWS_REGION required")
    provider = PollyTTS(
        access_key_id=access,
        secret_access_key=secret,
        session_token=os.getenv("AWS_SESSION_TOKEN"),
        region=region,
        name=os.getenv("SWARMAURI_TTS_MODEL", "neural"),
        voice=os.getenv("SWARMAURI_TTS_VOICE", "Joanna"),
    )
    path = str(tmp_path / "speech.mp3")
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
            "A second short verification.": str(tmp_path / "second.mp3"),
        }
        if operation == "batch":
            provider.batch(paths)
        else:
            asyncio.run(provider.abatch(paths, max_concurrent=1))
    assert (tmp_path / "speech.mp3").stat().st_size > 0
    if operation in {"batch", "abatch"}:
        assert (tmp_path / "second.mp3").stat().st_size > 0
