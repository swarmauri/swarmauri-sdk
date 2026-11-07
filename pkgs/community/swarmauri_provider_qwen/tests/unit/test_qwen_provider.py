from swarmauri_provider_qwen import QwenProvider
from swarmauri_core.model_providers import IProviderAuth, IProviderEndpoint


def test_provider_defaults():
    assert QwenProvider().catalog.get_model("qwen-omni-turbo-realtime")


def test_provider_implements_auth_and_endpoint_contracts():
    provider = QwenProvider(api_key="secret")

    assert isinstance(provider.auth, IProviderAuth)
    assert isinstance(provider.endpoints, IProviderEndpoint)
    config = provider.connection_config("realtime.connect")
    assert config.endpoint.startswith("wss://")
    assert provider.authorize(config)["Authorization"] == "Bearer secret"
    assert "secret" not in config.model_dump_json()
