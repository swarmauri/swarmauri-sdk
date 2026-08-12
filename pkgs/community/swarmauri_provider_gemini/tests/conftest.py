from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase
from swarmauri_provider_gemini import GeminiProvider
from swarmauri_tests_component import ComponentSpec


def pytest_swarmauri_component_specs():
    return [
        ComponentSpec(
            GeminiProvider,
            {"api_key": "test-key"},
            "ModelProvider",
            None,
            ModelProviderBase,
            round_trip_overrides={"api_key": "test-key"},
            excluded_fields=("api_key", "auth"),
        )
    ]
