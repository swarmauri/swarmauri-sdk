from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_provider_models_are_second_class():
    expected = {
        "swarmauri.llms.NvidiaNIMModel": (
            "swarmauri_llm_nvidia_nim.NvidiaNIMModel"
        ),
        "swarmauri.tool_llms.NvidiaNIMToolModel": (
            "swarmauri_llm_nvidia_nim.NvidiaNIMToolModel"
        ),
        "swarmauri.llms.CloudflareWorkersAIModel": (
            "swarmauri_llm_cloudflare.CloudflareWorkersAIModel"
        ),
        "swarmauri.tool_llms.CloudflareWorkersAIToolModel": (
            "swarmauri_llm_cloudflare.CloudflareWorkersAIToolModel"
        ),
    }
    for public_name, provider_name in expected.items():
        assert PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY[
            public_name
        ] == (provider_name)


def test_provider_models_lazy_import():
    from swarmauri.llms import CloudflareWorkersAIModel, NvidiaNIMModel
    from swarmauri.tool_llms import (
        CloudflareWorkersAIToolModel,
        NvidiaNIMToolModel,
    )

    assert NvidiaNIMModel.NvidiaNIMModel.__name__ == "NvidiaNIMModel"
    assert NvidiaNIMToolModel.NvidiaNIMToolModel.__name__ == (
        "NvidiaNIMToolModel"
    )
    assert CloudflareWorkersAIModel.CloudflareWorkersAIModel.__name__ == (
        "CloudflareWorkersAIModel"
    )
    assert (
        CloudflareWorkersAIToolModel.CloudflareWorkersAIToolModel.__name__
        == "CloudflareWorkersAIToolModel"
    )
