import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestRFC8414AuthorizationServerMetadata:
    """Tests for the OAuth 2.0 Authorization Server Metadata endpoint."""

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="RFC 8414 endpoint not yet implemented; feature planned")
    async def test_metadata_endpoint_returns_valid_json(
        self, async_client: AsyncClient
    ) -> None:
        """Endpoint should return valid JSON document per RFC 8414."""
        response = await async_client.get("/.well-known/oauth-authorization-server")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        metadata = response.json()
        assert isinstance(metadata, dict)

    @pytest.mark.asyncio
    @pytest.mark.xfail(reason="RFC 8414 endpoint not yet implemented; feature planned")
    async def test_metadata_document_contains_required_fields(
        self, async_client: AsyncClient
    ) -> None:
        """Metadata document should include required RFC 8414 fields."""
        response = await async_client.get("/.well-known/oauth-authorization-server")
        assert response.status_code == 200
        metadata = response.json()
        required_fields = [
            "issuer",
            "authorization_endpoint",
            "token_endpoint",
        ]
        for field in required_fields:
            assert field in metadata, f"Missing required field: {field}"
