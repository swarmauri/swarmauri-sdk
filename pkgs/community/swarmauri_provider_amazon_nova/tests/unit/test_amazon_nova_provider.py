import pytest
from swarmauri_provider_amazon_nova import AmazonNovaProvider
from swarmauri_core.model_providers import IProviderAuth, IProviderEndpoint


def test_provider_defaults():
    provider = AmazonNovaProvider()
    assert provider.region == "us-east-1"
    assert provider.catalog.get_model("amazon.nova-sonic-v1:0")


def test_explicit_credentials_are_prepared_but_not_serialized():
    provider = AmazonNovaProvider(
        access_key_id="access",
        secret_access_key="secret",
        session_token="token",
    )

    config = provider.prepare_connection(
        "live.connect", model="amazon.nova-sonic-v1:0"
    )
    options = config.transport_options

    assert options["aws_access_key_id"] == "access"
    assert options["aws_secret_access_key"] == "secret"
    assert options["aws_session_token"] == "token"
    assert config.endpoint.endswith(
        "/model/amazon.nova-sonic-v1%3A0/invoke-with-bidirectional-stream"
    )
    assert "secret" not in provider.connection_options().values()
    assert (
        "secret"
        not in provider.connection_config(
            "live.connect", model="amazon.nova-sonic-v1:0"
        ).model_dump_json()
    )
    dumped = provider.model_dump()
    assert "access_key_id" not in dumped
    assert "secret_access_key" not in dumped
    assert "session_token" not in dumped


def test_provider_implements_auth_and_endpoint_contracts():
    provider = AmazonNovaProvider()

    assert isinstance(provider.auth, IProviderAuth)
    assert isinstance(provider.endpoints, IProviderEndpoint)
    assert provider.endpoints.resolve("bedrock.runtime") == provider.base_url
    assert provider.auth.apply({"Accept": "application/json"}) == {
        "Accept": "application/json"
    }
    config = provider.connection_config("bedrock.runtime")
    assert "access" not in config.model_dump_json()


def test_partial_explicit_credentials_are_rejected():
    provider = AmazonNovaProvider(access_key_id="access")
    with pytest.raises(ValueError, match="provided together"):
        provider.prepare_connection("live.connect", model="nova")
