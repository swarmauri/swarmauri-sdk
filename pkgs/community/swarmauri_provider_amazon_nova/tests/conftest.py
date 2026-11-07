from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase
from swarmauri_base.model_providers.ModelCatalogBase import ModelCatalogBase
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase
from swarmauri_base.model_providers.ProviderEndpointBase import (
    ProviderEndpointBase,
)
from swarmauri_base.model_providers.ProviderErrorMapperBase import (
    ProviderErrorMapperBase,
)
from swarmauri_provider_amazon_nova import (
    AmazonNovaAuthConfig,
    AmazonNovaEndpoints,
    AmazonNovaErrorMapper,
    AmazonNovaModelCatalog,
    AmazonNovaProvider,
)
from swarmauri_tests_component import (
    ComponentSpec,
    MethodSpec,
    model_catalog_method_specs,
)


_CREDENTIALS = {
    "access_key_id": "test-id",
    "secret_access_key": "test-secret",
    "session_token": "test-token",
}


def _configure(provider):
    assert provider.configure() is provider


def _options(provider):
    assert provider.connection_options()["timeout"] == provider.timeout


def _config(provider):
    assert provider.connection_config("bedrock.runtime").endpoint.startswith(
        "https://"
    )


def _authorize(provider):
    assert (
        provider.authorize(provider.connection_config("bedrock.runtime")) == {}
    )


def _prepare(provider):
    config = provider.prepare_connection(
        "live.connect", model="amazon.nova-sonic-v1:0"
    )
    assert config.transport_options["aws_access_key_id"] == "test-id"


_METHODS = tuple(
    MethodSpec(name, proof)
    for name, proof in (
        ("configure", _configure),
        ("connection_options", _options),
        ("connection_config", _config),
        ("authorize", _authorize),
        ("prepare_connection", _prepare),
    )
)


def _auth_apply(auth):
    assert auth.apply({"existing": "value"}) == {"existing": "value"}


def _auth_apply_query(auth):
    assert auth.apply_query({"existing": "value"}) == {"existing": "value"}


def _sdk_credentials(auth):
    assert auth.sdk_credentials()["aws_access_key_id"] == "test-id"


def _runtime_url(endpoints):
    assert endpoints.runtime_url().startswith("https://bedrock-runtime")


def _endpoint_resolve(endpoints):
    assert endpoints.resolve("bedrock.runtime") == endpoints.runtime_url()


def _map_error(mapper):
    assert isinstance(mapper.map_error("failure"), RuntimeError)


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
            method_specs=_METHODS,
        ),
        ComponentSpec(
            AmazonNovaAuthConfig,
            _CREDENTIALS,
            "ModelProvider",
            None,
            ProviderAuthBase,
            round_trip_overrides=_CREDENTIALS,
            excluded_fields=(
                "api_key",
                "token",
                "access_key_id",
                "secret_access_key",
                "session_token",
            ),
            method_specs=(
                MethodSpec("apply", _auth_apply),
                MethodSpec("apply_query", _auth_apply_query),
                MethodSpec("sdk_credentials", _sdk_credentials),
            ),
        ),
        ComponentSpec(
            AmazonNovaEndpoints,
            {},
            "ModelProvider",
            None,
            ProviderEndpointBase,
            method_specs=(
                MethodSpec("runtime_url", _runtime_url),
                MethodSpec("resolve", _endpoint_resolve),
            ),
        ),
        ComponentSpec(
            AmazonNovaErrorMapper,
            {},
            "ComponentBase",
            None,
            ProviderErrorMapperBase,
            method_specs=(MethodSpec("map_error", _map_error),),
        ),
        ComponentSpec(
            AmazonNovaModelCatalog,
            {},
            "ComponentBase",
            None,
            ModelCatalogBase,
            method_specs=model_catalog_method_specs(),
        ),
    ]
