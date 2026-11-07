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
    assert "key" not in config.query
    prepared = provider.prepare_connection("live.connect")
    assert prepared.query == {"key": "secret"}
    assert prepared.resolved_url().endswith("?key=secret")
    assert "api_key" not in prepared.transport_options
