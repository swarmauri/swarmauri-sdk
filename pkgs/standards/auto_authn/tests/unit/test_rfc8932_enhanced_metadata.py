"""Tests for RFC 8932: Enhanced OAuth 2.0 Authorization Server Metadata.

See related RFC 8414: OAuth 2.0 Authorization Server Metadata
"""

from unittest.mock import patch

import pytest
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient

from auto_authn.v2.rfc8932 import (
    RFC8932_SPEC_URL,
    get_enhanced_authorization_server_metadata,
    validate_metadata_consistency,
    get_capability_matrix,
    router,
)
from auto_authn.v2.runtime_cfg import settings


@pytest.mark.unit
def test_get_enhanced_authorization_server_metadata_basic():
    """RFC 8932: Get basic enhanced metadata."""
    metadata = get_enhanced_authorization_server_metadata()

    # Basic RFC 8414 fields should be present
    assert "issuer" in metadata
    assert "authorization_endpoint" in metadata
    assert "token_endpoint" in metadata
    assert "jwks_uri" in metadata
    assert "scopes_supported" in metadata
    assert "response_types_supported" in metadata
    assert "grant_types_supported" in metadata

    # Check some expected values
    assert "openid" in metadata["scopes_supported"]
    assert "authorization_code" in metadata["grant_types_supported"]
    assert "EdDSA" in metadata["id_token_signing_alg_values_supported"]


@pytest.mark.unit
def test_get_enhanced_authorization_server_metadata_with_extensions():
    """RFC 8932: Enhanced metadata includes RFC extensions when enabled."""
    with patch.object(settings, "enable_rfc7009", True):
        with patch.object(settings, "enable_rfc7662", True):
            with patch.object(settings, "enable_rfc8628", True):
                metadata = get_enhanced_authorization_server_metadata()

                # RFC 7009 - Token Revocation
                assert "revocation_endpoint" in metadata
                assert metadata["revocation_endpoint"].endswith("/revoke")

                # RFC 7662 - Token Introspection
                assert "introspection_endpoint" in metadata
                assert metadata["introspection_endpoint"].endswith("/introspect")

                # RFC 8628 - Device Authorization Grant
                assert "device_authorization_endpoint" in metadata
                assert (
                    "urn:ietf:params:oauth:grant-type:device_code"
                    in metadata["grant_types_supported"]
                )


@pytest.mark.unit
def test_get_enhanced_authorization_server_metadata_token_exchange():
    """RFC 8932: Token exchange metadata when RFC 8693 is enabled."""
    with patch.object(settings, "enable_rfc8693", True):
        metadata = get_enhanced_authorization_server_metadata()

        assert "token_exchange_endpoint" in metadata
        assert metadata["token_exchange_endpoint"].endswith("/token/exchange")
        assert (
            "urn:ietf:params:oauth:grant-type:token-exchange"
            in metadata["grant_types_supported"]
        )
        assert "token_types_supported" in metadata
        assert (
            "urn:ietf:params:oauth:token-type:access_token"
            in metadata["token_types_supported"]
        )


@pytest.mark.unit
def test_get_enhanced_authorization_server_metadata_mtls():
    """RFC 8932: mTLS metadata when RFC 8705 is enabled."""
    with patch.object(settings, "enable_rfc8705", True):
        metadata = get_enhanced_authorization_server_metadata()

        assert "tls_client_certificate_bound_access_tokens" in metadata
        assert metadata["tls_client_certificate_bound_access_tokens"] is True
        assert "tls_client_auth" in metadata["token_endpoint_auth_methods_supported"]
        assert (
            "self_signed_tls_client_auth"
            in metadata["token_endpoint_auth_methods_supported"]
        )


@pytest.mark.unit
def test_get_enhanced_authorization_server_metadata_dpop():
    """RFC 8932: DPoP metadata when RFC 9449 is enabled."""
    with patch.object(settings, "enable_rfc9449", True):
        metadata = get_enhanced_authorization_server_metadata()

        assert "dpop_signing_alg_values_supported" in metadata
        assert "EdDSA" in metadata["dpop_signing_alg_values_supported"]
        assert "ES256" in metadata["dpop_signing_alg_values_supported"]


