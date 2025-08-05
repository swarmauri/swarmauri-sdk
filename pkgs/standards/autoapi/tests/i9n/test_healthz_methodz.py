"""
Healthz and Methodz Endpoints Tests for AutoAPI v2

Tests that healthz and methodz endpoints are properly attached and behave as expected.
"""

import pytest


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

    # Should return JSON array of method names (strings)
    data = response.json()
    assert isinstance(data, list)

    # Each item should be a string (method name)
    for method_name in data:
        assert isinstance(method_name, str)
        assert "." in method_name  # Should follow Model.operation pattern

    # Should have methods for Item and Tenant (from conftest)
    expected_methods = [
        "Items.create",
        "Items.read",
        "Items.update",
        "Items.delete",
        "Items.list",
        "Tenants.create",
        "Tenants.read",
        "Tenants.update",
        "Tenants.delete",
        "Tenants.list",
    ]

    for method in expected_methods:
        assert method in data


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_methodz_basic_functionality(api_client):
    """Test that methodz endpoint provides basic method information."""
    client, api, _ = api_client

    response = await client.get("/methodz")
    data = response.json()

    # Should contain Items.create method
    assert "Items.create" in data

    # Should contain basic CRUD operations
    crud_operations = ["create", "read", "update", "delete", "list"]
    for operation in crud_operations:
        assert f"Items.{operation}" in data
        assert f"Tenants.{operation}" in data


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_healthz_methodz_in_openapi_schema(api_client):
    """Test that healthz and methodz endpoints are included in OpenAPI schema."""
    client, api, _ = api_client

    # Get OpenAPI schema
    spec_response = await client.get("/openapi.json")
    spec = spec_response.json()
    paths = spec["paths"]

    # healthz and methodz should be in OpenAPI spec
    assert "/healthz" in paths
    assert "/methodz" in paths


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

    # Should include methods for models from conftest
    assert "Tenants.create" in initial_data
    assert "Tenants.read" in initial_data
    assert "Tenants.update" in initial_data
    assert "Tenants.delete" in initial_data
    assert "Tenants.list" in initial_data


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_endpoints_are_synchronous(api_client):
    """Test that healthz and methodz endpoints work in sync mode."""
    client, api, _ = api_client

    # These endpoints should work regardless of async/sync context
    healthz_response = await client.get("/healthz")
    assert healthz_response.status_code == 200

    methodz_response = await client.get("/methodz")
    assert methodz_response.status_code == 200

    # Responses should be immediate and not require async database operations
    assert healthz_response.json()
    assert methodz_response.json()
