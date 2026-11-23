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
    prepared = provider.prepare_connection(
        "realtime.connect", model="gpt-realtime"
    )
    assert prepared.resolved_url().endswith("?model=gpt-realtime")
    assert prepared.headers["OpenAI-Beta"] == "realtime=v1"
    assert "api_key" not in prepared.transport_options


def test_responses_connection_uses_dedicated_endpoint():
    provider = OpenAIProvider(api_key="secret")
    prepared = provider.prepare_connection("responses.connect")

    assert prepared.resolved_url() == "wss://api.openai.com/v1/responses"
    assert "OpenAI-Beta" not in prepared.headers
