import pytest

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


@pytest.mark.parametrize(
    ("public_name", "package_name"),
    [
        ("GeminiLiveModel", "swarmauri_live_model_gemini"),
        ("OpenAIRealtimeModel", "swarmauri_live_model_openai"),
        ("OpenAIResponsesWSModel", "swarmauri_live_model_openai"),
        ("XAIRealtimeModel", "swarmauri_live_model_xai"),
        ("QwenOmniRealtimeModel", "swarmauri_live_model_qwen"),
        ("NovaSonicLiveModel", "swarmauri_live_model_amazon_nova"),
    ],
)
def test_live_model_citizenship(public_name, package_name):
    registry = PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY
    assert registry[f"swarmauri.live_models.{public_name}"] == (
        f"{package_name}.{public_name}"
    )
