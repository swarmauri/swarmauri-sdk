from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase
from swarmauri_provider_amazon_nova import AmazonNovaProvider
from swarmauri_tests_component import ComponentSpec


_CREDENTIALS = {
    "access_key_id": "test-id",
    "secret_access_key": "test-secret",
    "session_token": "test-token",
}


def pytest_swarmauri_component_specs():
    return [
        ComponentSpec(
            AmazonNovaProvider,
            _CREDENTIALS,
            "ModelProvider",
            None,
            ModelProviderBase,
            round_trip_overrides=_CREDENTIALS,
            excluded_fields=(
                "api_key",
                "auth",
                "access_key_id",
                "secret_access_key",
                "session_token",
            ),
        )
    ]
