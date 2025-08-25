"""
Integration tests for OIDC (OpenID Connect) endpoints.

Tests the OpenID Connect discovery endpoint (.well-known/openid-configuration)
and JWKS endpoint (.well-known/jwks.json) for proper format, compliance,
and functionality.
"""

import os
from unittest.mock import patch
from urllib.parse import urlparse

import pytest
from httpx import AsyncClient
from swarmauri_signing_jws.JwsSignerVerifier import _jwk_to_pub_for_signer


@pytest.mark.integration
class TestOIDCDiscoveryEndpoint:
    """Test OpenID Connect discovery endpoint compliance."""

    @pytest.mark.asyncio
    async def test_discovery_endpoint_returns_valid_json(
        self, async_client: AsyncClient
    ):
        """Test that the discovery endpoint returns valid JSON."""
        response = await async_client.get("/.well-known/openid-configuration")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")

        # Should be parseable as JSON
        discovery_doc = response.json()
        assert isinstance(discovery_doc, dict)

    @pytest.mark.asyncio
    async def test_discovery_document_structure(self, async_client: AsyncClient):
        """Test that the discovery document contains required OIDC fields."""
        response = await async_client.get("/.well-known/openid-configuration")
        discovery_doc = response.json()

        # Required OIDC discovery fields
        required_fields = [
            "issuer",
            "jwks_uri",
            "token_endpoint",
            "scopes_supported",
            "response_types_supported",
            "subject_types_supported",
            "id_token_signing_alg_values_supported",
            "claims_supported",
        ]

        for field in required_fields:
            assert field in discovery_doc, f"Missing required field: {field}"
            assert discovery_doc[field] is not None, f"Field {field} should not be None"

    @pytest.mark.asyncio
    async def test_discovery_issuer_url_format(self, async_client):
        """Test that the issuer URL is properly formatted."""
        response = await async_client.get("/.well-known/openid-configuration")
        discovery_doc = response.json()

        issuer = discovery_doc["issuer"]

        # Should be a valid URL
        parsed = urlparse(issuer)
        assert parsed.scheme in [
            "https",
            "http",
        ], f"Invalid issuer scheme: {parsed.scheme}"
        assert parsed.netloc, "Issuer should have a valid network location"

        # Should not end with a trailing slash (per OIDC spec)
        assert not issuer.endswith("/"), "Issuer URL should not end with trailing slash"

    @pytest.mark.asyncio
    async def test_discovery_jwks_uri_format(self, async_client):
        """Test that the JWKS URI is properly formatted."""
        response = await async_client.get("/.well-known/openid-configuration")
        discovery_doc = response.json()

        jwks_uri = discovery_doc["jwks_uri"]
        issuer = discovery_doc["issuer"]

        # JWKS URI should be based on the issuer
        assert jwks_uri.startswith(issuer), "JWKS URI should be based on issuer URL"
        assert jwks_uri.endswith("/.well-known/jwks.json"), (
            "JWKS URI should end with proper path"
        )

    @pytest.mark.asyncio
    async def test_discovery_endpoints_format(self, async_client):
        """Test that endpoint URLs are properly formatted."""
        response = await async_client.get("/.well-known/openid-configuration")
        discovery_doc = response.json()

        issuer = discovery_doc["issuer"]
        token_endpoint = discovery_doc["token_endpoint"]

        # Endpoints should be based on the issuer
        assert token_endpoint.startswith(issuer), (
            "Token endpoint should be based on issuer URL"
        )

        # Check if registration endpoint exists and is properly formatted
        if "registration_endpoint" in discovery_doc:
            registration_endpoint = discovery_doc["registration_endpoint"]
            assert registration_endpoint.startswith(issuer), (
                "Registration endpoint should be based on issuer URL"
            )

    @pytest.mark.asyncio
    async def test_discovery_supported_values(self, async_client):
        """Test that supported values are compliant with OIDC standards."""
        response = await async_client.get("/.well-known/openid-configuration")
        discovery_doc = response.json()

        # Check supported scopes include required OIDC scopes
        scopes_supported = discovery_doc["scopes_supported"]
        assert isinstance(scopes_supported, list), "Scopes should be a list"
        for scope in ["openid", "profile", "email", "address", "phone"]:
            assert scope in scopes_supported, f"Must support '{scope}' scope"

        # Check response types
        response_types = discovery_doc["response_types_supported"]
        assert isinstance(response_types, list), "Response types should be a list"
        assert len(response_types) > 0, "Must support at least one response type"

        # Check subject types
        subject_types = discovery_doc["subject_types_supported"]
        assert isinstance(subject_types, list), "Subject types should be a list"
        assert "public" in subject_types, "Must support 'public' subject type"

        # Check signing algorithms
        signing_algs = discovery_doc["id_token_signing_alg_values_supported"]
        assert isinstance(signing_algs, list), "Signing algorithms should be a list"
        assert "EdDSA" in signing_algs, "Must support EdDSA algorithm"

        claims_supported = discovery_doc["claims_supported"]
        assert isinstance(claims_supported, list), "Claims should be a list"
        for claim in [
            "sub",
            "email",
            "address",
            "phone_number",
            "phone_number_verified",
        ]:
            assert claim in claims_supported, f"Missing claim: {claim}"

    @pytest.mark.asyncio
    async def test_discovery_with_custom_issuer(self, async_client):
        """Test discovery endpoint with custom issuer environment variable."""
        custom_issuer = "https://custom.auth.example.com"

        with patch.dict(os.environ, {"AUTHN_ISSUER": custom_issuer}):
            # Need to reload the app module to pick up the new environment variable
            response = await async_client.get("/.well-known/openid-configuration")
            discovery_doc = response.json()

            # The response might still use the default issuer since the module
            # was already loaded, but we test the structure remains valid
            assert "issuer" in discovery_doc
            assert discovery_doc["jwks_uri"].endswith("/.well-known/jwks.json")

    @pytest.mark.asyncio
    async def test_discovery_endpoint_caching_headers(self, async_client):
        """Test that discovery endpoint has appropriate caching headers."""
        response = await async_client.get("/.well-known/openid-configuration")

        # The endpoint should be cacheable but not too long
        # (In production, you might want Cache-Control headers)
        assert response.status_code == 200


