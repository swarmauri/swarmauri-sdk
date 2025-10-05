import base64
import json
from typing import Mapping, Optional



import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import SECP256R1

from swarmauri_core.pop import (
    BindType,
    CnfBinding,
    PoPBindingError,
    PoPParseError,
    PoPVerificationError,
    VerifyPolicy,
)
from swarmauri_base.pop import RequestContext

from swarmauri_pop_dpop.dpop import (
    DPoPSigner,
    DPoPVerifier,
    _compute_jwk_thumbprint,
    _resolve_kid,
)


@pytest.fixture
def ec_keypair() -> tuple[ec.EllipticCurvePrivateKey, Mapping[str, str], str]:
    private_key = ec.generate_private_key(SECP256R1())
    public_numbers = private_key.public_key().public_numbers()

    def _encode(value: int) -> str:
        return base64.urlsafe_b64encode(value.to_bytes(32, "big")).rstrip(b"=").decode()

    jwk = {
        "kty": "EC",
        "crv": "P-256",
        "x": _encode(public_numbers.x),
        "y": _encode(public_numbers.y),
    }
    thumbprint = _compute_jwk_thumbprint(jwk)
    return private_key, jwk, thumbprint


class DummyReplay:
    def __init__(self) -> None:
        self.seen_calls: list[tuple[str, str]] = []
        self.mark_calls: list[tuple[str, str, int]] = []

    def seen(self, scope: str, key: str) -> bool:
        self.seen_calls.append((scope, key))
        return False

    def mark(self, scope: str, key: str, ttl_s: int) -> None:
        self.mark_calls.append((scope, key, ttl_s))


class AlwaysSeenReplay:
    def seen(
        self, scope: str, key: str
    ) -> bool:  # pragma: no cover - simple delegation
        return True

    def mark(
        self, scope: str, key: str, ttl_s: int
    ) -> None:  # pragma: no cover - never called
        raise AssertionError("mark should not be called when replay is detected")


class TrackingResolver:
    def __init__(
        self, key: object, *, thumbprint: str, kid: Optional[bytes] = None
    ) -> None:
        self._key = key
        self._thumbprint = thumbprint
        self._kid = kid
        self.kid_queries: list[bytes] = []
        self.thumb_queries: list[CnfBinding] = []

    def by_kid(self, kid: bytes) -> object | None:
        self.kid_queries.append(kid)
        if self._kid and kid == self._kid:
            return self._key
        return None

    def by_thumb(self, bind: CnfBinding) -> object | None:
        self.thumb_queries.append(bind)
        if bind.value_b64u == self._thumbprint:
            return self._key
        return None


class NullResolver:
    def by_kid(self, kid: bytes) -> None:  # pragma: no cover - trivial helper
        return None

    def by_thumb(self, bind: CnfBinding) -> None:  # pragma: no cover - trivial helper
        return None


def _make_header(payload: Mapping[str, object], header: Mapping[str, object]) -> str:
    header_segment = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=")
    payload_segment = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(
        b"="
    )
    signature_segment = base64.urlsafe_b64encode(b"signature").rstrip(b"=")
    return b".".join([header_segment, payload_segment, signature_segment]).decode()


def test_compute_jwk_thumbprint_ec() -> None:
    jwk = {
        "kty": "EC",
        "crv": "P-256",
        "x": "f83OJ3D2xF4gWDhZ5teLoI0lp4rWu-9sYji0m7Rk6nM",
        "y": "x_FEzRu9BX9iN6tZp_mJZbWNoXDp8G26iRwViT8-n6M",
    }
    assert _compute_jwk_thumbprint(jwk) == "D5Iw3MSqY7qCbFQ5gz8JBvxCXkoeLgqbOmgrhXmh9IM"


