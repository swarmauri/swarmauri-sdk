from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase
from swarmauri_provider_qwen import QwenProvider
from swarmauri_tests_component import ComponentSpec


def pytest_swarmauri_component_specs():
    return [
        ComponentSpec(
            QwenProvider,
            {"api_key": "test-key"},
            "ModelProvider",
            None,
            ModelProviderBase,
            round_trip_overrides={"api_key": "test-key"},
            excluded_fields=("api_key", "auth"),
        )
    ]
