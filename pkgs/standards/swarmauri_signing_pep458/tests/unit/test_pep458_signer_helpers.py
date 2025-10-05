import base64

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

from swarmauri_signing_pep458 import Pep458Signer
from swarmauri_signing_pep458.Pep458Signer import (
    _alg_from_method,
    _method_from_alg,
)


@pytest.fixture()
def signer() -> Pep458Signer:
    return Pep458Signer()


@pytest.fixture()
def ed_key_pair():
    private = ed25519.Ed25519PrivateKey.generate()
    public = private.public_key()
    return private, public


@pytest.fixture()
def rsa_key_pair():
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = private.public_key()
    return private, public


def test_supports_reports_expected_values(signer: Pep458Signer):
    assert signer.supports() == {
        "algs": ("Ed25519", "RSA-PSS-SHA256"),
        "canons": ("tuf-json", "json"),
        "signs": ("bytes", "envelope"),
        "verifies": ("bytes", "envelope"),
        "envelopes": ("mapping",),
        "features": ("detached_only", "multi"),
    }


@pytest.mark.asyncio
async def test_canonicalize_envelope_rejects_unknown_canon(signer: Pep458Signer):
    with pytest.raises(ValueError):
        await signer.canonicalize_envelope({}, canon="yaml")


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Ed25519", "ed25519"),
        ("rsa_pss_sha256", "rsa-pss-sha256"),
        ("RSA-PSS-SHA256", "rsa-pss-sha256"),
    ],
)
def test_method_from_alg_normalizes_variants(value: str, expected: str):
    assert _method_from_alg(value) == expected


def test_method_from_alg_rejects_unknown_values():
    with pytest.raises(ValueError):
        _method_from_alg("dsa")


@pytest.mark.parametrize(
    "method,expected",
    [("ed25519", "Ed25519"), ("rsa-pss-sha256", "RSA-PSS-SHA256")],
)
def test_alg_from_method_round_trip(method: str, expected: str):
    assert _alg_from_method(method) == expected


def test_alg_from_method_rejects_unknown_method():
    with pytest.raises(ValueError):
        _alg_from_method("unknown")


def test_resolve_method_prefers_explicit_alg(signer: Pep458Signer, ed_key_pair):
    method = signer._resolve_method(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, "RSA-PSS-SHA256"
    )
    assert method == "rsa-pss-sha256"


def test_resolve_method_uses_alg_field(signer: Pep458Signer, ed_key_pair):
    method = signer._resolve_method(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0], "alg": "rsa_pss_sha256"},
        None,
    )
    assert method == "rsa-pss-sha256"


def test_resolve_method_infers_from_kty(signer: Pep458Signer):
    method = signer._resolve_method({"kty": "RSA"}, None)
    assert method == "rsa-pss-sha256"


def test_resolve_method_defaults_to_ed25519(signer: Pep458Signer):
    method = signer._resolve_method({}, None)
    assert method == "ed25519"


def test_load_private_key_accepts_cryptography_object(
    signer: Pep458Signer, ed_key_pair
):
    key = signer._load_private_key(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, "ed25519"
    )
    assert key is ed_key_pair[0]


def test_load_private_key_accepts_pem_string(signer: Pep458Signer, ed_key_pair):
    pem = (
        ed_key_pair[0]
        .private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        .decode("utf-8")
    )
    loaded = signer._load_private_key({"kind": "pem", "priv": pem}, "ed25519")
    assert isinstance(loaded, ed25519.Ed25519PrivateKey)


def test_load_private_key_from_raw_bytes(signer: Pep458Signer):
    seed = b"\x00" * 64
    loaded = signer._load_private_key(
        {"kind": "raw_ed25519_sk", "bytes": seed}, "ed25519"
    )
    assert isinstance(loaded, ed25519.Ed25519PrivateKey)


def test_load_private_key_requires_bytes_for_raw_seed(signer: Pep458Signer):
    with pytest.raises(TypeError):
        signer._load_private_key(
            {"kind": "raw_ed25519_sk", "bytes": "not-bytes"}, "ed25519"
        )


def test_load_private_key_rejects_unknown_kind(signer: Pep458Signer):
    with pytest.raises(ValueError):
        signer._load_private_key({"kind": "unknown"}, "ed25519")


def test_coerce_public_key_returns_objects_unchanged(signer: Pep458Signer, ed_key_pair):
    assert signer._coerce_public_key(ed_key_pair[1]) is ed_key_pair[1]


def test_coerce_public_key_accepts_pem_bytes(signer: Pep458Signer, ed_key_pair):
    pem = ed_key_pair[1].public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    loaded = signer._coerce_public_key(pem)
    assert (
        loaded.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        == pem
    )


def test_coerce_public_key_accepts_pem_string(signer: Pep458Signer, ed_key_pair):
    pem = (
        ed_key_pair[1]
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )
    loaded = signer._coerce_public_key(pem)
    assert isinstance(loaded, ed25519.Ed25519PublicKey)


def test_coerce_public_key_accepts_mapping_with_object(
    signer: Pep458Signer, ed_key_pair
):
    loaded = signer._coerce_public_key(
        {"kind": "cryptography_obj", "obj": ed_key_pair[1]}
    )
    assert loaded is ed_key_pair[1]


def test_coerce_public_key_accepts_mapping_with_pem(signer: Pep458Signer, ed_key_pair):
    pem = ed_key_pair[1].public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    loaded = signer._coerce_public_key({"kind": "pem", "pub": pem})
    assert isinstance(loaded, ed25519.Ed25519PublicKey)


