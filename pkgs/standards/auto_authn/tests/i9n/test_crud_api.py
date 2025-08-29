"""
Simplified integration tests for CRUD API endpoints.

Tests basic CRUD operations and endpoint availability for auto-generated
AutoAPI endpoints, focusing on status codes and basic response validation.
"""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestCRUDEndpointAvailability:
    """Test that CRUD endpoints are available and respond correctly."""

    @pytest.mark.asyncio
    async def test_tenants_endpoints_available(self, async_client: AsyncClient):
        """Test that tenant CRUD endpoints are available."""
        # Test GET /tenants (list)
        response = await async_client.get("/tenants")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        # Test invalid tenant ID returns 404
        invalid_id = str(uuid.uuid4())
        response = await async_client.get(f"/tenants/{invalid_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_users_endpoints_available(self, async_client: AsyncClient):
        """Test that user CRUD endpoints are available."""
        # Test GET /users (list)
        response = await async_client.get("/users")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        # Test invalid user ID returns 404
        invalid_id = str(uuid.uuid4())
        response = await async_client.get(f"/users/{invalid_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_clients_endpoints_available(self, async_client: AsyncClient):
        """Test that client CRUD endpoints are available."""
        # Test GET /clients (list)
        response = await async_client.get("/clients")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        # Test invalid client ID returns 404
        invalid_id = str(uuid.uuid4())
        response = await async_client.get(f"/clients/{invalid_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_api_keys_endpoints_available(self, async_client: AsyncClient):
        """Test that API key CRUD endpoints are available."""
        # Test GET /api_keys (list)
        response = await async_client.get("/api_keys")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        # Test invalid API key ID returns 404
        invalid_id = str(uuid.uuid4())
        response = await async_client.get(f"/api_keys/{invalid_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_services_endpoints_available(self, async_client: AsyncClient):
        """Test that service CRUD endpoints are available."""
        # Test GET /services (list)
        response = await async_client.get("/services")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        # Test invalid service ID returns 404
        invalid_id = str(uuid.uuid4())
        response = await async_client.get(f"/services/{invalid_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_service_keys_endpoints_available(self, async_client: AsyncClient):
        """Test that service key CRUD endpoints are available."""
        # Test GET /service_keys (list)
        response = await async_client.get("/service_keys")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        # Test invalid service key ID returns 404
        invalid_id = str(uuid.uuid4())
        response = await async_client.get(f"/service_keys/{invalid_id}")
        assert response.status_code == 404


@pytest.mark.integration
class TestCRUDValidation:
    """Test validation and error handling for CRUD operations."""

    @pytest.mark.asyncio
    async def test_invalid_json_returns_422(self, async_client: AsyncClient):
        """Test that invalid JSON returns proper validation error."""
        invalid_data = {"invalid": "data structure"}

        response = await async_client.post("/tenants", json=invalid_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_invalid_uuid_returns_422(self, async_client: AsyncClient):
        """Test that invalid UUID formats return validation errors."""
        invalid_id = "not-a-uuid"

        response = await async_client.get(f"/tenants/{invalid_id}")
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_unsupported_methods_return_405(self, async_client: AsyncClient):
        """Test that unsupported HTTP methods return 405 Method Not Allowed."""
        # Test unsupported methods on list endpoints
        response = await async_client.put("/tenants")
        assert response.status_code == 405

        response = await async_client.patch("/tenants")
        assert response.status_code == 405

        # Test unsupported methods on detail endpoints
        test_id = str(uuid.uuid4())
        response = await async_client.put(f"/tenants/{test_id}")
        assert response.status_code == 405  # Should be PATCH for updates


@pytest.mark.integration
class TestCRUDResponseStructure:
    """Test response structure and content types."""

    @pytest.mark.asyncio
    async def test_list_endpoints_return_arrays(self, async_client: AsyncClient):
        """Test that list endpoints return JSON arrays."""
        endpoints = [
            "/tenants",
            "/users",
            "/clients",
            "/api_keys",
            "/services",
            "/service_keys",
        ]

        for endpoint in endpoints:
            response = await async_client.get(endpoint)
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("application/json")
            data = response.json()
            assert isinstance(data, list), f"Endpoint {endpoint} should return an array"

    @pytest.mark.asyncio
    async def test_tenant_list_structure(self, async_client: AsyncClient):
        """Test that tenant list has expected structure."""
        response = await async_client.get("/tenants")
        assert response.status_code == 200

        data = response.json()
        if data:  # If there are tenants
            tenant = data[0]
            expected_fields = [
                "id",
                "slug",
                "name",
                "email",
                "created_at",
                "updated_at",
            ]
            for field in expected_fields:
                assert field in tenant, f"Tenant should have '{field}' field"

    @pytest.mark.asyncio
    async def test_user_list_structure(self, async_client: AsyncClient):
        """Test that user list has expected structure."""
        response = await async_client.get("/users")
        assert response.status_code == 200

        data = response.json()
        if data:  # If there are users
            user = data[0]
            expected_fields = [
                "id",
                "tenant_id",
                "username",
                "email",
                "created_at",
                "updated_at",
            ]
            for field in expected_fields:
                assert field in user, f"User should have '{field}' field"

            # Should not expose sensitive fields
            assert "password_hash" not in user, "User should not expose password_hash"

    @pytest.mark.asyncio
    async def test_client_list_structure(self, async_client: AsyncClient):
        """Test that client list has expected structure."""
        response = await async_client.get("/clients")
        assert response.status_code == 200

        data = response.json()
        if data:  # If there are clients
            client = data[0]
            expected_fields = ["id", "tenant_id", "created_at", "updated_at"]
            for field in expected_fields:
                assert field in client, f"Client should have '{field}' field"

            # Should not expose sensitive fields
            assert "client_secret_hash" not in client, (
                "Client should not expose client_secret_hash"
            )

    @pytest.mark.asyncio
    async def test_api_key_list_structure(self, async_client: AsyncClient):
        """Test that API key list has expected structure."""
        response = await async_client.get("/api_keys")
        assert response.status_code == 200

        data = response.json()
        if data:  # If there are API keys
            api_key = data[0]
            expected_fields = ["id", "user_id", "label", "created_at"]
            for field in expected_fields:
                assert field in api_key, f"API key should have '{field}' field"

            # Should not expose sensitive fields
            assert "raw_key" not in api_key, "API key should not expose raw_key"
            # May or may not have digest depending on API design


@pytest.mark.integration
class TestCRUDOperationalEndpoints:
    """Test operational endpoints related to CRUD API."""

    @pytest.mark.asyncio
    async def test_methodz_endpoint(self, async_client: AsyncClient):
        """Test that the methodz endpoint is available."""
        response = await async_client.get("/system/methodz")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")

    @pytest.mark.asyncio
    async def test_healthz_endpoint(self, async_client: AsyncClient):
        """Test that the healthz endpoint is available."""
        response = await async_client.get("/system/healthz")
        assert response.status_code == 200
        data = response.json()
        # The response might have either "status" or "ok" field
        assert ("status" in data and data["status"] == "alive") or (
            "ok" in data and data["ok"] is True
        )

    @pytest.mark.asyncio
    async def test_rpc_endpoint_exists(self, async_client: AsyncClient):
        """Test that the RPC endpoint exists (may not be fully functional)."""
        # RPC endpoint usually requires specific payload, so we just test if it exists
        response = await async_client.post("/rpc", json={})
        # Should not return 404 (endpoint exists) but may return 400/422 (bad request)
        assert response.status_code != 404


@pytest.mark.integration
class TestCRUDPermissions:
    """Test basic permission and access control behaviors."""

    @pytest.mark.asyncio
    async def test_delete_nonexistent_returns_404(self, async_client: AsyncClient):
        """Test that deleting non-existent resources returns 404."""
        nonexistent_id = str(uuid.uuid4())

        response = await async_client.delete(f"/tenants/{nonexistent_id}")
        assert response.status_code == 404

        response = await async_client.delete(f"/users/{nonexistent_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_patch_nonexistent_returns_404_or_422(
        self, async_client: AsyncClient
    ):
        """Test that updating non-existent resources returns 404 or 422."""
        nonexistent_id = str(uuid.uuid4())
        update_data = {"name": "Updated Name"}

        response = await async_client.patch(
            f"/tenants/{nonexistent_id}", json=update_data
        )
        # May return 404 (not found) or 422 (validation error, if validation happens first)
        assert response.status_code in [404, 422]

        response = await async_client.patch(
            f"/users/{nonexistent_id}", json=update_data
        )
        assert response.status_code in [404, 422]

    @pytest.mark.asyncio
    async def test_bulk_delete_behavior(self, async_client: AsyncClient):
        """Test bulk delete endpoint behavior."""
        # Test bulk delete endpoints (if supported)
        response = await async_client.delete("/tenants")
        # May return 405 (not allowed), 501 (not implemented), or 200/204 (success)
        assert response.status_code in [200, 204, 405, 501]

        response = await async_client.delete("/users")
        assert response.status_code in [200, 204, 405, 501]


@pytest.mark.integration
class TestCRUDIntegration:
    """Test integration between different CRUD resources."""

    @pytest.mark.asyncio
    async def test_tenant_user_relationship_structure(self, async_client: AsyncClient):
        """Test that tenant-user relationships are properly structured."""
        # Get tenants and users to verify relationship structure
        tenants_response = await async_client.get("/tenants")
        users_response = await async_client.get("/users")

        assert tenants_response.status_code == 200
        assert users_response.status_code == 200

        tenants = tenants_response.json()
        users = users_response.json()

        # If there are users, they should reference valid tenant IDs
        if users and tenants:
            user = users[0]
            if "tenant_id" in user:
                # User's tenant_id should reference an existing tenant
                # (This is a structural test, not enforcing referential integrity)
                assert isinstance(user["tenant_id"], str)

    @pytest.mark.asyncio
    async def test_user_api_key_relationship_structure(self, async_client: AsyncClient):
        """Test that user-API key relationships are properly structured."""
        # Get users and API keys to verify relationship structure
        users_response = await async_client.get("/users")
        api_keys_response = await async_client.get("/api_keys")

        assert users_response.status_code == 200
        assert api_keys_response.status_code == 200

        users = users_response.json()
        api_keys = api_keys_response.json()

        # If there are API keys, they should reference valid user IDs
        if api_keys and users:
            api_key = api_keys[0]
            if "user_id" in api_key:
                # API key's user_id should reference an existing user
                assert isinstance(api_key["user_id"], str)

    @pytest.mark.asyncio
    async def test_all_crud_endpoints_consistent(self, async_client: AsyncClient):
        """Test that all CRUD endpoints have consistent behavior."""
        endpoints = [
            "/tenants",
            "/users",
            "/clients",
            "/api_keys",
            "/services",
            "/service_keys",
        ]

        for endpoint in endpoints:
            # All should support GET (list)
            response = await async_client.get(endpoint)
            assert response.status_code == 200, f"GET {endpoint} should work"

            # All should return JSON arrays
            data = response.json()
            assert isinstance(data, list), f"GET {endpoint} should return array"

            # All should support POST (create) - might fail due to validation but should not 404
            response = await async_client.post(endpoint, json={})
            assert response.status_code != 404, (
                f"POST {endpoint} should exist (even if validation fails)"
            )

            # All should have detail endpoints that return 404 for invalid IDs
            invalid_id = str(uuid.uuid4())
            response = await async_client.get(f"{endpoint}/{invalid_id}")
            assert response.status_code == 404, (
                f"GET {endpoint}/{invalid_id} should return 404"
            )
