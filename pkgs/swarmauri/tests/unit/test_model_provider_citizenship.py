import pytest

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


@pytest.mark.parametrize(
    ("public_name", "package_name"),
    [
        ("GeminiProvider", "swarmauri_provider_gemini"),
        ("OpenAIProvider", "swarmauri_provider_openai"),
        ("OpenRouterProvider", "swarmauri_provider_openrouter"),
        ("XAIProvider", "swarmauri_provider_xai"),
        ("QwenProvider", "swarmauri_provider_qwen"),
        ("AmazonNovaProvider", "swarmauri_provider_amazon_nova"),
    ],
)
def test_model_provider_citizenship(public_name, package_name):
    registry = PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY
    assert registry[f"swarmauri.model_providers.{public_name}"] == (
        f"{package_name}.{public_name}"
    )