def test_coerce_public_key_returns_none_for_unknown_input(signer: Pep458Signer):
    assert signer._coerce_public_key(42) is None


def test_methods_for_public_key_detects_ed25519(signer: Pep458Signer, ed_key_pair):
    assert signer._methods_for_public_key(ed_key_pair[1]) == ("ed25519",)


def test_methods_for_public_key_detects_rsa(signer: Pep458Signer, rsa_key_pair):
    assert signer._methods_for_public_key(rsa_key_pair[1]) == ("rsa-pss-sha256",)


def test_methods_for_public_key_falls_back_to_supported(signer: Pep458Signer):
    assert signer._methods_for_public_key(object()) == ("ed25519", "rsa-pss-sha256")


@pytest.mark.asyncio
async def test_verify_bytes_returns_false_without_pubkeys(
    signer: Pep458Signer, ed_key_pair
):
    payload = b"no-pubkeys"
    signatures = await signer.sign_bytes(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, payload
    )
    assert not await signer.verify_bytes(payload, signatures)


@pytest.mark.asyncio
async def test_verify_bytes_respects_allowed_methods(signer: Pep458Signer, ed_key_pair):
    payload = b"allowed-methods"
    signatures = await signer.sign_bytes(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, payload
    )
    assert not await signer.verify_bytes(
        payload,
        signatures,
        require={"algs": ["rsa-pss-sha256"], "pubkeys": [ed_key_pair[1]]},
    )


@pytest.mark.asyncio
async def test_verify_bytes_filters_by_kid(signer: Pep458Signer, ed_key_pair):
    payload = b"kid-filter"
    signatures = await signer.sign_bytes(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, payload
    )
    assert not await signer.verify_bytes(
        payload,
        signatures,
        require={"kids": ["non-matching"], "pubkeys": [ed_key_pair[1]]},
    )


@pytest.mark.asyncio
async def test_verify_bytes_returns_false_for_invalid_signature(
    signer: Pep458Signer, ed_key_pair
):
    payload = b"invalid-sig"
    signatures = await signer.sign_bytes(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, payload
    )
    corrupted = [
        {**signatures[0], "sig": base64.b64encode(b"tampered").decode("ascii")}
    ]
    assert not await signer.verify_bytes(
        payload,
        corrupted,
        opts={"pubkeys": [ed_key_pair[1]]},
    )


@pytest.mark.asyncio
async def test_verify_bytes_skips_unknown_signature_format(
    signer: Pep458Signer, ed_key_pair
):
    payload = b"unknown-format"
    signatures = await signer.sign_bytes(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, payload
    )
    malformed = [{**signatures[0], "format": "other"}]
    assert not await signer.verify_bytes(
        payload,
        malformed,
        opts={"pubkeys": [ed_key_pair[1]]},
    )


@pytest.mark.asyncio
async def test_verify_bytes_skips_unknown_methods(signer: Pep458Signer, ed_key_pair):
    payload = b"unknown-method"
    signatures = await signer.sign_bytes(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, payload
    )
    malformed = [{**signatures[0], "method": "unknown"}]
    assert not await signer.verify_bytes(
        payload,
        malformed,
        opts={"pubkeys": [ed_key_pair[1]]},
    )


@pytest.mark.asyncio
async def test_verify_bytes_handles_missing_key_ring_entries(
    signer: Pep458Signer, ed_key_pair
):
    payload = b"missing-key"
    signatures = await signer.sign_bytes(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, payload
    )
    unrelated_public = ed25519.Ed25519PrivateKey.generate().public_key()
    assert not await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [unrelated_public]},
    )


@pytest.mark.asyncio
async def test_verify_bytes_ignores_invalid_alg_requirements(
    signer: Pep458Signer, ed_key_pair
):
    payload = b"invalid-alg"
    signatures = await signer.sign_bytes(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, payload
    )
    assert await signer.verify_bytes(
        payload,
        signatures,
        require={"algs": ["invalid"], "pubkeys": [ed_key_pair[1]]},
    )


@pytest.mark.asyncio
async def test_sign_digest_delegates_to_sign_bytes(signer: Pep458Signer, ed_key_pair):
    payload = b"digest"
    expected = await signer.sign_bytes(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, payload
    )
    assert (
        await signer.sign_digest(
            {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, payload
        )
        == expected
    )


@pytest.mark.asyncio
async def test_verify_digest_delegates_to_verify_bytes(
    signer: Pep458Signer, ed_key_pair
):
    payload = b"verify-digest"
    signatures = await signer.sign_bytes(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, payload
    )
    assert await signer.verify_digest(
        payload,
        signatures,
        opts={"pubkeys": [ed_key_pair[1]]},
    )


@pytest.mark.asyncio
async def test_sign_envelope_delegates_to_sign_bytes(signer: Pep458Signer, ed_key_pair):
    envelope = {"meta": 1}
    expected_payload = await signer.canonicalize_envelope(envelope)
    signatures = await signer.sign_envelope(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, envelope
    )
    decoded = base64.b64decode(signatures[0]["sig"])
    ed_key_pair[1].verify(decoded, expected_payload)


@pytest.mark.asyncio
async def test_verify_envelope_delegates_to_verify_bytes(
    signer: Pep458Signer, ed_key_pair
):
    envelope = {"targets": []}
    signatures = await signer.sign_envelope(
        {"kind": "cryptography_obj", "obj": ed_key_pair[0]}, envelope
    )
    assert await signer.verify_envelope(
        envelope,
        signatures,
        opts={"pubkeys": [ed_key_pair[1]]},
    )
