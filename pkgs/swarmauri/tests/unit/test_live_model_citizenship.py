from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_live_model_citizenship():
    registry = PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY
    assert registry["swarmauri.live_models.GeminiLiveModel"] == (
        "swarmauri_live_model_gemini.GeminiLiveModel"
    )
    assert registry["swarmauri.live_models.OpenAIRealtimeModel"] == (
        "swarmauri_live_model_openai.OpenAIRealtimeModel"
    )