@pytest.mark.unit
def test_get_enhanced_authorization_server_metadata_par():
    """RFC 8932: PAR metadata when RFC 9126 is enabled."""
    with patch.object(settings, "enable_rfc9126", True):
        metadata = get_enhanced_authorization_server_metadata()

        assert "pushed_authorization_request_endpoint" in metadata
        assert metadata["pushed_authorization_request_endpoint"].endswith("/par")
        assert "require_pushed_authorization_requests" in metadata


@pytest.mark.unit
def test_get_enhanced_authorization_server_metadata_jwt_access_tokens():
    """RFC 8932: JWT access token metadata when RFC 9068 is enabled."""
    with patch.object(settings, "enable_rfc9068", True):
        metadata = get_enhanced_authorization_server_metadata()

        assert "access_token_issuer" in metadata
        assert "access_token_signing_alg_values_supported" in metadata
        assert "EdDSA" in metadata["access_token_signing_alg_values_supported"]


@pytest.mark.unit
def test_get_enhanced_authorization_server_metadata_resource_indicators():
    """RFC 8932: Resource indicators metadata when RFC 8707 is enabled."""
    with patch.object(settings, "rfc8707_enabled", True):
        metadata = get_enhanced_authorization_server_metadata()

        assert "resource_parameter_supported" in metadata
        assert metadata["resource_parameter_supported"] is True


@pytest.mark.unit
def test_get_enhanced_authorization_server_metadata_rich_authz():
    """RFC 8932: Rich authorization requests metadata when RFC 9396 is enabled."""
    with patch.object(settings, "enable_rfc9396", True):
        metadata = get_enhanced_authorization_server_metadata()

        assert "authorization_details_types_supported" in metadata
        assert "openid_credential" in metadata["authorization_details_types_supported"]


@pytest.mark.unit
def test_get_enhanced_authorization_server_metadata_deduplication():
    """RFC 8932: Metadata should deduplicate list values."""
    with patch.object(settings, "enable_rfc8705", True):
        metadata = get_enhanced_authorization_server_metadata()

        # Check that there are no duplicates in auth methods
        auth_methods = metadata["token_endpoint_auth_methods_supported"]
        assert len(auth_methods) == len(set(auth_methods))

        # Check that there are no duplicates in grant types
        grant_types = metadata["grant_types_supported"]
        assert len(grant_types) == len(set(grant_types))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enhanced_authorization_server_metadata_endpoint():
    """RFC 8932: Enhanced metadata endpoint returns correct data."""
    app = FastAPI()
    app.include_router(router)

    with patch.object(settings, "enable_rfc8932", True):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/.well-known/oauth-authorization-server-enhanced")

        assert resp.status_code == status.HTTP_200_OK
        metadata = resp.json()

        assert "issuer" in metadata
        assert "authorization_endpoint" in metadata
        assert "token_endpoint" in metadata


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enhanced_authorization_server_metadata_endpoint_disabled():
    """RFC 8932: Enhanced metadata endpoint returns 404 when disabled."""
    app = FastAPI()
    app.include_router(router)

    with patch.object(settings, "enable_rfc8932", False):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/.well-known/oauth-authorization-server-enhanced")

        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.unit
def test_validate_metadata_consistency_clean():
    """RFC 8932: Metadata consistency validation with no issues."""
    with patch.object(settings, "enable_rfc7662", True):
        warnings = validate_metadata_consistency()

        # Should have no warnings for consistent configuration
        device_warnings = [w for w in warnings if "device" in w.lower()]
        assert len(device_warnings) == 0