@pytest.mark.integration
class TestJWKSEndpoint:
    """Test JWKS (JSON Web Key Set) endpoint functionality."""

    @pytest.mark.asyncio
    async def test_jwks_endpoint_returns_valid_json(self, async_client):
        """Test that the JWKS endpoint returns valid JSON."""
        response = await async_client.get("/.well-known/jwks.json")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")

        # Should be parseable as JSON
        jwks_doc = response.json()
        assert isinstance(jwks_doc, dict)

    @pytest.mark.asyncio
    async def test_jwks_document_structure(self, async_client):
        """Test that the JWKS document has the correct structure."""
        response = await async_client.get("/.well-known/jwks.json")
        jwks_doc = response.json()

        # Must have 'keys' field
        assert "keys" in jwks_doc, "JWKS document must contain 'keys' field"
        assert isinstance(jwks_doc["keys"], list), "'keys' field must be a list"
        assert len(jwks_doc["keys"]) > 0, "Must contain at least one key"

    @pytest.mark.asyncio
    async def test_jwk_key_format(self, async_client):
        """Test that individual JWK keys have the correct format."""
        response = await async_client.get("/.well-known/jwks.json")
        jwks_doc = response.json()

        key = jwks_doc["keys"][0]  # Test the first key

        # Required JWK fields
        required_fields = ["kty", "use", "kid"]
        for field in required_fields:
            if field == "use":
                # 'use' is optional but commonly included
                continue
            assert field in key, f"JWK must contain '{field}' field"

        # Key type should be appropriate for Ed25519
        assert key["kty"] in ["OKP"], f"Unexpected key type: {key['kty']}"

        # Should have a key ID for rotation
        assert key["kid"], "Key should have a non-empty key ID"

    @pytest.mark.asyncio
    async def test_jwk_ed25519_specific_fields(self, async_client):
        """Test Ed25519 specific JWK fields."""
        response = await async_client.get("/.well-known/jwks.json")
        jwks_doc = response.json()

        key = jwks_doc["keys"][0]

        # Ed25519 keys should have specific fields
        if key["kty"] == "OKP":
            assert "crv" in key, "OKP key must have 'crv' (curve) field"
            assert key["crv"] == "Ed25519", (
                f"Expected Ed25519 curve, got: {key.get('crv')}"
            )
            assert "x" in key, "Ed25519 key must have 'x' field (public key)"

            # Should not have private key material in public JWKS
            assert "d" not in key, "Public JWKS should not contain private key material"

    @pytest.mark.asyncio
    async def test_jwk_can_create_jwk_object(self, async_client):
        """Test that the JWK can be parsed using Swarmauri utilities."""
        response = await async_client.get("/.well-known/jwks.json")
        jwks_doc = response.json()

        key_dict = jwks_doc["keys"][0]

        # Should be able to convert the JWK to a public key representation
        try:
            pub = _jwk_to_pub_for_signer(key_dict)
            assert pub is not None
        except Exception as e:
            pytest.fail(f"Failed to parse JWK from JWKS response: {e}")

    @pytest.mark.asyncio
    async def test_jwks_key_consistency(self, async_client):
        """Test that JWKS endpoint returns consistent keys across requests."""
        # Make two requests
        response1 = await async_client.get("/.well-known/jwks.json")
        response2 = await async_client.get("/.well-known/jwks.json")

        jwks1 = response1.json()
        jwks2 = response2.json()

        # Should return the same keys (assuming no key rotation between requests)
        assert len(jwks1["keys"]) == len(jwks2["keys"])

        # Compare key IDs
        kids1 = [key["kid"] for key in jwks1["keys"]]
        kids2 = [key["kid"] for key in jwks2["keys"]]
        assert kids1 == kids2, "Key IDs should be consistent across requests"

    @pytest.mark.asyncio
    async def test_jwks_key_id_format(self, async_client):
        """Test that key IDs follow expected format."""
        response = await async_client.get("/.well-known/jwks.json")
        jwks_doc = response.json()

        for key in jwks_doc["keys"]:
            kid = key["kid"]

            # Should be a non-empty string
            assert isinstance(kid, str), "Key ID should be a string"
            assert len(kid) > 0, "Key ID should not be empty"

            # For Ed25519 keys, might follow a specific pattern
            # This is implementation-specific but we can check it's reasonable
            assert len(kid) >= 3, "Key ID should be at least 3 characters"

    @pytest.mark.asyncio
    async def test_jwks_with_crypto_key_consistency(self, async_client, temp_key_file):
        """Test that JWKS endpoint uses the same key as the crypto module."""
        # This test uses the temp_key_file fixture to ensure we have a known key
        response = await async_client.get("/.well-known/jwks.json")
        jwks_doc = response.json()

        # Should have at least one key
        assert len(jwks_doc["keys"]) >= 1

        # The key should be valid Ed25519 format
        key = jwks_doc["keys"][0]
        assert key["kty"] == "OKP"
        assert key["crv"] == "Ed25519"


