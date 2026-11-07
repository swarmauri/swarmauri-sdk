from swarmauri_provider_gemini import GeminiProvider
from swarmauri_core.model_providers import IProviderAuth, IProviderEndpoint


def test_provider_defaults():
    provider = GeminiProvider()
    assert provider.provider_name == "gemini"
    assert provider.catalog.get_model("gemini-3.1-flash-live-preview")


def test_provider_implements_auth_and_endpoint_contracts():
    provider = GeminiProvider(api_key="secret")

    assert isinstance(provider.auth, IProviderAuth)
    assert isinstance(provider.endpoints, IProviderEndpoint)
    assert provider.auth.apply({}) == {"x-goog-api-key": "secret"}
    config = provider.connection_config("live.connect")
    assert config.endpoint.startswith("wss://")
    assert "secret" not in config.model_dump_json()
