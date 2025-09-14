import base64
import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tigrbl_auth.rfc9449_dpop import create_proof, jwk_from_public_key, jwk_thumbprint
from tigrbl_auth.rfc8693 import (
    TOKEN_EXCHANGE_GRANT_TYPE,
    TokenExchangeRequest,
    TokenType,
    exchange_token,
)
from tigrbl_auth.jwtoken import JWTCoder
from tigrbl_auth.rfc7519 import encode_jwt
from tigrbl_auth import runtime_cfg


def _stub_verify(proof: str, method: str, url: str, jkt: str | None = None) -> str:
    header = json.loads(base64.urlsafe_b64decode(proof.split(".")[0] + "=="))
    thumb = jwk_thumbprint(header["jwk"])
    if jkt and thumb != jkt:
        raise ValueError("jkt mismatch")
    return thumb


def test_worker_enrollment_sender_constrained_flow(monkeypatch):
    private_key = Ed25519PrivateKey.generate()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    jwk = jwk_from_public_key(private_key.public_key())
    jkt = jwk_thumbprint(jwk)

    dpop = create_proof(private_pem, "POST", "https://as.example.com/token")
    monkeypatch.setattr("tigrbl_auth.rfc9449_dpop.verify_proof", _stub_verify)
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc8693", True)

    subject = encode_jwt(sub="user")
    request = TokenExchangeRequest(
        grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
        subject_token=subject,
        subject_token_type=TokenType.JWT.value,
        audience="peagen-gateway",
    )
    response = exchange_token(
        request,
        issuer="issuer",
        jkt=_stub_verify(dpop, "POST", "https://as.example.com/token"),
    )
    payload = JWTCoder.default().decode(response.access_token)
    assert payload["cnf"]["jkt"] == jkt
