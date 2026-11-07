from types import SimpleNamespace

import pytest
from swarmauri_provider_xai import (
    XAIAuthConfig,
    XAIEndpoints,
    XAIErrorMapper,
    XAIToolSchemaConverter,
)


def _public_methods(cls):
    return {
        name
        for name, value in cls.__dict__.items()
        if not name.startswith("_")
        and (callable(value) or isinstance(value, (classmethod, staticmethod)))
    }


def test_converter_public_method_inventory_is_exhaustive():
    assert _public_methods(XAIToolSchemaConverter) == {"convert"}


def test_auth_apply_success_and_missing_key_failure():
    assert XAIAuthConfig(api_key="key").apply({}) == {
        "Authorization": "Bearer key"
    }
    with pytest.raises(ValueError, match="api_key"):
        XAIAuthConfig().apply({})


def test_endpoint_resolve_success_and_unknown_failure():
    endpoints = XAIEndpoints()
    assert endpoints.resolve("chat.completions").endswith("/chat/completions")
    assert endpoints.resolve("realtime.connect") == endpoints.websocket_url
    with pytest.raises(ValueError, match="unsupported"):
        endpoints.resolve("unsupported")


def test_error_mapper_and_tool_converter():
    assert str(XAIErrorMapper().map_error("bad")) == "xAI provider error: bad"
    parameter = SimpleNamespace(
        name="mode",
        input_type="string",
        description="Mode",
        enum=["a"],
        required=True,
    )
    converted = XAIToolSchemaConverter().convert(
        SimpleNamespace(
            name="lookup", description="Lookup", parameters=[parameter]
        )
    )
    schema = converted["function"]["parameters"]
    assert schema["required"] == ["mode"]
    assert schema["properties"]["mode"]["enum"] == ["a"]
