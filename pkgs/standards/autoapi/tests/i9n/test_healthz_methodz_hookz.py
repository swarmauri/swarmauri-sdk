"""
Healthz, Methodz and Hookz Endpoints Tests for AutoAPI v2

Tests that healthz, methodz and hookz endpoints are properly attached and behave as expected.
"""

from types import SimpleNamespace

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

    # Should return JSON object with method details
    data = response.json()
    assert isinstance(data, dict)
    assert isinstance(data.get("methods"), list)

    method_names = [entry["method"] for entry in data["methods"]]

    # Each item should describe a method
    for entry in data["methods"]:
        assert isinstance(entry["method"], str)
        assert "." in entry["method"]  # Should follow Model.operation pattern

    # Should have methods for Item and Tenant (from conftest)
    expected_methods = [
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
    ]

    for method in expected_methods:
        assert method in method_names


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hookz_endpoint_comprehensive(api_client):
    """Test hookz endpoint attachment, behavior, and response format."""
    client, api, _ = api_client

    def first_hook(ctx):
        pass

    def second_hook(ctx):
        pass

    def item_hook(ctx):
        pass

    # Manually attach hooks
    for model in api.models.values():
        create_ns = getattr(model.hooks, "create", SimpleNamespace())
        create_ns.POST_RESPONSE = [first_hook, second_hook]
        setattr(model.hooks, "create", create_ns)
    # Append item-specific hook
    item_ns = getattr(api.models["Item"].hooks, "create")
    item_ns.POST_RESPONSE.append(item_hook)

    routes = [route.path for route in api.router.routes]
    assert "/hookz" in routes

    response = await client.get("/hookz")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()
    assert isinstance(data, dict)

    expected_global_hooks = [
        f"{first_hook.__module__}.{first_hook.__qualname__}",
        f"{second_hook.__module__}.{second_hook.__qualname__}",
    ]

    # Validate Item.create hooks include global and item-specific hooks
    assert data["Item"]["create"]["POST_RESPONSE"] == expected_global_hooks + [
        f"{item_hook.__module__}.{item_hook.__qualname__}",
    ]

    # Validate Tenant.create hooks include only global hooks
    assert data["Tenant"]["create"]["POST_RESPONSE"] == expected_global_hooks


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_methodz_basic_functionality(api_client):
    """Test that methodz endpoint provides basic method information."""
    client, api, _ = api_client

    response = await client.get("/methodz")
    data = response.json()

    method_names = [entry["method"] for entry in data["methods"]]

    # Should contain Item.create method
    assert "Item.create" in method_names

    # Should contain basic CRUD operations
    crud_operations = ["create", "read", "update", "delete", "list"]
    for operation in crud_operations:
        assert f"Item.{operation}" in method_names
        assert f"Tenant.{operation}" in method_names


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
    method_names = [entry["method"] for entry in initial_data["methods"]]

    # Should include methods for models from conftest
    assert "Tenant.create" in method_names
    assert "Tenant.read" in method_names
    assert "Tenant.update" in method_names
    assert "Tenant.delete" in method_names
    assert "Tenant.list" in method_names


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
