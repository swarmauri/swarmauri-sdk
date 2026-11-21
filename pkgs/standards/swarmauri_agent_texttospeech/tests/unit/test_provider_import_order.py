"""Verify installed providers discovered after the agent class is defined."""

import subprocess
import sys

import pytest

pytestmark = pytest.mark.unit


def test_provider_import_order_and_serialization():
    code = """
from swarmauri_tts_openai import OpenaiTTS
from swarmauri_agent_texttospeech import TextToSpeechAgent
from swarmauri_tts_gemini import GeminiTTS

provider = GeminiTTS(api_key="offline-key", voice="Puck", style="cheerful")
agent = TextToSpeechAgent(tts=provider, output_path="speech.wav")
assert agent.tts is provider
restored = TextToSpeechAgent.model_validate_json(agent.model_dump_json())
assert isinstance(restored.tts, GeminiTTS)
assert restored.tts.voice == "Puck"
assert restored.tts.style == "cheerful"
assert restored.output_path == "speech.wav"
openai = OpenaiTTS(api_key="offline-key")
assert TextToSpeechAgent(tts=openai).tts is openai
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