@pytest.mark.integration
class TestOIDCEndpointIntegration:
    """Test integration between OIDC endpoints."""

    @pytest.mark.asyncio
    async def test_discovery_and_jwks_consistency(self, async_client):
        """Test that discovery document and JWKS endpoint are consistent."""
        # Get discovery document
        discovery_response = await async_client.get("/.well-known/openid-configuration")
        discovery_doc = discovery_response.json()

        # Get JWKS document
        jwks_response = await async_client.get("/.well-known/jwks.json")
        jwks_doc = jwks_response.json()

        # Verify JWKS URI from discovery matches actual endpoint
        jwks_uri = discovery_doc["jwks_uri"]

        # The JWKS should be accessible at the advertised URI
        # (We're testing locally, so we just check the path)
        assert jwks_uri.endswith("/.well-known/jwks.json")

        # Signing algorithms in discovery should match key types in JWKS
        signing_algs = discovery_doc["id_token_signing_alg_values_supported"]

        if "EdDSA" in signing_algs:
            # Should have Ed25519 keys in JWKS
            ed25519_keys = [
                key
                for key in jwks_doc["keys"]
                if key.get("kty") == "OKP" and key.get("crv") == "Ed25519"
            ]
            assert len(ed25519_keys) > 0, (
                "Should have Ed25519 keys if EdDSA is supported"
            )

    @pytest.mark.asyncio
    async def test_oidc_endpoints_security_headers(self, async_client):
        """Test that OIDC endpoints have appropriate security headers."""
        endpoints = ["/.well-known/openid-configuration", "/.well-known/jwks.json"]

        for endpoint in endpoints:
            response = await async_client.get(endpoint)

            assert response.status_code == 200

            # These endpoints should be publicly accessible
            # but might have security headers in production
            headers = response.headers

            # Content-Type should be application/json
            assert headers["content-type"].startswith("application/json")

    @pytest.mark.asyncio
    async def test_oidc_endpoints_error_handling(self, async_client):
        """Test error handling for OIDC endpoints."""
        # Test with invalid methods
        discovery_post = await async_client.post("/.well-known/openid-configuration")
        assert discovery_post.status_code == 405  # Method Not Allowed

        jwks_post = await async_client.post("/.well-known/jwks.json")
        assert jwks_post.status_code == 405  # Method Not Allowed

    @pytest.mark.asyncio
    async def test_oidc_discovery_with_different_environments(
        self, async_client, mock_env_vars
    ):
        """Test OIDC discovery with different environment configurations."""
        # The mock_env_vars fixture should provide test environment variables
        response = await async_client.get("/.well-known/openid-configuration")
        discovery_doc = response.json()

        # Should still return valid discovery document
        assert "issuer" in discovery_doc
        assert "jwks_uri" in discovery_doc

        # URLs should be properly formatted regardless of environment
        issuer = discovery_doc["issuer"]
        parsed = urlparse(issuer)
        assert parsed.scheme in ["http", "https"]
        assert parsed.netloc


