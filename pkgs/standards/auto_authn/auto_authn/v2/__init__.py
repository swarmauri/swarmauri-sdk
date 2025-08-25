"""auto_authn.v2 – OAuth utilities and helpers.

This package aggregates optional helpers for various OAuth 2.0 RFCs such as
RFC 7636 (PKCE) and RFC 8705 (mutual-TLS client authentication).
"""

from .rfc7636_pkce import (
    create_code_challenge,
    create_code_verifier,
    verify_code_challenge,
)
from .rfc9396 import AuthorizationDetail, parse_authorization_details
from .rfc6750 import extract_bearer_token
from .rfc7662 import introspect_token, register_token, reset_tokens
from .rfc8705 import thumbprint_from_cert_pem, validate_certificate_binding

__all__ = [
    "create_code_verifier",
    "create_code_challenge",
    "verify_code_challenge",
    "parse_authorization_details",
    "AuthorizationDetail",
    "extract_bearer_token",
    "introspect_token",
    "register_token",
    "reset_tokens",
    "thumbprint_from_cert_pem",
    "validate_certificate_binding",
]
