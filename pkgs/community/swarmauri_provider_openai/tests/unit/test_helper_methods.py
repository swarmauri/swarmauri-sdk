from types import SimpleNamespace

import pytest
from swarmauri_provider_openai import (
    OpenAIAuthConfig,
    OpenAIEndpoints,
    OpenAIErrorMapper,
    OpenAIToolSchemaConverter,
)


def _public_methods(cls):
    return {
        name
        for name, value in cls.__dict__.items()
        if not name.startswith("_")
        and (callable(value) or isinstance(value, (classmethod, staticmethod)))
    }


def test_converter_public_method_inventory_is_exhaustive():
    assert _public_methods(OpenAIToolSchemaConverter) == {"convert"}


def test_auth_apply_success_and_missing_key_failure():
    auth = OpenAIAuthConfig(
        api_key="key", organization="org", project="project"
    )
    headers = auth.apply({"x": "y"})
    assert headers == {
        "x": "y",
        "Authorization": "Bearer key",
        "OpenAI-Organization": "org",
        "OpenAI-Project": "project",
    }
    with pytest.raises(ValueError, match="api_key"):
        OpenAIAuthConfig().apply({})


def test_endpoint_resolve_success_and_unknown_failure():
    endpoints = OpenAIEndpoints()
    assert endpoints.resolve("api") == endpoints.base_url
    assert endpoints.resolve("realtime.connect") == endpoints.realtime_url
    with pytest.raises(ValueError, match="unsupported"):
        endpoints.resolve("unsupported")


def test_error_mapper_and_tool_converter():
    assert (
        str(OpenAIErrorMapper().map_error(ValueError("bad")))
        == "OpenAI provider error: bad"
    )
    tool = SimpleNamespace(
        name="lookup",
        description="Lookup",
        parameters=[
            SimpleNamespace(name="query", type="string", description="Query")
        ],
    )
    converted = OpenAIToolSchemaConverter().convert(tool)
    assert converted["name"] == "lookup"
    assert converted["parameters"]["properties"]["query"]["type"] == "string"