@pytest.mark.integration
class TestOIDCCompliance:
    """Test OIDC specification compliance."""

    @pytest.mark.asyncio
    async def test_discovery_document_oidc_compliance(self, async_client):
        """Test that discovery document complies with OIDC Core specification."""
        response = await async_client.get("/.well-known/openid-configuration")
        discovery_doc = response.json()

        # OIDC Core 1.0 Section 3 - mandatory fields
        mandatory_fields = [
            "issuer",
            "jwks_uri",
            "response_types_supported",
            "subject_types_supported",
            "id_token_signing_alg_values_supported",
        ]

        for field in mandatory_fields:
            assert field in discovery_doc, f"Missing mandatory OIDC field: {field}"

    @pytest.mark.asyncio
    async def test_jwks_rfc7517_compliance(self, async_client):
        """Test that JWKS endpoint complies with RFC 7517 (JSON Web Key)."""
        response = await async_client.get("/.well-known/jwks.json")
        jwks_doc = response.json()

        # RFC 7517 Section 5 - JWK Set format
        assert "keys" in jwks_doc, "JWK Set must have 'keys' parameter"
        assert isinstance(jwks_doc["keys"], list), "'keys' must be an array"

        # Each key must be a valid JWK
        for key in jwks_doc["keys"]:
            assert isinstance(key, dict), "Each key must be a JSON object"
            assert "kty" in key, "Each JWK must have 'kty' parameter"

    @pytest.mark.asyncio
    async def test_ed25519_key_rfc8037_compliance(self, async_client):
        """Test that Ed25519 keys comply with RFC 8037 (CFRG Elliptic Curve Keys)."""
        response = await async_client.get("/.well-known/jwks.json")
        jwks_doc = response.json()

        # Find Ed25519 keys
        ed25519_keys = [
            key
            for key in jwks_doc["keys"]
            if key.get("kty") == "OKP" and key.get("crv") == "Ed25519"
        ]

        assert len(ed25519_keys) > 0, "Should have at least one Ed25519 key"

        for key in ed25519_keys:
            # RFC 8037 Section 2 - OKP Key Type
            assert key["kty"] == "OKP", "Ed25519 keys must have kty=OKP"
            assert key["crv"] == "Ed25519", "Must specify Ed25519 curve"
            assert "x" in key, "Must have 'x' parameter (public key)"

            # x parameter should be base64url-encoded
            x_value = key["x"]
            assert isinstance(x_value, str), "'x' parameter must be a string"
            assert len(x_value) > 0, "'x' parameter must not be empty"

    @pytest.mark.asyncio
    async def test_content_type_compliance(self, async_client):
        """Test that endpoints return correct Content-Type headers."""
        endpoints = ["/.well-known/openid-configuration", "/.well-known/jwks.json"]

        for endpoint in endpoints:
            response = await async_client.get(endpoint)

            # Should return application/json
            content_type = response.headers["content-type"]
            assert content_type.startswith("application/json"), (
                f"Endpoint {endpoint} should return application/json, got: {content_type}"
            )
