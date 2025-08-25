"""auto_authn.v2 – OAuth utilities and helpers.

This package aggregates optional helpers for various OAuth 2.0 RFCs such as
RFC 7636 (PKCE), RFC 8705 (mutual-TLS client authentication), and RFC 9396
(Rich Authorization Requests).
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
from .rfc9396 import (
    AuthorizationDetail,
    parse_authorization_details,
    RFC9396_SPEC_URL,
)

from .rfc6750 import extract_bearer_token
from .rfc7662 import introspect_token, register_token, reset_tokens
from .rfc9207 import RFC9207_SPEC_URL, extract_issuer
from .rfc8932 import RFC8932_SPEC_URL, enforce_encrypted_dns
from .rfc9126 import store_par_request, get_par_request, reset_par_store
from .rfc8707 import extract_resource, RFC8707_SPEC_URL
from .rfc8705 import (
    RFC8705_SPEC_URL,
    thumbprint_from_cert_pem,
    validate_certificate_binding,
)
from .rfc8252 import is_native_redirect_uri, validate_native_redirect_uri
from .rfc7638 import jwk_thumbprint, verify_jwk_thumbprint
from .rfc7800 import add_cnf_claim, verify_proof_of_possession
from .rfc8291 import encrypt_push_message, decrypt_push_message, RFC8291_SPEC_URL
from .rfc8812 import (
    is_webauthn_algorithm,
    WEBAUTHN_ALGORITHMS,
    RFC8812_SPEC_URL,
)
from .rfc9068 import add_rfc9068_claims, validate_rfc9068_claims
from .rfc8037 import sign_eddsa, verify_eddsa, RFC8037_SPEC_URL
from .rfc8176 import (
    validate_amr_claim,
    AMR_VALUES,
    RFC8176_SPEC_URL,
)

from .rfc7515 import sign_jws, verify_jws
from .rfc7516 import encrypt_jwe, decrypt_jwe
from .rfc7517 import load_signing_jwk, load_public_jwk
from .rfc7518 import supported_algorithms
from .rfc7519 import encode_jwt, decode_jwt

from .rfc7520 import jws_then_jwe, jwe_then_jws, RFC7520_SPEC_URL
from .rfc7591 import (
    register_client,
    get_client,
    reset_client_registry,
    RFC7591_SPEC_URL,
)
from .rfc7592 import update_client, delete_client, RFC7592_SPEC_URL

from .rfc7521 import validate_jwt_assertion, RFC7521_SPEC_URL
from .rfc7523 import validate_client_jwt_bearer, RFC7523_SPEC_URL

# New RFC implementations
from .rfc8523 import (
    validate_enhanced_jwt_bearer,
    create_client_assertion_jwt,
    is_jwt_replay,
    RFC8523_SPEC_URL,
)
from .rfc7952 import (
    create_security_event_token,
    validate_security_event_token,
    extract_event_data,
    get_set_subject_identifiers,
    create_account_disabled_set,
    create_session_revoked_set,
    SET_EVENT_TYPES,
    RFC7952_SPEC_URL,
)
from .rfc8693 import (
    TokenExchangeRequest,
    TokenExchangeResponse,
    TokenType,
    validate_token_exchange_request,
    validate_subject_token,
    exchange_token,
    create_impersonation_token,
    create_delegation_token,
    TOKEN_EXCHANGE_GRANT_TYPE,
    RFC8693_SPEC_URL,
    include_rfc8693,
)
from .rfc8932 import (
    get_enhanced_authorization_server_metadata,
    validate_metadata_consistency,
    get_capability_matrix,
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
    "RFC9396_SPEC_URL",
    "extract_bearer_token",
    "extract_issuer",
    "extract_resource",
    "RFC8707_SPEC_URL",
    "RFC8705_SPEC_URL",
    "RFC9207_SPEC_URL",
    "enforce_encrypted_dns",
    "RFC8932_SPEC_URL",
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
    "register_client",
    "get_client",
    "reset_client_registry",
    "RFC7591_SPEC_URL",
    "update_client",
    "delete_client",
    "RFC7592_SPEC_URL",
    "jwk_thumbprint",
    "verify_jwk_thumbprint",
    "add_cnf_claim",
    "verify_proof_of_possession",
    "encrypt_push_message",
    "decrypt_push_message",
    "RFC8291_SPEC_URL",
    "is_webauthn_algorithm",
    "WEBAUTHN_ALGORITHMS",
    "RFC8812_SPEC_URL",
    "validate_jwt_assertion",
    "RFC7521_SPEC_URL",
    "RFC7520_SPEC_URL",
    "sign_eddsa",
    "verify_eddsa",
    "RFC8037_SPEC_URL",
    "validate_amr_claim",
    "AMR_VALUES",
    "RFC8176_SPEC_URL",
    "validate_client_jwt_bearer",
    "RFC7523_SPEC_URL",
    # New RFC implementations
    "validate_enhanced_jwt_bearer",
    "create_client_assertion_jwt",
    "is_jwt_replay",
    "RFC8523_SPEC_URL",
    "create_security_event_token",
    "validate_security_event_token",
    "extract_event_data",
    "get_set_subject_identifiers",
    "create_account_disabled_set",
    "create_session_revoked_set",
    "SET_EVENT_TYPES",
    "RFC7952_SPEC_URL",
    "TokenExchangeRequest",
    "TokenExchangeResponse",
    "TokenType",
    "validate_token_exchange_request",
    "validate_subject_token",
    "exchange_token",
    "create_impersonation_token",
    "create_delegation_token",
    "TOKEN_EXCHANGE_GRANT_TYPE",
    "RFC8693_SPEC_URL",
    "include_rfc8693",
    "get_enhanced_authorization_server_metadata",
    "validate_metadata_consistency",
    "get_capability_matrix",
    "RFC8932_SPEC_URL",
]
