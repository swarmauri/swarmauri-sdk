"""auto_authn.v2 – OAuth utilities and helpers.

This package aggregates optional helpers for various OAuth 2.0 RFCs such as
RFC 7636 (PKCE) and RFC 8705 (mutual-TLS client authentication).
"""

from .rfc7636_pkce import (
    create_code_challenge,
    create_code_verifier,
    verify_code_challenge,
)
from .rfc8628 import generate_device_code, generate_user_code, validate_user_code
from .rfc9396 import AuthorizationDetail, parse_authorization_details
from .rfc6750 import extract_bearer_token
from .rfc7662 import introspect_token, register_token, reset_tokens
from .rfc8707 import extract_resource, RFC8707_SPEC_URL
from .rfc8705 import thumbprint_from_cert_pem, validate_certificate_binding
from .rfc8252 import is_native_redirect_uri, validate_native_redirect_uri
__all__ = [
    "create_code_verifier",
    "create_code_challenge",
    "verify_code_challenge",
    "generate_user_code",
    "validate_user_code",
    "generate_device_code",
    "parse_authorization_details",
    "AuthorizationDetail",
    "extract_bearer_token",
    "extract_resource",
    "RFC8707_SPEC_URL",
    "introspect_token",
    "register_token",
    "reset_tokens",
    "thumbprint_from_cert_pem",
    "validate_certificate_binding",
    "is_native_redirect_uri",
    "validate_native_redirect_uri",
]
