import json

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from cryptography.hazmat.primitives import serialization

from swarmauri_signing_pep458 import Pep458Signer


@pytest.mark.asyncio
async def test_ed25519_sign_and_verify_round_trip():
    signer = Pep458Signer()
    private = ed25519.Ed25519PrivateKey.generate()
    keyref = {"kind": "cryptography_obj", "obj": private, "alg": "Ed25519"}
    payload = b"pep458-test-payload"

    signatures = await signer.sign_bytes(keyref, payload)

    assert await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [private.public_key()]},
    )


@pytest.mark.asyncio
async def test_rsa_pss_sign_and_verify_round_trip():
    signer = Pep458Signer()
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    keyref = {"kind": "cryptography_obj", "obj": private, "alg": "RSA-PSS-SHA256"}
    payload = b"pep458-test-payload"

    signatures = await signer.sign_bytes(keyref, payload)

    assert await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [private.public_key()]},
    )


@pytest.mark.asyncio
async def test_verify_respects_min_signers_requirement():
    signer = Pep458Signer()
    ed_private = ed25519.Ed25519PrivateKey.generate()
    rsa_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    payload = b"pep458-threshold"
    ed_sig = await signer.sign_bytes(
        {"kind": "cryptography_obj", "obj": ed_private}, payload
    )
    rsa_sig = await signer.sign_bytes(
        {"kind": "cryptography_obj", "obj": rsa_private, "alg": "RSA-PSS-SHA256"},
        payload,
    )

    assert await signer.verify_bytes(
        payload,
        [*ed_sig, *rsa_sig],
        require={"min_signers": 2},
        opts={"pubkeys": [ed_private.public_key(), rsa_private.public_key()]},
    )


@pytest.mark.asyncio
async def test_verify_fails_when_min_signers_not_met():
    signer = Pep458Signer()
    ed_private = ed25519.Ed25519PrivateKey.generate()
    rsa_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    payload = b"pep458-threshold"
    ed_sig = await signer.sign_bytes(
        {"kind": "cryptography_obj", "obj": ed_private}, payload
    )

    assert not await signer.verify_bytes(
        payload,
        ed_sig,
        require={"min_signers": 2},
        opts={"pubkeys": [ed_private.public_key(), rsa_private.public_key()]},
    )


@pytest.mark.asyncio
async def test_envelope_canonicalization_is_deterministic():
    signer = Pep458Signer()
    envelope = {
        "targets": {"pkg": {"hashes": {"sha256": "00"}}},
        "_meta": {"version": 1},
    }

    canonical = await signer.canonicalize_envelope(envelope)
    expected = json.dumps(
        envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    assert canonical == expected


@pytest.mark.asyncio
async def test_public_key_loading_from_pem_round_trip():
    signer = Pep458Signer()
    private = ed25519.Ed25519PrivateKey.generate()
    pem = private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_pem = private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    signatures = await signer.sign_bytes({"kind": "pem", "priv": pem}, b"payload")

    assert await signer.verify_bytes(
        b"payload",
        signatures,
        opts={"pubkeys": [pub_pem]},
    )
