"""RFC 8932 - OAuth 2.0 Authorization Server Metadata Extensions.

This module provides extended authorization server metadata functionality
beyond the basic RFC 8414 implementation. It includes additional metadata
fields and capabilities for enhanced OAuth 2.0 server discovery.

Note: RFC 8932 may refer to extensions or updates to authorization server
metadata. This implementation provides enhanced metadata capabilities.

See related: RFC 8414 (OAuth 2.0 Authorization Server Metadata)
"""

from __future__ import annotations


from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, status

from .runtime_cfg import settings
from .rfc8414_metadata import ISSUER, JWKS_PATH

RFC8932_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc8932"

router = APIRouter()

# Supported encrypted DNS transports per RFC 8932 recommendations
ENCRYPTED_DNS_TRANSPORTS = {"DoT", "DoH"}


def enforce_encrypted_dns(transport: str) -> str:
    """Validate that DNS queries use encrypted transports.

    RFC 8932 \u00a75.1.1 recommends that operators ensure DNS queries are sent
    over encrypted transports such as DNS over TLS (DoT) or DNS over HTTPS
    (DoH).

    Args:
        transport: The DNS transport protocol to validate.

    Returns:
        The validated transport string.

    Raises:
        NotImplementedError: If RFC 8932 support is disabled.
        ValueError: If an unencrypted transport is provided.
    """

    if not settings.enable_rfc8932:
        raise NotImplementedError("RFC 8932 is disabled")
    if transport not in ENCRYPTED_DNS_TRANSPORTS:
        raise ValueError("unencrypted DNS transport")
    return transport


def get_enhanced_authorization_server_metadata() -> Dict[str, Any]:
    """Generate enhanced OAuth 2.0 Authorization Server Metadata.

    This extends the basic RFC 8414 metadata with additional capabilities
    and security features supported by the authorization server.

    Returns:
        Dict containing comprehensive authorization server metadata
    """
    # Base metadata from RFC 8414
    base_metadata = {
        "issuer": ISSUER,
        "authorization_endpoint": f"{ISSUER}/authorize",
        "token_endpoint": f"{ISSUER}/token",
        "jwks_uri": f"{ISSUER}{JWKS_PATH}",
        "scopes_supported": ["openid", "profile", "email", "address", "phone"],
        "response_types_supported": [
            "code",
            "token",
            "id_token",
            "code token",
            "code id_token",
            "token id_token",
            "code token id_token",
        ],
        "grant_types_supported": [
            "authorization_code",
            "implicit",
            "password",
            "client_credentials",
            "refresh_token",
        ],
        "subject_types_supported": ["public", "pairwise"],
        "id_token_signing_alg_values_supported": ["EdDSA", "RS256", "ES256"],
        "token_endpoint_auth_methods_supported": [
            "client_secret_basic",
            "client_secret_post",
            "private_key_jwt",
            "client_secret_jwt",
        ],
        "claims_supported": ["sub", "name", "email", "address", "phone_number"],
        "code_challenge_methods_supported": ["S256"],
    }
    if settings.enable_rfc7591:
        base_metadata["registration_endpoint"] = f"{ISSUER}/register"

    # Enhanced metadata extensions
    enhanced_metadata = {}

    # RFC 7009 - Token Revocation
    if settings.enable_rfc7009:
        enhanced_metadata["revocation_endpoint"] = f"{ISSUER}/revoked_tokens/revoke"
        enhanced_metadata["revocation_endpoint_auth_methods_supported"] = [
            "client_secret_basic",
            "client_secret_post",
        ]

    # RFC 7662 - Token Introspection
    if settings.enable_rfc7662:
        enhanced_metadata["introspection_endpoint"] = f"{ISSUER}/introspect"
        enhanced_metadata["introspection_endpoint_auth_methods_supported"] = [
            "client_secret_basic",
            "client_secret_post",
        ]

    # RFC 8628 - Device Authorization Grant
    if settings.enable_rfc8628:
        enhanced_metadata["device_authorization_endpoint"] = (
            f"{ISSUER}/device_codes/device_authorization"
        )
        base_metadata["grant_types_supported"].append(
            "urn:ietf:params:oauth:grant-type:device_code"
        )

    # RFC 8693 - Token Exchange
    if settings.enable_rfc8693:
        enhanced_metadata["token_exchange_endpoint"] = f"{ISSUER}/token/exchange"
        base_metadata["grant_types_supported"].append(
            "urn:ietf:params:oauth:grant-type:token-exchange"
        )
        enhanced_metadata["token_types_supported"] = [
            "urn:ietf:params:oauth:token-type:access_token",
            "urn:ietf:params:oauth:token-type:refresh_token",
            "urn:ietf:params:oauth:token-type:id_token",
            "urn:ietf:params:oauth:token-type:jwt",
        ]

    # RFC 8705 - OAuth 2.0 Mutual-TLS Client Authentication
    if settings.enable_rfc8705:
        enhanced_metadata["tls_client_certificate_bound_access_tokens"] = True
        base_metadata["token_endpoint_auth_methods_supported"].extend(
            [
                "tls_client_auth",
                "self_signed_tls_client_auth",
            ]
        )

    # RFC 8707 - Resource Indicators
    if settings.rfc8707_enabled:
        enhanced_metadata["resource_parameter_supported"] = True

    # RFC 9126 - Pushed Authorization Requests
    if settings.enable_rfc9126:
        enhanced_metadata["pushed_authorization_request_endpoint"] = f"{ISSUER}/par"
        enhanced_metadata["require_pushed_authorization_requests"] = False

    # RFC 9449 - DPoP (Demonstrating Proof-of-Possession)
    if settings.enable_rfc9449:
        enhanced_metadata["dpop_signing_alg_values_supported"] = [
            "EdDSA",
            "ES256",
            "RS256",
        ]

    # RFC 9068 - JWT Access Token Profile
    if settings.enable_rfc9068:
        enhanced_metadata["access_token_issuer"] = ISSUER
        enhanced_metadata["access_token_signing_alg_values_supported"] = [
            "EdDSA",
            "RS256",
        ]

    # RFC 9396 - Rich Authorization Requests
    if settings.enable_rfc9396:
        enhanced_metadata["authorization_details_types_supported"] = [
            "openid_credential",
            "payment_initiation",
            "account_information",
        ]

    # Security and capability indicators
    enhanced_metadata.update(
        {
            "request_parameter_supported": True,
            "request_uri_parameter_supported": True,
            "require_request_uri_registration": False,
            "claims_parameter_supported": True,
            "frontchannel_logout_supported": True,
            "frontchannel_logout_session_supported": True,
            "backchannel_logout_supported": True,
            "backchannel_logout_session_supported": True,
        }
    )

    # Merge base and enhanced metadata
    result = {**base_metadata, **enhanced_metadata}

    # Remove duplicates from lists
    for key in ["grant_types_supported", "token_endpoint_auth_methods_supported"]:
        if key in result:
            result[key] = list(set(result[key]))

    return result


