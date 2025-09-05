import pytest_asyncio

import asyncio

from auto_authn.app import app
from auto_authn.routers.surface import surface_api

ORM_MODELS = [
    "Tenant",
    "User",
    "Client",
    "ApiKey",
    "Service",
    "ServiceKey",
    "AuthSession",
]


@pytest_asyncio.fixture()
async def openapi_spec() -> dict:
    """Initialize the API surface once and return its OpenAPI spec."""
    init = surface_api.initialize()
    if asyncio.iscoroutine(init):
        await init
    return app.openapi()


def test_request_response_examples_presence(openapi_spec: dict) -> None:
    """Ensure clear responses expose example bodies for every ORM."""
    for model in ORM_MODELS:
        schema_name = f"{model}ClearResponse"
        schema = openapi_spec["components"]["schemas"].get(schema_name)
        assert schema is not None, f"missing schema {schema_name}"
        assert schema.get("examples"), f"{schema_name} lacks examples"


def test_openapi_contains_all_schemas(openapi_spec: dict) -> None:
    """Verify OpenAPI documents request/response schemas for each ORM."""
    schema_names = set(openapi_spec["components"]["schemas"].keys())
    for model in ORM_MODELS:
        expected = {
            f"{model}{suffix}"
            for suffix in (
                "CreateRequest",
                "CreateResponse",
                "ReadResponse",
                "ListResponse",
                "UpdateRequest",
                "UpdateResponse",
                "ReplaceRequest",
                "ReplaceResponse",
                "DeleteResponse",
                "ClearResponse",
            )
        }
        assert expected.issubset(schema_names), f"schemas missing for {model}"


def test_all_models_registered_on_api_and_tables() -> None:
    """Ensure AutoAPI tracks all ORM models in schemas and tables."""
    expected = set(ORM_MODELS)
    assert expected == set(surface_api.tables.keys())
    assert expected.issubset(vars(surface_api.schemas).keys())


def test_service_key_request_schema(openapi_spec: dict) -> None:
    """ServiceKey request body exposes only allowed fields."""
    schema = openapi_spec["components"]["schemas"]["ServiceKeyCreateRequest"]
    assert set(schema["properties"].keys()) == {
        "label",
        "service_id",
        "valid_from",
        "valid_to",
    }
    assert set(schema["required"]) == {"label", "service_id"}
    assert "digest" not in schema["properties"]
    assert "api_key" not in schema["properties"]


def test_service_key_response_examples_include_validity(openapi_spec: dict) -> None:
    """Response examples include digest and validity window."""
    schema = openapi_spec["components"]["schemas"]["ServiceKeyCreateResponse"]
    props = schema["properties"]
    assert {
        "id",
        "label",
        "service_id",
        "digest",
        "valid_from",
        "valid_to",
        "last_used_at",
        "created_at",
    }.issubset(props.keys())
    examples = schema.get("examples")
    if examples:
        example = examples[0]["value"]
        assert "valid_from" in example and "valid_to" in example
