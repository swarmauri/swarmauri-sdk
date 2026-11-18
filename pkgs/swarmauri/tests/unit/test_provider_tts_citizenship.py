import pytest

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "name,package",
    [
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
