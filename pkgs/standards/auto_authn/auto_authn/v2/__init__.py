"""auto_authn.v2 – OAuth utilities and helpers.

This package aggregates optional helpers for various OAuth 2.0 RFCs such as
RFC 7636 (PKCE) and RFC 8705 (mutual-TLS client authentication).
"""

from .rfc7636_pkce import (
    create_code_challenge,
    create_code_verifier,
    verify_code_challenge,
)
from .rfc8628 import (
    generate_device_code,
    generate_user_code,
    validate_user_code,
    RFC8628_SPEC_URL,
)
from .rfc9396 import AuthorizationDetail, parse_authorization_details
from .rfc6750 import extract_bearer_token
from .rfc7662 import introspect_token, register_token, reset_tokens
from .rfc9207 import RFC9207_SPEC_URL, extract_issuer
from .rfc9126 import store_par_request, get_par_request, reset_par_store
from .rfc8707 import extract_resource, RFC8707_SPEC_URL
from .rfc8705 import thumbprint_from_cert_pem, validate_certificate_binding
from .rfc9068 import add_rfc9068_claims, validate_rfc9068_claims
from .rfc8252 import is_native_redirect_uri, validate_native_redirect_uri
from .rfc7515 import sign_jws, verify_jws
from .rfc7516 import encrypt_jwe, decrypt_jwe
from .rfc7517 import load_signing_jwk, load_public_jwk
from .rfc7518 import supported_algorithms
from .rfc7519 import encode_jwt, decode_jwt
from .rfc7520 import jws_then_jwe, jwe_then_jws
from .rfc7521 import extract_client_assertion, RFC7521_SPEC_URL
from .rfc7523 import (
    create_jwt_bearer_assertion,
    verify_jwt_bearer_assertion,
    RFC7523_SPEC_URL,
)

__all__ = [
    "create_code_verifier",
    "create_code_challenge",
    "verify_code_challenge",
    "generate_user_code",
    "validate_user_code",
    "generate_device_code",
    "RFC8628_SPEC_URL",
    "parse_authorization_details",
    "AuthorizationDetail",
    "extract_bearer_token",
    "extract_issuer",
    "extract_resource",
    "RFC8707_SPEC_URL",
    "RFC9207_SPEC_URL",
    "introspect_token",
    "register_token",
    "reset_tokens",
    "store_par_request",
    "get_par_request",
    "reset_par_store",
    "thumbprint_from_cert_pem",
    "validate_certificate_binding",
    "add_rfc9068_claims",
    "validate_rfc9068_claims",
    "is_native_redirect_uri",
    "validate_native_redirect_uri",
    "sign_jws",
    "verify_jws",
    "encrypt_jwe",
    "decrypt_jwe",
    "load_signing_jwk",
    "load_public_jwk",
    "supported_algorithms",
    "encode_jwt",
    "decode_jwt",
    "jws_then_jwe",
    "jwe_then_jws",
    "extract_client_assertion",
    "RFC7521_SPEC_URL",
    "create_jwt_bearer_assertion",
    "verify_jwt_bearer_assertion",
    "RFC7523_SPEC_URL",
]
