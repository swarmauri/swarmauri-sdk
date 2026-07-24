"""Verify OpenRouter facade resources remain second-class citizens."""

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_openrouter_models_are_second_class():
    expected = {
        "swarmauri.llms.OpenRouterModel": (
            "swarmauri_llm_openrouter.OpenRouterModel"
        ),
        "swarmauri.tool_llms.OpenRouterToolModel": (
            "swarmauri_llm_openrouter.OpenRouterToolModel"
        ),
        "swarmauri.vlms.OpenRouterVLM": "swarmauri_llm_openrouter.OpenRouterVLM",
        "swarmauri.image_gens.OpenRouterImgGenModel": (
            "swarmauri_llm_openrouter.OpenRouterImgGenModel"
        ),
    }
    for public_name, provider_name in expected.items():
        assert (
            PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY[public_name]
            == provider_name
        )
