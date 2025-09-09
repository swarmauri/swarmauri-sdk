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
    """Ensure Tigrbl tracks all ORM models in schemas and tables."""
    expected = set(ORM_MODELS)
    assert expected == set(surface_api.tables.keys())
    assert expected.issubset(vars(surface_api.schemas).keys())
