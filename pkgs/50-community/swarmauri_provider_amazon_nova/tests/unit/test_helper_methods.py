from types import SimpleNamespace

import pytest
from swarmauri_provider_amazon_nova import (
    AmazonNovaAuthConfig,
    AmazonNovaEndpoints,
    AmazonNovaErrorMapper,
    AmazonNovaToolSchemaConverter,
)


def _public_methods(cls):
    return {
        name
        for name, value in cls.__dict__.items()
        if not name.startswith("_")
        and (callable(value) or isinstance(value, (classmethod, staticmethod)))
    }


def test_converter_public_method_inventory_is_exhaustive():
    assert _public_methods(AmazonNovaToolSchemaConverter) == {"convert"}


def test_auth_apply_and_sdk_credentials_methods():
    auth = AmazonNovaAuthConfig(
        access_key_id="id", secret_access_key="secret", session_token="token"
    )
    assert auth.apply({"x": "y"}) == {"x": "y"}
    assert auth.sdk_credentials() == {
        "aws_access_key_id": "id",
        "aws_secret_access_key": "secret",
        "aws_session_token": "token",
    }
    assert AmazonNovaAuthConfig().sdk_credentials() == {}
    with pytest.raises(ValueError, match="provided together"):
        AmazonNovaAuthConfig(access_key_id="id").sdk_credentials()


def test_endpoint_runtime_url_resolve_and_unknown_failure():
    endpoints = AmazonNovaEndpoints(region="us-west-2")
    assert (
        endpoints.runtime_url()
        == "https://bedrock-runtime.us-west-2.amazonaws.com"
    )
    assert endpoints.resolve("live.connect") == endpoints.runtime_url()
    with pytest.raises(ValueError, match="unsupported"):
        endpoints.resolve("unsupported")


def test_error_mapper_and_tool_converter():
    assert (
        str(AmazonNovaErrorMapper().map_error("bad"))
        == "Amazon Nova provider error: bad"
    )
    converted = AmazonNovaToolSchemaConverter().convert(
        SimpleNamespace(name="lookup", description="Lookup")
    )
    assert converted["toolSpec"]["name"] == "lookup"
