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


def test_provider_models_lazy_import():
    from swarmauri.llms import AzureOpenAIModel, XAIModel
    from swarmauri.tool_llms import AzureOpenAIToolModel, XAIToolModel

    assert AzureOpenAIModel.AzureOpenAIModel.__name__ == "AzureOpenAIModel"
    assert AzureOpenAIToolModel.AzureOpenAIToolModel.__name__ == (
        "AzureOpenAIToolModel"
    )
    assert XAIModel.XAIModel.__name__ == "XAIModel"
    assert XAIToolModel.XAIToolModel.__name__ == "XAIToolModel"
