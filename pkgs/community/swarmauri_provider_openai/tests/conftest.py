from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase
from swarmauri_base.model_providers.ModelCatalogBase import ModelCatalogBase
from swarmauri_base.model_providers.ProviderAuthBase import ProviderAuthBase
from swarmauri_base.model_providers.ProviderEndpointBase import (
    ProviderEndpointBase,
)
from swarmauri_base.model_providers.ProviderErrorMapperBase import (
    ProviderErrorMapperBase,
)
from swarmauri_provider_openai import (
    OpenAIAuthConfig,
    OpenAIEndpoints,
    OpenAIErrorMapper,
    OpenAIModelCatalog,
    OpenAIProvider,
)
from swarmauri_tests_component import (
    ComponentSpec,
    MethodSpec,
    model_catalog_method_specs,
)


def _configure(provider):
    assert provider.configure() is provider


def _options(provider):
    assert provider.connection_options()["timeout"] == provider.timeout


def _config(provider):
    assert provider.connection_config("realtime.connect").endpoint.startswith(
        "wss://"
    )


def _authorize(provider):
    config = provider.connection_config("realtime.connect")
    assert provider.authorize(config)["Authorization"] == "Bearer test-key"


def _prepare(provider):
    assert (
        provider.prepare_connection(
            "realtime.connect", model="gpt-realtime"
        ).query["model"]
        == "gpt-realtime"
    )


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
    assert auth.apply({})["Authorization"] == "Bearer test-key"


def _auth_apply_query(auth):
    assert auth.apply_query({"existing": "value"}) == {"existing": "value"}


def _endpoint_resolve(endpoints):
    assert endpoints.resolve("api") == endpoints.base_url


def _map_error(mapper):
    assert isinstance(mapper.map_error("failure"), RuntimeError)


def pytest_swarmauri_component_specs():
    return [
        ComponentSpec(
            OpenAIProvider,
            {"api_key": "test-key"},
            "ModelProvider",
            None,
            ModelProviderBase,
            round_trip_overrides={"api_key": "test-key"},
            excluded_fields=("api_key", "auth"),
            method_specs=_METHODS,
        ),
        ComponentSpec(
            OpenAIAuthConfig,
            {"api_key": "test-key"},
            "ModelProvider",
            None,
            ProviderAuthBase,
            round_trip_overrides={"api_key": "test-key"},
            excluded_fields=("api_key", "token"),
            method_specs=(
                MethodSpec("apply", _auth_apply),
                MethodSpec("apply_query", _auth_apply_query),
            ),
        ),
        ComponentSpec(
            OpenAIEndpoints,
            {},
            "ModelProvider",
            None,
            ProviderEndpointBase,
            method_specs=(MethodSpec("resolve", _endpoint_resolve),),
        ),
        ComponentSpec(
            OpenAIErrorMapper,
            {},
            "ComponentBase",
            None,
            ProviderErrorMapperBase,
            method_specs=(MethodSpec("map_error", _map_error),),
        ),
        ComponentSpec(
            OpenAIModelCatalog,
            {},
            "ComponentBase",
            None,
            ModelCatalogBase,
            method_specs=model_catalog_method_specs(),
        ),
    ]