def test_compute_jwk_thumbprint_rsa() -> None:
    jwk = {
        "kty": "RSA",
        "n": "0vx7agoebGcQSuuPiLJXZptN9nndrXx9jHvdSkZLtueS4omK0VJW6LQn9Q0QgVH8bR_i_zXNXtKgzYV3P6gPl0Q8BCmG5Fi7o3M4ZaChkCGbdF9ersCzXZBfPzlfDsGTi0a5cc0qpAoky6fhiUikens27ayk_iVIbIAXo1Zb1tcHTfbvUodSnb6P0FoYgqD9BfbK3Wlt8X9-7w3LDwW9ki2TkuuzMdGzRNuESyZ3hFbaM4XapCszgmF0wBp-JT5tAM-QsS1d73ZB_pY0V9jvZA67TUrROoUzHB25m_nZg6aj_SA1w4v7w2gw2NXK9enEDJjT2XlHz-3WlEBeIqoQ",
        "e": "AQAB",
    }
    assert _compute_jwk_thumbprint(jwk) == "3yUYYCjJKZBMVIkUnqaePoyUT4Oz-Hj6cBnqcGZNKAw"


def test_compute_jwk_thumbprint_okp() -> None:
    jwk = {
        "kty": "OKP",
        "crv": "Ed25519",
        "x": "11qYAYLefZ8kbZBv41G7AKOrO5NsuU_LYyJCU4s0x8",
    }
    assert _compute_jwk_thumbprint(jwk) == "aapki20nwBGeEcGsXupl2hmbEdHnu4gmfC5eqVpw3Ik"


def test_compute_jwk_thumbprint_missing_kty() -> None:
    with pytest.raises(PoPParseError, match="JWK missing kty"):
        _compute_jwk_thumbprint({})


def test_compute_jwk_thumbprint_unsupported_type() -> None:
    with pytest.raises(PoPParseError, match="Unsupported JWK kty"):
        _compute_jwk_thumbprint({"kty": "oct"})


def test_resolve_kid_none() -> None:
    assert _resolve_kid(None) is None


def test_resolve_kid_str_to_bytes() -> None:
    assert _resolve_kid("test-key") == b"test-key"


def test_signer_cnf_binding_uses_jwk_thumbprint(ec_keypair) -> None:
    private_key, jwk, thumbprint = ec_keypair
    signer = DPoPSigner(private_key=private_key, public_jwk=jwk, algorithm="ES256")
    binding = signer.cnf_binding()
    assert binding.bind_type is BindType.JKT
    assert binding.value_b64u == thumbprint


def test_signer_includes_public_jwk_in_header(monkeypatch, ec_keypair) -> None:
    private_key, jwk, _ = ec_keypair
    signer = DPoPSigner(private_key=private_key, public_jwk=jwk, algorithm="ES256")
    monkeypatch.setattr(DPoPSigner, "_now", lambda self: 1700000000)
    token = signer.sign_request("GET", "https://example.com")
    header = jwt.get_unverified_header(token)
    assert header["typ"] == "dpop+jwt"
    assert header["jwk"] == jwk


def test_signer_includes_kid_header_when_bytes_supplied(
    monkeypatch, ec_keypair
) -> None:
    private_key, jwk, _ = ec_keypair
    signer = DPoPSigner(private_key=private_key, public_jwk=jwk, algorithm="ES256")
    monkeypatch.setattr(DPoPSigner, "_now", lambda self: 1700000000)
    token = signer.sign_request(
        "POST",
        "https://example.com/resource",
        kid=b"kid-value",
        jti="fixed-jti",
    )
    header = jwt.get_unverified_header(token)
    assert header["kid"] == "kid-value"


def test_signer_merges_extra_claims(monkeypatch, ec_keypair) -> None:
    private_key, jwk, _ = ec_keypair
    signer = DPoPSigner(private_key=private_key, public_jwk=jwk, algorithm="ES256")
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPSigner, "_now", lambda self: fixed_time)
    token = signer.sign_request(
        "GET",
        "https://example.com/resource",
        jti="custom-jti",
        extra_claims={"nonce": "abc"},
    )
    payload = jwt.decode(
        token,
        private_key.public_key(),
        algorithms=["ES256"],
        options={
            "verify_aud": False,
            "verify_exp": False,
            "verify_iat": False,
            "verify_iss": False,
        },
    )
    assert payload["iat"] == fixed_time
    assert payload["jti"] == "custom-jti"
    assert payload["nonce"] == "abc"


