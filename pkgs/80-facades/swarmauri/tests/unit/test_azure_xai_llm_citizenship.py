from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_provider_models_are_second_class():
    expected = {
        "swarmauri.llms.AzureOpenAIModel": (
            "swarmauri_llm_azureopenai.AzureOpenAIModel"
        ),
        "swarmauri.tool_llms.AzureOpenAIToolModel": (
            "swarmauri_llm_azureopenai.AzureOpenAIToolModel"
        ),
        "swarmauri.llms.XAIModel": "swarmauri_llm_xai.XAIModel",
        "swarmauri.tool_llms.XAIToolModel": "swarmauri_llm_xai.XAIToolModel",
    }
    for public_name, provider_name in expected.items():
        assert PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY[
            public_name
        ] == (provider_name)
