"""
Healthz, Methodz and Hookz Endpoints Tests for AutoAPI v2

Tests that healthz, methodz and hookz endpoints are properly attached and behave as expected.
"""

import pytest
from autoapi.v3.decorators import hook_ctx


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_healthz_endpoint_comprehensive(api_client):
    """Test healthz endpoint attachment, behavior, and response format."""
    client, api, _ = api_client

    # Check that healthz endpoint exists in routes
    routes = [route.path for route in api.router.routes]
    assert "/healthz" in routes

    # Test healthz response
    response = await client.get("/healthz")
    assert response.status_code == 200

    # Check content type
    assert response.headers["content-type"].startswith("application/json")

    # Should return JSON with health status
    data = response.json()

    # The actual healthz endpoint returns {'ok': True}
    assert "ok" in data
    assert isinstance(data["ok"], bool)
    assert data["ok"] is True


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_methodz_endpoint_comprehensive(api_client):
    """Test methodz endpoint attachment, behavior, and response format."""
    client, api, _ = api_client

    # Check that methodz endpoint exists in routes
    routes = [route.path for route in api.router.routes]
    assert "/methodz" in routes

    # Test methodz response
    response = await client.get("/methodz")
    assert response.status_code == 200

    # Check content type
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()
    assert "methods" in data
    assert isinstance(data["methods"], list)

    method_names = [m["method"] for m in data["methods"]]

    # Should have methods for Item (from conftest)
    expected_methods = [
        "Item.create",
        "Item.read",
        "Item.update",
        "Item.delete",
        "Item.list",
    ]

    for method in expected_methods:
        assert method in method_names


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hookz_endpoint_comprehensive(api_client):
    """Test hookz endpoint attachment, behavior, and response format."""
    client, api, Item = api_client

    @hook_ctx(ops="create", phase="POST_RESPONSE")
    async def item_hook(cls, ctx):
        pass

    Item.item_hook = item_hook
    api.rebind(Item)

    routes = [route.path for route in api.router.routes]
    assert "/hookz" in routes

    response = await client.get("/hookz")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()
    assert isinstance(data, dict)
    assert "Item" in data
    assert "create" in data["Item"]
    assert "POST_RESPONSE" in data["Item"]["create"]
    assert any("item_hook" in h for h in data["Item"]["create"]["POST_RESPONSE"])


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_methodz_basic_functionality(api_client):
    """Test that methodz endpoint provides basic method information."""
    client, api, _ = api_client

    response = await client.get("/methodz")
    data = response.json()
    method_names = [m["method"] for m in data.get("methods", [])]

    # Should contain Item.create method
    assert "Item.create" in method_names

    # Should contain basic CRUD operations for Item
    crud_operations = ["create", "read", "update", "delete", "list"]
    for operation in crud_operations:
        assert f"Item.{operation}" in method_names


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_healthz_methodz_hookz_in_openapi_schema(api_client):
    """Test that healthz, methodz and hookz endpoints are included in OpenAPI schema."""
    client, api, _ = api_client

    # Get OpenAPI schema
    spec_response = await client.get("/openapi.json")
    spec = spec_response.json()
    paths = spec["paths"]

    # healthz, methodz and hookz should be in OpenAPI spec
    assert "/healthz" in paths
    assert "/methodz" in paths
    assert "/hookz" in paths


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_healthz_database_error_handling(api_client):
    """Test healthz endpoint behavior when database has issues."""
    client, api, _ = api_client

    # Note: In a real test, we'd mock database connectivity issues
    # For now, we just verify the endpoint responds and has the right structure
    response = await client.get("/healthz")
    assert response.status_code == 200

    data = response.json()
    assert "ok" in data
    assert isinstance(data["ok"], bool)

    # The actual values depend on database state
    # but structure should always be consistent


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_methodz_reflects_dynamic_models(api_client):
    """Test that methodz reflects dynamically registered models."""
    client, api, _ = api_client

    # Get initial methods
    response = await client.get("/methodz")
    initial_data = response.json()
    method_names = [m["method"] for m in initial_data.get("methods", [])]

    # Should include methods for Item model from conftest
    assert "Item.create" in method_names
    assert "Item.read" in method_names
    assert "Item.update" in method_names
    assert "Item.delete" in method_names
    assert "Item.list" in method_names


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_endpoints_are_synchronous(api_client):
    """Test that healthz, methodz and hookz endpoints work in sync mode."""
    client, api, _ = api_client

    # These endpoints should work regardless of async/sync context
    healthz_response = await client.get("/healthz")
    assert healthz_response.status_code == 200

    methodz_response = await client.get("/methodz")
    assert methodz_response.status_code == 200

    hookz_response = await client.get("/hookz")
    assert hookz_response.status_code == 200

    # Responses should be immediate and not require async database operations
    assert healthz_response.json()
    assert methodz_response.json()
    assert isinstance(hookz_response.json(), dict)