@pytest.mark.asyncio
async def test_verifier_accepts_valid_proof_with_embedded_jwk(
    monkeypatch, ec_keypair
) -> None:
    private_key, jwk, thumbprint = ec_keypair
    signer = DPoPSigner(private_key=private_key, public_jwk=jwk, algorithm="ES256")
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPSigner, "_now", lambda self: fixed_time)
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)
    ath_value = signer.ath_from_token(b"access-token")
    token = signer.sign_request(
        "GET",
        "https://example.com/resource",
        jti="proof-jti",
        ath_b64u=ath_value,
        extra_claims={"nonce": "server-nonce"},
    )

    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET",
        htu="https://example.com/resource",
        policy=VerifyPolicy(),
    )
    replay = DummyReplay()
    extras = {"nonce": "server-nonce", "access_token": b"access-token"}

    await verifier._verify_core(
        token,
        context,
        CnfBinding(BindType.JKT, thumbprint),
        replay=replay,
        keys=None,
        extras=extras,
    )

    assert replay.seen_calls == [("dpop:https://example.com/resource", "proof-jti")]
    assert replay.mark_calls == [
        ("dpop:https://example.com/resource", "proof-jti", context.policy.max_skew_s)
    ]


@pytest.mark.asyncio
async def test_verifier_detects_replay(monkeypatch, ec_keypair) -> None:
    private_key, jwk, thumbprint = ec_keypair
    signer = DPoPSigner(private_key=private_key, public_jwk=jwk, algorithm="ES256")
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPSigner, "_now", lambda self: fixed_time)
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)
    token = signer.sign_request("GET", "https://example.com", jti="dup")
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    with pytest.raises(PoPVerificationError, match="Replay detected"):
        await verifier._verify_core(
            token,
            context,
            CnfBinding(BindType.JKT, thumbprint),
            replay=AlwaysSeenReplay(),
            keys=None,
            extras={},
        )


@pytest.mark.asyncio
async def test_verifier_rejects_thumbprint_mismatch(monkeypatch, ec_keypair) -> None:
    private_key, jwk, _ = ec_keypair
    signer = DPoPSigner(private_key=private_key, public_jwk=jwk, algorithm="ES256")
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPSigner, "_now", lambda self: fixed_time)
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)
    token = signer.sign_request("GET", "https://example.com")
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    with pytest.raises(PoPBindingError, match="thumbprint"):
        await verifier._verify_core(
            token,
            context,
            CnfBinding(BindType.JKT, "incorrect"),
            replay=DummyReplay(),
            keys=None,
            extras={},
        )


@pytest.mark.asyncio
async def test_verifier_requires_key_resolver_when_header_omits_jwk(
    monkeypatch, ec_keypair
) -> None:
    private_key, jwk, thumbprint = ec_keypair
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)

    payload = {
        "htm": "GET",
        "htu": "https://example.com",
        "iat": fixed_time,
        "jti": "proof",
    }
    token = jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers={"typ": "dpop+jwt", "kid": "kid"},
    )
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    with pytest.raises(PoPVerificationError, match="Key resolver required"):
        await verifier._verify_core(
            token,
            context,
            CnfBinding(BindType.JKT, thumbprint),
            replay=DummyReplay(),
            keys=None,
            extras={},
        )


@pytest.mark.asyncio
async def test_verifier_uses_kid_to_resolve_key(monkeypatch, ec_keypair) -> None:
    private_key, jwk, thumbprint = ec_keypair
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)

    payload = {
        "htm": "GET",
        "htu": "https://example.com",
        "iat": fixed_time,
        "jti": "kid-proof",
    }
    token = jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers={"typ": "dpop+jwt", "kid": "kid-value"},
    )

    resolver = TrackingResolver(
        private_key.public_key(), thumbprint=thumbprint, kid=b"kid-value"
    )
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    await verifier._verify_core(
        token,
        context,
        CnfBinding(BindType.JKT, thumbprint),
        replay=DummyReplay(),
        keys=resolver,
        extras={},
    )

    assert resolver.kid_queries == [b"kid-value"]
    assert resolver.thumb_queries == []


@pytest.mark.asyncio
async def test_verifier_falls_back_to_thumbprint_resolution(
    monkeypatch, ec_keypair
) -> None:
    private_key, jwk, thumbprint = ec_keypair
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)

    payload = {
        "htm": "GET",
        "htu": "https://example.com",
        "iat": fixed_time,
        "jti": "thumb-proof",
    }
    token = jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers={"typ": "dpop+jwt"},
    )

    resolver = TrackingResolver(private_key.public_key(), thumbprint=thumbprint)
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    await verifier._verify_core(
        token,
        context,
        CnfBinding(BindType.JKT, thumbprint),
        replay=DummyReplay(),
        keys=resolver,
        extras={},
    )

    assert resolver.kid_queries == []
    assert resolver.thumb_queries == [CnfBinding(BindType.JKT, thumbprint)]


