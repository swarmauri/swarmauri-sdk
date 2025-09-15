"""tigrbl_auth – OAuth utilities and helpers.

This package aggregates optional helpers for various OAuth 2.0 RFCs such as
RFC 7636 (PKCE), RFC 8705 (mutual-TLS client authentication), and RFC 9396
(Rich Authorization Requests).
"""

from .rfc.rfc7636_pkce import (
    makeCodeChallenge,
    makeCodeVerifier,
    verify_code_challenge,
    create_code_challenge,
    create_code_verifier,
)
from .rfc.rfc8628 import (
    generate_device_code,
    generate_user_code,
    validate_user_code,
    RFC8628_SPEC_URL,
)
from .rfc.rfc9396 import (
    AuthorizationDetail,
    parse_authorization_details,
    RFC9396_SPEC_URL,
)

from .rfc.rfc6750 import extract_bearer_token
from .rfc import rfc7662, rfc7591, rfc7592, rfc9101
from .rfc.rfc7662 import introspect_token, register_token, reset_tokens
from .rfc.rfc9207 import RFC9207_SPEC_URL, extract_issuer
from .rfc.rfc8932 import RFC8932_SPEC_URL, enforce_encrypted_dns
from .rfc.rfc8707 import extract_resource, RFC8707_SPEC_URL
from .rfc.rfc8705 import (
    RFC8705_SPEC_URL,
    thumbprint_from_cert_pem,
    validate_certificate_binding,
)
from .rfc.rfc8252 import is_native_redirect_uri, validate_native_redirect_uri
from .rfc.rfc7638 import jwk_thumbprint, verify_jwk_thumbprint
from .rfc.rfc7800 import add_cnf_claim, verify_proof_of_possession
from .rfc.rfc8291 import encrypt_push_message, decrypt_push_message, RFC8291_SPEC_URL
from .rfc.rfc8812 import (
    is_webauthn_algorithm,
    WEBAUTHN_ALGORITHMS,
    RFC8812_SPEC_URL,
)
from .rfc.rfc9068 import add_rfc9068_claims, validate_rfc9068_claims
from .rfc.rfc8037 import sign_eddsa, verify_eddsa, RFC8037_SPEC_URL
from .rfc.rfc8176 import (
    validate_amr_claim,
    AMR_VALUES,
    RFC8176_SPEC_URL,
)

from .rfc.rfc7515 import sign_jws, verify_jws
from .rfc.rfc7516 import encrypt_jwe, decrypt_jwe
from .rfc.rfc7517 import load_signing_jwk, load_public_jwk
from .rfc.rfc7518 import supported_algorithms
from .rfc.rfc7519 import encode_jwt, decode_jwt

from .rfc.rfc7520 import jws_then_jwe, jwe_then_jws, RFC7520_SPEC_URL
from .rfc.rfc7591 import RFC7591_SPEC_URL
from .rfc.rfc7592 import RFC7592_SPEC_URL

from .rfc.rfc7521 import validate_jwt_assertion, RFC7521_SPEC_URL
from .rfc.rfc7523 import validate_client_jwt_bearer, RFC7523_SPEC_URL

# New RFC implementations
from .rfc.rfc8523 import (
    validate_enhanced_jwt_bearer,
    makeClientAssertionJwt,
    is_jwt_replay,
    RFC8523_SPEC_URL,
    create_client_assertion_jwt,
)
from .rfc.rfc7952 import (
    makeSecurityEventToken,
    validate_security_event_token,
    extract_event_data,
    get_set_subject_identifiers,
    makeAccountDisabledSet,
    makeSessionRevokedSet,
    SET_EVENT_TYPES,
    RFC7952_SPEC_URL,
    create_security_event_token,
    create_account_disabled_set,
    create_session_revoked_set,
)
from .rfc.rfc8693 import (
    TokenExchangeRequest,
    TokenExchangeResponse,
    TokenType,
    validate_token_exchange_request,
    validate_subject_token,
    exchange_token,
    makeImpersonationToken,
    makeDelegationToken,
    TOKEN_EXCHANGE_GRANT_TYPE,
    RFC8693_SPEC_URL,
    include_rfc8693,
    create_impersonation_token,
    create_delegation_token,
)
from .rfc.rfc8932 import (
    get_enhanced_authorization_server_metadata,
    validate_metadata_consistency,
    get_capability_matrix,
)

from .oidc_id_token import mint_id_token, verify_id_token

__all__ = [
    "makeCodeVerifier",
    "makeCodeChallenge",
    "verify_code_challenge",
    "create_code_verifier",
    "create_code_challenge",
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
    "RFC7591_SPEC_URL",
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
    "makeClientAssertionJwt",
    "is_jwt_replay",
    "RFC8523_SPEC_URL",
    "makeSecurityEventToken",
    "validate_security_event_token",
    "extract_event_data",
    "get_set_subject_identifiers",
    "makeAccountDisabledSet",
    "makeSessionRevokedSet",
    "SET_EVENT_TYPES",
    "RFC7952_SPEC_URL",
    "TokenExchangeRequest",
    "TokenExchangeResponse",
    "TokenType",
    "validate_token_exchange_request",
    "validate_subject_token",
    "exchange_token",
    "makeImpersonationToken",
    "makeDelegationToken",
    "TOKEN_EXCHANGE_GRANT_TYPE",
    "RFC8693_SPEC_URL",
    "include_rfc8693",
    "create_client_assertion_jwt",
    "create_security_event_token",
    "create_account_disabled_set",
    "create_session_revoked_set",
    "create_impersonation_token",
    "create_delegation_token",
    "get_enhanced_authorization_server_metadata",
    "validate_metadata_consistency",
    "get_capability_matrix",
    "RFC8932_SPEC_URL",
    "rfc7591",
    "rfc7592",
    "rfc7662",
    "rfc9101",
    "mint_id_token",
    "verify_id_token",
]
