import pytest

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "name,package",
    [
        ("DeepInfraKokoroTTS", "swarmauri_tts_deepinfra_kokoro"),
        ("DeepInfraQwen3TTS", "swarmauri_tts_deepinfra_qwen3"),
        (
            "DeepInfraQwen3VoiceDesignTTS",
            "swarmauri_tts_deepinfra_qwen3_voicedesign",
        ),
        ("ElevenLabsDialogueTTS", "swarmauri_tts_elevenlabs_dialogue"),
        ("PollyTTS", "swarmauri_tts_polly"),
        ("AzureTTS", "swarmauri_tts_azure"),
        ("CartesiaTTS", "swarmauri_tts_cartesia"),
        ("ElevenLabsTTS", "swarmauri_tts_elevenlabs"),
        ("DeepgramTTS", "swarmauri_tts_deepgram"),
        ("GeminiDialogueTTS", "swarmauri_tts_gemini_dialogue"),
        ("GeminiTTS", "swarmauri_tts_gemini"),
        ("OpenaiTTS", "swarmauri_tts_openai"),
        ("DeepInfraTTS", "swarmauri_tts_deepinfra"),
        ("TogetherTTS", "swarmauri_tts_together"),
    ],
)
def test_canonical_provider_registry(name, package):
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[f"swarmauri.tts.{name}"]
        == f"{package}.{name}"
    )


def test_facade_imports_point_to_standalone_classes():
    from swarmauri.tts.DeepInfraTTS import DeepInfraTTS
    from swarmauri.tts.OpenaiTTS import OpenaiTTS
    from swarmauri.tts.TogetherTTS import TogetherTTS
    from swarmauri_tts_deepinfra import DeepInfraTTS as DeepInfra
    from swarmauri_tts_openai import OpenaiTTS as OpenAI
    from swarmauri_tts_together import TogetherTTS as Together

    assert (OpenaiTTS, DeepInfraTTS, TogetherTTS) == (
        OpenAI,
        DeepInfra,
        Together,
    )


@pytest.mark.parametrize(
    "name,vendor",
    [
        ("DeepInfraKokoroTTS", "deepinfra_kokoro"),
        ("DeepInfraQwen3TTS", "deepinfra_qwen3"),
        ("DeepInfraQwen3VoiceDesignTTS", "deepinfra_qwen3_voicedesign"),
        ("ElevenLabsDialogueTTS", "elevenlabs_dialogue"),
        ("PollyTTS", "polly"),
        ("AzureTTS", "azure"),
        ("CartesiaTTS", "cartesia"),
        ("ElevenLabsTTS", "elevenlabs"),
        ("DeepgramTTS", "deepgram"),
        ("GeminiDialogueTTS", "gemini_dialogue"),
        ("GeminiTTS", "gemini"),
    ],
)
def test_standalone_facade_imports(name, vendor):
    import importlib

    facade = importlib.import_module(f"swarmauri.tts.{name}")
    canonical = importlib.import_module(f"swarmauri_tts_{vendor}")
    assert getattr(facade, name) is getattr(canonical, name)


def test_facade_legacy_openai_llm_route_uses_community_provider():
    from swarmauri.llms.OpenAIAudioTTS import OpenAIAudioTTS
    from swarmauri_llm_openai import OpenAIAudioTTS as CommunityOpenAIAudioTTS

    assert OpenAIAudioTTS is CommunityOpenAIAudioTTS