@pytest.mark.asyncio
async def test_verifier_rejects_when_key_unavailable(monkeypatch, ec_keypair) -> None:
    private_key, jwk, thumbprint = ec_keypair
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)

    payload = {
        "htm": "GET",
        "htu": "https://example.com",
        "iat": fixed_time,
        "jti": "missing-key",
    }
    token = jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers={"typ": "dpop+jwt"},
    )

    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    with pytest.raises(PoPVerificationError, match="No verification key"):
        await verifier._verify_core(
            token,
            context,
            CnfBinding(BindType.JKT, thumbprint),
            replay=DummyReplay(),
            keys=NullResolver(),
            extras={},
        )


@pytest.mark.asyncio
async def test_verifier_rejects_on_signature_failure(monkeypatch, ec_keypair) -> None:
    private_key, jwk, thumbprint = ec_keypair
    signer = DPoPSigner(private_key=private_key, public_jwk=jwk, algorithm="ES256")
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPSigner, "_now", lambda self: fixed_time)
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)
    token = signer.sign_request("GET", "https://example.com", jti="sig")
    tampered = token[:-2] + ("A" if token[-1] != "A" else "B")
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    with pytest.raises(PoPVerificationError, match="signature verification failed"):
        await verifier._verify_core(
            tampered,
            context,
            CnfBinding(BindType.JKT, thumbprint),
            replay=DummyReplay(),
            keys=None,
            extras={},
        )


@pytest.mark.asyncio
async def test_verifier_rejects_on_htm_htu_mismatch(monkeypatch, ec_keypair) -> None:
    private_key, jwk, thumbprint = ec_keypair
    signer = DPoPSigner(private_key=private_key, public_jwk=jwk, algorithm="ES256")
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPSigner, "_now", lambda self: fixed_time)
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)
    token = signer.sign_request("POST", "https://example.com", jti="htm")
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    with pytest.raises(PoPVerificationError, match="htm/htu mismatch"):
        await verifier._verify_core(
            token,
            context,
            CnfBinding(BindType.JKT, thumbprint),
            replay=DummyReplay(),
            keys=None,
            extras={},
        )


@pytest.mark.asyncio
async def test_verifier_rejects_on_invalid_iat(monkeypatch, ec_keypair) -> None:
    private_key, jwk, thumbprint = ec_keypair
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)

    payload = {
        "htm": "GET",
        "htu": "https://example.com",
        "iat": "invalid",
        "jti": "bad-iat",
    }
    token = jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers={"typ": "dpop+jwt", "jwk": jwk},
    )
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    with pytest.raises(PoPParseError, match="Invalid or missing iat"):
        await verifier._verify_core(
            token,
            context,
            CnfBinding(BindType.JKT, thumbprint),
            replay=DummyReplay(),
            keys=None,
            extras={},
        )


@pytest.mark.asyncio
async def test_verifier_rejects_when_jti_missing(monkeypatch, ec_keypair) -> None:
    private_key, jwk, thumbprint = ec_keypair
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)

    payload = {
        "htm": "GET",
        "htu": "https://example.com",
        "iat": fixed_time,
    }
    token = jwt.encode(
        payload,
        private_key,
        algorithm="ES256",
        headers={"typ": "dpop+jwt", "jwk": jwk},
    )
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    with pytest.raises(PoPParseError, match="Missing jti"):
        await verifier._verify_core(
            token,
            context,
            CnfBinding(BindType.JKT, thumbprint),
            replay=DummyReplay(),
            keys=None,
            extras={},
        )


