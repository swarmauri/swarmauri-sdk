from types import SimpleNamespace

import pytest
from swarmauri_provider_gemini import (
    GeminiAuthConfig,
    GeminiEndpoints,
    GeminiErrorMapper,
    GeminiToolSchemaConverter,
)


def _public_methods(cls):
    return {
        name
        for name, value in cls.__dict__.items()
        if not name.startswith("_")
        and (callable(value) or isinstance(value, (classmethod, staticmethod)))
    }


def test_converter_public_method_inventory_is_exhaustive():
    assert _public_methods(GeminiToolSchemaConverter) == {"convert"}


def test_auth_header_and_query_methods():
    auth = GeminiAuthConfig(api_key="key")
    assert auth.apply({"x": "y"}) == {"x": "y", "x-goog-api-key": "key"}
    assert auth.apply_query({"model": "m"}) == {"model": "m", "key": "key"}
    with pytest.raises(ValueError, match="api_key"):
        GeminiAuthConfig().apply_query({})


def test_endpoint_resolve_success_and_unknown_failure():
    endpoints = GeminiEndpoints()
    assert endpoints.resolve("api") == endpoints.base_url
    assert endpoints.resolve("live.connect") == endpoints.websocket_url
    with pytest.raises(ValueError, match="unsupported"):
        endpoints.resolve("unsupported")


def test_error_mapper_and_tool_converter():
    assert (
        str(GeminiErrorMapper().map_error("bad"))
        == "Gemini provider error: bad"
    )
    parameter = SimpleNamespace(
        name="query", type="string", description="Query", required=True
    )
    converted = GeminiToolSchemaConverter().convert(
        SimpleNamespace(
            name="lookup", description="Lookup", parameters=[parameter]
        )
    )
    assert converted["parameters"]["required"] == ["query"]
