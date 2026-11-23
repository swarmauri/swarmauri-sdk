"""Keep the legacy standard import usable without contacting OpenAI."""

import importlib

import pytest
from swarmauri_tts_openai import OpenaiTTS as CanonicalTTS

pytestmark = pytest.mark.unit


def test_legacy_standard_import_warns_and_preserves_class():
    with pytest.warns(FutureWarning, match="swarmauri_tts_openai"):
        module = importlib.import_module("swarmauri_standard.tts.OpenaiTTS")
        importlib.reload(module)
    assert module.OpenaiTTS is CanonicalTTS
    provider = module.OpenaiTTS(api_key="offline-key")
    assert provider.type == "OpenaiTTS"
    assert provider.resource == "TTS"
    assert provider.name == "tts-1"


def test_old_standard_serialized_type_is_preserved():
    provider = CanonicalTTS(api_key="offline-key")
    restored = CanonicalTTS.model_validate_json(provider.model_dump_json())
    assert restored.id == provider.id
    assert restored.type == "OpenaiTTS"
    assert restored.resource == "TTS"