@router.get("/.well-known/oauth-authorization-server-enhanced", include_in_schema=False)
async def enhanced_authorization_server_metadata():
    """Return enhanced OAuth 2.0 Authorization Server Metadata.

    This endpoint provides comprehensive metadata about the authorization
    server's capabilities, including all supported RFC extensions.
    """
    if not settings.enable_rfc8932:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enhanced authorization server metadata disabled",
        )

    return get_enhanced_authorization_server_metadata()


def validate_metadata_consistency() -> List[str]:
    """Validate that the metadata configuration is consistent.

    Returns:
        List of validation warnings/errors
    """
    warnings = []
    metadata = get_enhanced_authorization_server_metadata()

    # Check for inconsistencies
    if "device_authorization_endpoint" in metadata:
        if "urn:ietf:params:oauth:grant-type:device_code" not in metadata.get(
            "grant_types_supported", []
        ):
            warnings.append(
                "Device authorization endpoint present but device_code grant type not supported"
            )

    if "introspection_endpoint" in metadata:
        if not settings.enable_rfc7662:
            warnings.append(
                "Introspection endpoint in metadata but RFC 7662 not enabled"
            )

    if "tls_client_certificate_bound_access_tokens" in metadata:
        if "tls_client_auth" not in metadata.get(
            "token_endpoint_auth_methods_supported", []
        ):
            warnings.append("mTLS tokens supported but mTLS auth method not available")

    return warnings


def get_capability_matrix() -> Dict[str, Dict[str, Any]]:
    """Get a matrix of supported capabilities and their status.

    Returns:
        Dict mapping RFC numbers to their implementation status and endpoints
    """
    return {
        "rfc6749": {
            "name": "OAuth 2.0 Authorization Framework",
            "enabled": True,
            "endpoints": ["/authorize", "/token"],
        },
        "rfc6750": {
            "name": "Bearer Token Usage",
            "enabled": True,
            "endpoints": [],
        },
        "rfc7009": {
            "name": "Token Revocation",
            "enabled": settings.enable_rfc7009,
            "endpoints": ["/revoked_tokens/revoke"] if settings.enable_rfc7009 else [],
        },
        "rfc7662": {
            "name": "Token Introspection",
            "enabled": settings.enable_rfc7662,
            "endpoints": ["/introspect"] if settings.enable_rfc7662 else [],
        },
        "rfc8414": {
            "name": "Authorization Server Metadata",
            "enabled": settings.enable_rfc8414,
            "endpoints": ["/.well-known/oauth-authorization-server"],
        },
        "rfc8628": {
            "name": "Device Authorization Grant",
            "enabled": settings.enable_rfc8628,
            "endpoints": ["/device_codes/device_authorization"]
            if settings.enable_rfc8628
            else [],
        },
        "rfc8693": {
            "name": "Token Exchange",
            "enabled": settings.enable_rfc8693,
            "endpoints": ["/token/exchange"] if settings.enable_rfc8693 else [],
        },
        "rfc8705": {
            "name": "OAuth 2.0 Mutual-TLS",
            "enabled": settings.enable_rfc8705,
            "endpoints": [],
        },
        "rfc8707": {
            "name": "Resource Indicators",
            "enabled": settings.rfc8707_enabled,
            "endpoints": [],
        },
        "rfc9126": {
            "name": "Pushed Authorization Requests",
            "enabled": settings.enable_rfc9126,
            "endpoints": ["/par"] if settings.enable_rfc9126 else [],
        },
        "rfc9449": {
            "name": "DPoP",
            "enabled": settings.enable_rfc9449,
            "endpoints": [],
        },
    }


__all__ = [
    "enforce_encrypted_dns",
    "get_enhanced_authorization_server_metadata",
    "enhanced_authorization_server_metadata",
    "validate_metadata_consistency",
    "get_capability_matrix",
    "router",
    "RFC8932_SPEC_URL",
    "enforce_encrypted_dns",
]
