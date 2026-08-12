from swarmauri_provider_openai import OpenAIProvider
from swarmauri_core.model_providers import IProviderAuth, IProviderEndpoint


def test_provider_defaults():
    provider = OpenAIProvider()
    assert provider.provider_name == "openai"
    assert provider.catalog.get_model("gpt-realtime")


def test_provider_implements_auth_and_endpoint_contracts():
    provider = OpenAIProvider(
        api_key="secret", organization="org", project="project"
    )

    assert isinstance(provider.auth, IProviderAuth)
    assert isinstance(provider.endpoints, IProviderEndpoint)
    config = provider.connection_config("realtime.connect")
    headers = provider.authorize(config)
    assert config.endpoint == "wss://api.openai.com/v1/realtime"
    assert headers["Authorization"] == "Bearer secret"
    assert headers["OpenAI-Organization"] == "org"
    assert headers["OpenAI-Project"] == "project"
    assert "secret" not in config.model_dump_json()