@pytest.mark.unit
def test_validate_metadata_consistency_device_inconsistency():
    """RFC 8932: Detect device authorization inconsistency."""
    with patch.object(settings, "enable_rfc8628", True):
        # Mock metadata that has device endpoint but missing grant type
        with patch(
            "auto_authn.v2.rfc8932.get_enhanced_authorization_server_metadata"
        ) as mock_metadata:
            mock_metadata.return_value = {
                "device_authorization_endpoint": "https://example.com/device_authorization",
                "grant_types_supported": [
                    "authorization_code",
                    "implicit",
                ],  # Missing device_code
            }

            warnings = validate_metadata_consistency()

            device_warnings = [w for w in warnings if "device" in w.lower()]
            assert len(device_warnings) > 0


@pytest.mark.unit
def test_validate_metadata_consistency_introspection_inconsistency():
    """RFC 8932: Detect introspection endpoint inconsistency."""
    with patch.object(settings, "enable_rfc7662", False):
        # Mock metadata that has introspection endpoint but RFC disabled
        with patch(
            "auto_authn.v2.rfc8932.get_enhanced_authorization_server_metadata"
        ) as mock_metadata:
            mock_metadata.return_value = {
                "introspection_endpoint": "https://example.com/introspect",
            }

            warnings = validate_metadata_consistency()

            introspection_warnings = [
                w for w in warnings if "introspection" in w.lower()
            ]
            assert len(introspection_warnings) > 0


@pytest.mark.unit
def test_validate_metadata_consistency_mtls_inconsistency():
    """RFC 8932: Detect mTLS configuration inconsistency."""
    with patch(
        "auto_authn.v2.rfc8932.get_enhanced_authorization_server_metadata"
    ) as mock_metadata:
        mock_metadata.return_value = {
            "tls_client_certificate_bound_access_tokens": True,
            "token_endpoint_auth_methods_supported": [
                "client_secret_basic"
            ],  # Missing mTLS methods
        }

        warnings = validate_metadata_consistency()

        mtls_warnings = [
            w for w in warnings if "mtls" in w.lower() or "tls_client_auth" in w.lower()
        ]
        assert len(mtls_warnings) > 0


@pytest.mark.unit
def test_get_capability_matrix():
    """RFC 8932: Get capability matrix for all RFCs."""
    with patch.object(settings, "enable_rfc7009", True):
        with patch.object(settings, "enable_rfc7662", False):
            matrix = get_capability_matrix()

            # Check structure
            assert "rfc6749" in matrix
            assert "rfc6750" in matrix
            assert "rfc7009" in matrix
            assert "rfc7662" in matrix

            # Check RFC 6749 (always enabled)
            assert matrix["rfc6749"]["enabled"] is True
            assert matrix["rfc6749"]["name"] == "OAuth 2.0 Authorization Framework"
            assert "/authorize" in matrix["rfc6749"]["endpoints"]

            # Check RFC 7009 (enabled in this test)
            assert matrix["rfc7009"]["enabled"] is True
            assert "/revoke" in matrix["rfc7009"]["endpoints"]

            # Check RFC 7662 (disabled in this test)
            assert matrix["rfc7662"]["enabled"] is False
            assert len(matrix["rfc7662"]["endpoints"]) == 0


@pytest.mark.unit
def test_get_capability_matrix_all_enabled():
    """RFC 8932: Capability matrix with all RFCs enabled."""
    with patch.object(settings, "enable_rfc7009", True):
        with patch.object(settings, "enable_rfc7662", True):
            with patch.object(settings, "enable_rfc8414", True):
                with patch.object(settings, "enable_rfc8628", True):
                    with patch.object(settings, "enable_rfc8693", True):
                        matrix = get_capability_matrix()

                        # All should be enabled
                        for rfc_key, rfc_data in matrix.items():
                            if rfc_key in [
                                "rfc7009",
                                "rfc7662",
                                "rfc8414",
                                "rfc8628",
                                "rfc8693",
                            ]:
                                assert rfc_data["enabled"] is True
                                if (
                                    rfc_key != "rfc8414"
                                ):  # Metadata endpoint is different
                                    assert len(rfc_data["endpoints"]) > 0


@pytest.mark.unit
def test_rfc8932_spec_url():
    """RFC 8932: Spec URL should be valid."""
    assert RFC8932_SPEC_URL.startswith("https://")
    assert "8932" in RFC8932_SPEC_URL
