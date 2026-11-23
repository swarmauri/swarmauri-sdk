from types import SimpleNamespace

import pytest
from swarmauri_provider_qwen import (
    QwenAuthConfig,
    QwenEndpoints,
    QwenErrorMapper,
    QwenToolSchemaConverter,
)


def _public_methods(cls):
    return {
        name
        for name, value in cls.__dict__.items()
        if not name.startswith("_")
        and (callable(value) or isinstance(value, (classmethod, staticmethod)))
    }


def test_converter_public_method_inventory_is_exhaustive():
    assert _public_methods(QwenToolSchemaConverter) == {"convert"}


def test_auth_apply_success_and_missing_key_failure():
    assert QwenAuthConfig(api_key="key").apply({}) == {
        "Authorization": "Bearer key"
    }
    with pytest.raises(ValueError, match="api_key"):
        QwenAuthConfig().apply({})


def test_endpoint_resolve_success_and_unknown_failure():
    endpoints = QwenEndpoints()
    assert endpoints.resolve("api") == endpoints.base_url
    assert endpoints.resolve("realtime.connect") == endpoints.websocket_url
    with pytest.raises(ValueError, match="unsupported"):
        endpoints.resolve("unsupported")


def test_error_mapper_and_tool_converter():
    assert (
        str(QwenErrorMapper().map_error("bad")) == "Qwen provider error: bad"
    )
    converted = QwenToolSchemaConverter().convert(
        SimpleNamespace(name="lookup")
    )
    assert converted == {
        "type": "function",
        "name": "lookup",
        "parameters": {"type": "object", "properties": {}},
    }
