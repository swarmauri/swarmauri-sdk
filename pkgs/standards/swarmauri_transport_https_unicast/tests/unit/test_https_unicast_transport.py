from __future__ import annotations

import base64
import hashlib
import hmac
import tomllib
from pathlib import Path

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from swarmauri_certs_self_signed import SelfSignedCertificate
from swarmauri_core.crypto.types import ExportPolicy, JWAAlg, KeyRef, KeyType, KeyUse
from swarmauri_core.transports import AddressScheme, Feature, Protocol, SecurityMode
from swarmauri_signing_jws import JwsSignerVerifier
from swarmauri_transport_https_unicast import (
    HttpsSecurityPolicy,
    HttpsUnicastTransport,
    http_signature,
)


JWS_KEY = {
    "kind": "raw",
    "key": b"transport-test-secret-32-bytes!!",
    "kid": "body.1",
}


def _self_signed_loopback_cert() -> bytes:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    key_ref = KeyRef(
        kid="https-unicast-test",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=private_pem,
    )
    return SelfSignedCertificate.tls_server("127.0.0.1", ip_addrs=("127.0.0.1",)).issue(
        key_ref
    )


@pytest.mark.unit
def test_supports_https_tls_capabilities() -> None:
    capabilities = HttpsUnicastTransport().supports()

    assert Protocol.HTTP1 in capabilities.protocols
    assert Protocol.TLS in capabilities.protocols
    assert AddressScheme.HTTPS in capabilities.schemes
    assert Feature.ENCRYPTED in capabilities.features
    assert Feature.AUTHENTICATED in capabilities.features
    assert capabilities.security is SecurityMode.TLS


@pytest.mark.unit
def test_cipher_suite_accepts_valid_tls13_ciphers() -> None:
    transport = HttpsUnicastTransport()
    descriptor = transport.cipher_descriptor

    assert descriptor["alg"] == "TLS_AES_256_GCM_SHA384"
    assert transport.allowed_tls_cipher(descriptor["alg"]) is True
    assert transport.allowed_tls_cipher("TLS_AES_128_GCM_SHA256") is True
    assert transport.allowed_tls_cipher("TLS_CHACHA20_POLY1305_SHA256") is True


@pytest.mark.unit
def test_cipher_suite_rejects_invalid_or_legacy_ciphers() -> None:
    transport = HttpsUnicastTransport()

    assert transport.allowed_tls_cipher("TLS_RSA_WITH_AES_128_CBC_SHA") is False
    assert transport.allowed_tls_cipher("AES-256-GCM") is False
    assert transport.allowed_tls_cipher("") is False


@pytest.mark.unit
def test_entry_point_metadata_is_registered() -> None:
    pyproject = tomllib.loads(
        (Path(__file__).resolve().parents[2] / "pyproject.toml").read_text(
            encoding="utf-8"
        )
    )

    assert (
        pyproject["project"]["entry-points"]["swarmauri.transports"][
            "HttpsUnicastTransport"
        ]
        == "swarmauri_transport_https_unicast:HttpsUnicastTransport"
    )


@pytest.mark.unit
def test_http_signature_uses_httpsig_hmac_shape() -> None:
    expected = base64.b64encode(
        hmac.new(b"secret", b"payload", hashlib.sha256).digest()
    ).decode("ascii")

    assert http_signature("secret", b"payload") == expected


@pytest.mark.unit
@pytest.mark.asyncio
async def test_request_applies_security_headers_and_verifies_response_jws() -> None:
    response_body = b'{"ok":true}'
    jws = JwsSignerVerifier()
    response_jws = await jws.sign_compact(
        payload=response_body,
        alg=JWAAlg.HS256,
        key=JWS_KEY,
        kid=JWS_KEY["kid"],
        typ="JWS",
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        request_body = await request.aread()
        assert request.headers["Authorization"] == "Bearer test-token"
        assert request.headers["X-Signature"] == http_signature(
            "shared-secret", request_body
        )
        request_jws = request.headers["X-Body-JWS"]
        verified = await jws.verify_compact(
            request_jws, hmac_keys=[JWS_KEY], alg_allowlist=[JWAAlg.HS256]
        )
        assert verified.payload == request_body
        return httpx.Response(
            200,
            content=response_body,
            headers={"X-Response-JWS": response_jws},
        )

    policy = HttpsSecurityPolicy(
        bearer_token="test-token",
        http_signature_secret="shared-secret",
        request_jws_key=JWS_KEY,
        request_jws_kid=JWS_KEY["kid"],
        response_jws_key=JWS_KEY,
    )
    transport = HttpsUnicastTransport(
        base_url="https://example.test",
        verify=False,
        security_policy=policy,
        require_response_jws=True,
        httpx_transport=httpx.MockTransport(handler),
    )

    status, headers, body = await transport.request("POST", "/orders", body=b"{}")

    assert status == 200
    assert body == response_body
    assert headers["x-response-jws"] == response_jws
    assert transport.last_evidence.response_jws_verified is True
    assert transport.last_evidence.cipher_alg == "TLS_AES_256_GCM_SHA384"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_certificate_preflight_verifies_x509_trust_root() -> None:
    cert_pem = _self_signed_loopback_cert()
    transport = HttpsUnicastTransport()

    result = await transport.verify_certificate(cert_pem, trust_roots=[cert_pem])

    assert result["valid"] is True
    assert result["subject"] == "CN=127.0.0.1"
    assert transport.last_evidence.certificate_valid is True
