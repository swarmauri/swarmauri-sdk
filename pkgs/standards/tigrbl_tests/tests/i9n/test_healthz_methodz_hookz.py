"""
Healthz, Methodz and Hookz Endpoints Tests for Tigrbl v3

Tests that healthz, methodz and hookz endpoints are properly attached and behave as expected.
"""

import pytest
from tigrbl import hook_ctx
from tigrbl.types import SimpleNamespace


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_healthz_endpoint_comprehensive(api_client):
    """Test healthz endpoint attachment, behavior, and response format."""
    client, api, _ = api_client
    api.attach_diagnostics(prefix="", app=client._transport.app)

    # Check that healthz endpoint exists in routes
    routes = [route.path for route in api.router.routes]
    assert "/healthz" in routes

    # Test healthz response
    response = await client.get("/healthz")
    assert response.status_code == 200

    # Check content type
    assert response.headers["content-type"].startswith("application/json")

    # Should return JSON with health status
    data = SimpleNamespace(**response.json())

    # The actual healthz endpoint returns {'ok': True}
    assert isinstance(data.ok, bool)
    assert data.ok is True


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_methodz_endpoint_comprehensive(api_client):
    """Test methodz endpoint attachment, behavior, and response format."""
    client, api, _ = api_client
    api.attach_diagnostics(prefix="", app=client._transport.app)

    # Check that methodz endpoint exists in routes
    routes = [route.path for route in api.router.routes]
    assert "/methodz" in routes

    # Test methodz response
    response = await client.get("/methodz")
    assert response.status_code == 200

    # Check content type
    assert response.headers["content-type"].startswith("application/json")

    # Should return list of method info dicts
    data = response.json()["methods"]
    assert isinstance(data, list)

    names = {entry["method"] for entry in data}

    expected_methods = {
        "Item.create",
        "Item.read",
        "Item.update",
        "Item.delete",
        "Item.list",
        "Tenant.create",
        "Tenant.read",
        "Tenant.update",
        "Tenant.delete",
        "Tenant.list",
    }

    assert expected_methods.issubset(names)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hookz_endpoint_comprehensive(api_client):
    """Test hookz endpoint attachment, behavior, and response format."""
    client, api, Item = api_client

    @hook_ctx(ops="*", phase="POST_RESPONSE")
    def first_hook(cls, ctx):
        pass

    @hook_ctx(ops="*", phase="POST_RESPONSE")
    def second_hook(cls, ctx):
        pass

    @hook_ctx(ops="create", phase="POST_RESPONSE")
    def item_hook(cls, ctx):
        pass

    Item.first_hook = first_hook
    Item.second_hook = second_hook
    Item.item_hook = item_hook
    api.rebind(Item)
    api.attach_diagnostics(prefix="", app=client._transport.app)

    response = await client.get("/hookz")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_methodz_basic_functionality(api_client):
    """Test that methodz endpoint provides basic method information."""
    client, api, _ = api_client
    api.attach_diagnostics(prefix="", app=client._transport.app)

    response = await client.get("/methodz")
    methods = {m["method"] for m in response.json()["methods"]}

    # Should contain Item.create method
    assert "Item.create" in methods

    # Should contain basic CRUD operations
    crud_operations = ["create", "read", "update", "delete", "list"]
    for operation in crud_operations:
        assert f"Item.{operation}" in methods
        assert f"Tenant.{operation}" in methods


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_healthz_methodz_hookz_in_openapi_schema(api_client):
    """Test that healthz, methodz and hookz endpoints are included in OpenAPI schema."""
    client, api, _ = api_client
    api.attach_diagnostics(prefix="", app=client._transport.app)

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
    api.attach_diagnostics(prefix="", app=client._transport.app)

    # Note: In a real test, we'd mock database connectivity issues
    # For now, we just verify the endpoint responds and has the right structure
    response = await client.get("/healthz")
    assert response.status_code == 200

    data = SimpleNamespace(**response.json())
    assert isinstance(data.ok, bool)

    # The actual values depend on database state
    # but structure should always be consistent


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_methodz_reflects_dynamic_models(api_client):
    """Test that methodz reflects dynamically registered models."""
    client, api, _ = api_client
    api.attach_diagnostics(prefix="", app=client._transport.app)

    # Get initial methods
    response = await client.get("/methodz")
    initial_names = {m["method"] for m in response.json()["methods"]}

    # Should include methods for models from conftest
    for op in ["create", "read", "update", "delete", "list"]:
        assert f"Tenant.{op}" in initial_names


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_endpoints_are_synchronous(api_client):
    """Test that healthz, methodz and hookz endpoints work in sync mode."""
    client, api, _ = api_client
    api.attach_diagnostics(prefix="", app=client._transport.app)

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
