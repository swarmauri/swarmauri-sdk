from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_model_provider_citizenship():
    registry = PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY
    assert registry["swarmauri.model_providers.GeminiProvider"] == (
        "swarmauri_provider_gemini.GeminiProvider"
    )
    assert registry["swarmauri.model_providers.OpenAIProvider"] == (
        "swarmauri_provider_openai.OpenAIProvider"
    )
    assert registry["swarmauri.model_providers.OpenRouterProvider"] == (
        "swarmauri_provider_openrouter.OpenRouterProvider"
    )
