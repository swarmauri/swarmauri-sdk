from swarmauri_base.ComponentBase import ResourceTypes
from swarmauri_base.model_providers import (
    ModelProviderBase,
    ProviderAuthBase,
    ProviderConnectionConfig,
    ProviderEndpointBase,
)
from swarmauri_base.model_providers.ProviderConnectionConfigBase import (
    ProviderConnectionConfigBase,
)
from swarmauri_core.model_providers import IProviderAuth, IProviderEndpoint


def test_auth_base_implements_interface_without_serializing_secrets() -> None:
    auth = ProviderAuthBase(api_key="secret", token="token")

    assert isinstance(auth, IProviderAuth)
    assert auth.apply({"Accept": "application/json"}) == {
        "Accept": "application/json"
    }
    assert "api_key" not in auth.model_dump()
    assert "token" not in auth.model_dump()
    assert auth.resource == ResourceTypes.MODEL_PROVIDER.value


def test_endpoint_base_implements_interface() -> None:
    endpoint = ProviderEndpointBase(base_url="https://example.test/v1")

    assert isinstance(endpoint, IProviderEndpoint)
    assert endpoint.resolve("models.list") == "https://example.test/v1"
    assert endpoint.resource == ResourceTypes.MODEL_PROVIDER.value


def test_connection_config_is_final_dto_with_compatibility_alias() -> None:
    assert ProviderConnectionConfigBase is ProviderConnectionConfig
    config = ProviderConnectionConfig(
        endpoint="https://example.test/v1",
        auth_context=ProviderAuthBase(api_key="secret"),
    )

    assert config.type == "ProviderConnectionConfig"
    assert "auth_context" not in config.model_dump()


def test_model_provider_resolves_and_authorizes_connection() -> None:
    provider = ModelProviderBase(
        base_url="https://example.test/v1",
        endpoints=ProviderEndpointBase(base_url="https://example.test/v1"),
    )

    config = provider.connection_config("models.list")

    assert config.endpoint == "https://example.test/v1"
    assert provider.authorize(config) == {}
    prepared = provider.prepare_connection("models.list")
    assert prepared.resolved_url() == "https://example.test/v1"


def test_connection_config_resolves_encoded_query_without_mutation() -> None:
    config = ProviderConnectionConfig(
        endpoint="wss://example.test/live?version=1",
        query={"model": "model/name"},
    )

    assert config.resolved_url() == (
        "wss://example.test/live?version=1&model=model%2Fname"
    )
    assert config.query == {"model": "model/name"}


def test_connection_config_rejects_missing_endpoint() -> None:
    config = ProviderConnectionConfig()

    try:
        config.resolved_url()
    except ValueError as error:
        assert "no endpoint" in str(error)
    else:
        raise AssertionError("connection without endpoint was resolved")