@pytest.mark.asyncio
async def test_verifier_rejects_on_nonce_mismatch(monkeypatch, ec_keypair) -> None:
    private_key, jwk, thumbprint = ec_keypair
    signer = DPoPSigner(private_key=private_key, public_jwk=jwk, algorithm="ES256")
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPSigner, "_now", lambda self: fixed_time)
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)
    token = signer.sign_request(
        "GET",
        "https://example.com",
        jti="nonce",
        extra_claims={"nonce": "proof"},
    )
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    with pytest.raises(PoPVerificationError, match="Nonce mismatch"):
        await verifier._verify_core(
            token,
            context,
            CnfBinding(BindType.JKT, thumbprint),
            replay=DummyReplay(),
            keys=None,
            extras={"nonce": "expected"},
        )


@pytest.mark.asyncio
async def test_verifier_requires_ath_claim_when_policy_demands(
    monkeypatch, ec_keypair
) -> None:
    private_key, jwk, thumbprint = ec_keypair
    signer = DPoPSigner(private_key=private_key, public_jwk=jwk, algorithm="ES256")
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPSigner, "_now", lambda self: fixed_time)
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)
    token = signer.sign_request("GET", "https://example.com", jti="ath")
    verifier = DPoPVerifier()
    policy = VerifyPolicy(require_ath=True)
    context = RequestContext(method="GET", htu="https://example.com", policy=policy)

    with pytest.raises(
        PoPVerificationError, match="Access-token hash \(ath\) required"
    ):
        await verifier._verify_core(
            token,
            context,
            CnfBinding(BindType.JKT, thumbprint),
            replay=DummyReplay(),
            keys=None,
            extras={"access_token": b"access"},
        )


@pytest.mark.asyncio
async def test_verifier_rejects_when_optional_ath_mismatches(
    monkeypatch, ec_keypair
) -> None:
    private_key, jwk, thumbprint = ec_keypair
    signer = DPoPSigner(private_key=private_key, public_jwk=jwk, algorithm="ES256")
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPSigner, "_now", lambda self: fixed_time)
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)
    token = signer.sign_request(
        "GET",
        "https://example.com",
        jti="ath-mismatch",
        ath_b64u=signer.ath_from_token(b"different"),
    )
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    with pytest.raises(PoPVerificationError, match="ath claim does not match"):
        await verifier._verify_core(
            token,
            context,
            CnfBinding(BindType.JKT, thumbprint),
            replay=DummyReplay(),
            keys=None,
            extras={"access_token": b"expected"},
        )


@pytest.mark.asyncio
async def test_verifier_rejects_unparsable_header(ec_keypair) -> None:
    _, _, thumbprint = ec_keypair
    token = "not-a-jwt"
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    with pytest.raises(PoPParseError, match="could not be parsed"):
        await verifier._verify_core(
            token,
            context,
            CnfBinding(BindType.JKT, thumbprint),
            replay=DummyReplay(),
            keys=None,
            extras={},
        )


@pytest.mark.asyncio
async def test_verifier_rejects_when_alg_missing(monkeypatch, ec_keypair) -> None:
    _, jwk, thumbprint = ec_keypair
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)
    payload = {
        "htm": "GET",
        "htu": "https://example.com",
        "iat": fixed_time,
        "jti": "no-alg",
    }
    header = {"typ": "dpop+jwt", "jwk": jwk}
    token = _make_header(payload, header)
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    with pytest.raises(PoPParseError, match="missing alg"):
        await verifier._verify_core(
            token,
            context,
            CnfBinding(BindType.JKT, thumbprint),
            replay=DummyReplay(),
            keys=None,
            extras={},
        )


@pytest.mark.asyncio
async def test_verifier_rejects_when_algorithm_unsupported(
    monkeypatch, ec_keypair
) -> None:
    _, jwk, thumbprint = ec_keypair
    fixed_time = 1700000000
    monkeypatch.setattr(DPoPVerifier, "_now", lambda self: fixed_time)
    payload = {
        "htm": "GET",
        "htu": "https://example.com",
        "iat": fixed_time,
        "jti": "bad-alg",
    }
    header = {"typ": "dpop+jwt", "jwk": jwk, "alg": "FAKE"}
    token = _make_header(payload, header)
    verifier = DPoPVerifier()
    context = RequestContext(
        method="GET", htu="https://example.com", policy=VerifyPolicy()
    )

    with pytest.raises(PoPVerificationError, match="Unsupported algorithm"):
        await verifier._verify_core(
            token,
            context,
            CnfBinding(BindType.JKT, thumbprint),
            replay=DummyReplay(),
            keys=None,
            extras={},
        )
