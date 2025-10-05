"""Unit tests for :mod:`swarmauri_signing_openpgp.openpgp_signer`."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator

import pytest

from swarmauri_signing_openpgp.openpgp_signer import (
    OpenPGPSigner,
    _canon_json,
    _ensure_pgpy,
    _hash_from_alg,
    _load_private_key,
    _load_public_keys,
    _load_signature,
    _min_signers,
    _serialize_signature,
    _stream_to_bytes,
)
from swarmauri_core.signing.types import Signature


@pytest.fixture(scope="module")
def pgp_material():
    """Provide a reusable OpenPGP key pair for the test module."""

    from pgpy import PGPKey, PGPUID
    from pgpy.constants import (
        CompressionAlgorithm,
        HashAlgorithm,
        KeyFlags,
        PubKeyAlgorithm,
        SymmetricKeyAlgorithm,
    )

    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 1024)
    uid = PGPUID.new("Test User", email="test@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.Sign},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )
    return key


def test_ensure_pgpy_raises_when_unavailable(monkeypatch):
    monkeypatch.setattr(
        "swarmauri_signing_openpgp.openpgp_signer._PGPY_AVAILABLE", False
    )
    with pytest.raises(RuntimeError):
        _ensure_pgpy()


@pytest.mark.asyncio
async def test_stream_to_bytes_from_bytes():
    payload = b"payload"
    assert await _stream_to_bytes(payload) == payload


@pytest.mark.asyncio
async def test_stream_to_bytes_from_async_iterable():
    async def producer() -> AsyncGenerator[bytes, None]:
        yield b"pa"
        yield b"yload"

    assert await _stream_to_bytes(producer()) == b"payload"


@pytest.mark.asyncio
async def test_stream_to_bytes_from_iterable():
    assert await _stream_to_bytes([b"pay", memoryview(b"load")]) == b"payload"


@pytest.mark.asyncio
async def test_stream_to_bytes_rejects_unsupported():
    class UnknownStream:  # pragma: no cover - defensive class definition
        pass

    with pytest.raises(TypeError):
        await _stream_to_bytes(UnknownStream())


def test_canon_json_returns_sorted_bytes():
    payload = {"b": 1, "a": 2}
    encoded = _canon_json(payload)
    assert json.loads(encoded) == {"a": 2, "b": 1}


def test_load_private_key_accepts_existing_instance(pgp_material):
    loaded = _load_private_key(pgp_material)
    assert loaded is pgp_material


def test_load_private_key_from_mapping_bytes(pgp_material):
    blob = bytes(str(pgp_material), "utf-8")
    loaded = _load_private_key({"kind": "pgpy-key", "data": blob})
    assert loaded.fingerprint == pgp_material.fingerprint


def test_load_private_key_from_file(tmp_path, pgp_material):
    path = tmp_path / "key.asc"
    path.write_text(str(pgp_material), encoding="utf-8")
    loaded = _load_private_key({"kind": "pgpy-file", "path": path})
    assert loaded.fingerprint == pgp_material.fingerprint


def test_load_private_key_unlocks_with_passphrase(pgp_material):
    from pgpy.constants import HashAlgorithm, SymmetricKeyAlgorithm

    protected_key = pgp_material.__class__.from_blob(str(pgp_material))[0]
    protected_key.protect(
        "secret",
        SymmetricKeyAlgorithm.AES256,
        HashAlgorithm.SHA256,
    )
    loaded = _load_private_key(
        {"kind": "pgpy-key", "data": str(protected_key), "passphrase": "secret"}
    )
    assert loaded.fingerprint == protected_key.fingerprint


def test_load_private_key_requires_passphrase(pgp_material):
    from pgpy.constants import HashAlgorithm, SymmetricKeyAlgorithm

    protected_key = pgp_material.__class__.from_blob(str(pgp_material))[0]
    protected_key.protect(
        "topsecret",
        SymmetricKeyAlgorithm.AES256,
        HashAlgorithm.SHA256,
    )
    with pytest.raises(RuntimeError):
        _load_private_key({"kind": "pgpy-key", "data": str(protected_key)})


def test_load_private_key_rejects_invalid_kind():
    with pytest.raises(TypeError):
        _load_private_key({"kind": "unknown"})


def test_load_private_key_requires_mapping_or_key():
    with pytest.raises(TypeError):
        _load_private_key(42)  # type: ignore[arg-type]


def test_load_public_keys_accepts_existing_key(pgp_material):
    keys = _load_public_keys([pgp_material.pubkey])
    assert keys[0].fingerprint == pgp_material.fingerprint


def test_load_public_keys_from_mapping_data(pgp_material):
    entries = [{"kind": "pgpy-key", "data": str(pgp_material.pubkey)}]
    keys = _load_public_keys(entries)
    assert keys[0].fingerprint == pgp_material.fingerprint


def test_load_public_keys_from_file(tmp_path, pgp_material):
    path = tmp_path / "pub.asc"
    path.write_text(str(pgp_material.pubkey), encoding="utf-8")
    keys = _load_public_keys([{"kind": "pgpy-file", "path": path}])
    assert keys[0].fingerprint == pgp_material.fingerprint


def test_load_public_keys_from_string(pgp_material):
    keys = _load_public_keys([str(pgp_material.pubkey)])
    assert keys[0].fingerprint == pgp_material.fingerprint


def test_load_public_keys_rejects_unknown_entry():
    with pytest.raises(TypeError):
        _load_public_keys([object()])


def test_hash_from_alg_defaults_to_sha256():
    from pgpy.constants import HashAlgorithm

    assert _hash_from_alg(None) is HashAlgorithm.SHA256


def test_hash_from_alg_accepts_friendly_name():
    from pgpy.constants import HashAlgorithm

    assert _hash_from_alg("sha-512") is HashAlgorithm.SHA512


def test_hash_from_alg_rejects_unknown_alg():
    with pytest.raises(ValueError):
        _hash_from_alg("unsupported")


def test_serialize_signature_captures_metadata(pgp_material):
    message = b"payload"
    signature = pgp_material.sign(message)
    result = _serialize_signature(
        signature,
        payload_kind="bytes",
        keyid=pgp_material.fingerprint.keyid,
        hash_alg=_hash_from_alg(None),
    )
    assert result.meta == {"payload_kind": "bytes", "signature_type": "BinaryDocument"}
    assert result.kid == pgp_material.fingerprint.keyid


def test_load_signature_from_signature_instance(pgp_material):
    signature = pgp_material.sign(b"payload")
    loaded = _load_signature(
        _serialize_signature(
            signature,
            payload_kind="bytes",
            keyid=None,
            hash_alg=_hash_from_alg(None),
        )
    )
    assert str(loaded) == str(signature)


def test_load_signature_from_mapping(pgp_material):
    signature = pgp_material.sign(b"payload")
    loaded = _load_signature({"artifact": str(signature)})
    assert str(loaded) == str(signature)


def test_load_signature_rejects_invalid_payload():
    with pytest.raises(TypeError):
        _load_signature({"artifact": object()})


def test_min_signers_default():
    assert _min_signers(None) == 1


def test_min_signers_reads_integer():
    assert _min_signers({"min_signers": 2}) == 2


def test_min_signers_handles_invalid_values():
    assert _min_signers({"min_signers": "bad"}) == 1


def test_signer_supports_reports_capabilities():
    signer = OpenPGPSigner()
    caps = signer.supports()
    assert "signs" in caps and "bytes" in caps["signs"]


def test_signer_supports_includes_key_reference():
    signer = OpenPGPSigner()
    caps = signer.supports("key-ref")
    assert caps["key_refs"] == ("key-ref",)


def test_signer_set_key_provider():
    signer = OpenPGPSigner()
    provider = object()
    signer.set_key_provider(provider)  # type: ignore[arg-type]
    assert signer._key_provider is provider


@pytest.mark.asyncio
async def test_sign_bytes_delegates_to_internal_helper(monkeypatch):
    signer = OpenPGPSigner()

    async def fake_sign(self, key, payload, *, alg, opts, payload_kind):
        return [payload_kind, payload]

    monkeypatch.setattr(OpenPGPSigner, "_sign_payload", fake_sign)
    result = await signer.sign_bytes("key", b"data")
    assert result == ["bytes", b"data"]


@pytest.mark.asyncio
async def test_sign_digest_delegates_to_internal_helper(monkeypatch):
    signer = OpenPGPSigner()

    async def fake_sign(self, key, payload, *, alg, opts, payload_kind):
        return [payload_kind, payload]

    monkeypatch.setattr(OpenPGPSigner, "_sign_payload", fake_sign)
    result = await signer.sign_digest("key", b"hash")
    assert result == ["digest", b"hash"]


@pytest.mark.asyncio
async def test_sign_stream_canonicalizes_payload(monkeypatch):
    signer = OpenPGPSigner()

    async def fake_sign(self, key, payload, *, alg, opts, payload_kind):
        return [payload_kind, payload]

    monkeypatch.setattr(OpenPGPSigner, "_sign_payload", fake_sign)

    async def stream() -> AsyncGenerator[bytes, None]:
        yield b"da"
        yield b"ta"

    result = await signer.sign_stream("key", stream())
    assert result == ["stream", b"data"]


@pytest.mark.asyncio
async def test_sign_envelope_canonicalizes(monkeypatch):
    signer = OpenPGPSigner()

    async def fake_canon(self, env, *, canon, opts):
        return b"canonical"

    async def fake_sign(self, key, payload, *, alg, opts, payload_kind):
        return [payload_kind, payload]

    monkeypatch.setattr(OpenPGPSigner, "canonicalize_envelope", fake_canon)
    monkeypatch.setattr(OpenPGPSigner, "_sign_payload", fake_sign)

    result = await signer.sign_envelope("key", {"k": "v"})
    assert result == ["envelope", b"canonical"]


@pytest.mark.asyncio
async def test_verify_bytes_delegates_to_internal_helper(monkeypatch):
    signer = OpenPGPSigner()

    async def fake_verify(self, payload, signatures, *, require, opts, payload_kind):
        return payload_kind == "bytes"

    monkeypatch.setattr(OpenPGPSigner, "_verify_payload", fake_verify)
    assert await signer.verify_bytes(b"data", []) is True


@pytest.mark.asyncio
async def test_verify_digest_delegates_to_internal_helper(monkeypatch):
    signer = OpenPGPSigner()

    async def fake_verify(self, payload, signatures, *, require, opts, payload_kind):
        return payload_kind == "digest"

    monkeypatch.setattr(OpenPGPSigner, "_verify_payload", fake_verify)
    assert await signer.verify_digest(b"data", []) is True


@pytest.mark.asyncio
async def test_verify_stream_canonicalizes_payload(monkeypatch):
    signer = OpenPGPSigner()

    async def fake_verify(self, payload, signatures, *, require, opts, payload_kind):
        return payload_kind == "stream" and payload == b"data"

    monkeypatch.setattr(OpenPGPSigner, "_verify_payload", fake_verify)

    async def stream() -> AsyncGenerator[bytes, None]:
        yield b"da"
        yield b"ta"

    assert await signer.verify_stream(stream(), []) is True


@pytest.mark.asyncio
async def test_verify_envelope_canonicalizes(monkeypatch):
    signer = OpenPGPSigner()

    async def fake_canon(self, env, *, canon, opts):
        return b"canonical"

    async def fake_verify(self, payload, signatures, *, require, opts, payload_kind):
        return payload_kind == "envelope" and payload == b"canonical"

    monkeypatch.setattr(OpenPGPSigner, "canonicalize_envelope", fake_canon)
    monkeypatch.setattr(OpenPGPSigner, "_verify_payload", fake_verify)

    assert await signer.verify_envelope({"k": "v"}, []) is True


@pytest.mark.asyncio
async def test_canonicalize_envelope_json_default():
    signer = OpenPGPSigner()
    env = {"b": 1, "a": 2}
    canonical = await signer.canonicalize_envelope(env)
    assert json.loads(canonical) == {"a": 2, "b": 1}


@pytest.mark.asyncio
async def test_canonicalize_envelope_raw_bytes():
    signer = OpenPGPSigner()
    env = b"raw"
    canonical = await signer.canonicalize_envelope(env, canon="raw")
    assert canonical == b"raw"


@pytest.mark.asyncio
async def test_canonicalize_envelope_raw_requires_bytes():
    signer = OpenPGPSigner()
    with pytest.raises(TypeError):
        await signer.canonicalize_envelope("raw", canon="raw")


@pytest.mark.asyncio
async def test_canonicalize_envelope_rejects_unknown():
    signer = OpenPGPSigner()
    with pytest.raises(ValueError):
        await signer.canonicalize_envelope({}, canon="xml")


@pytest.mark.asyncio
async def test_sign_payload_produces_signature(pgp_material):
    signer = OpenPGPSigner()
    signatures = await signer._sign_payload(
        pgp_material,
        b"payload",
        alg=None,
        opts=None,
        payload_kind="bytes",
    )
    assert isinstance(signatures[0], Signature)


@pytest.mark.asyncio
async def test_sign_payload_honors_hash_override(pgp_material):
    signer = OpenPGPSigner()
    signatures = await signer._sign_payload(
        pgp_material,
        b"payload",
        alg="sha-512",
        opts=None,
        payload_kind="bytes",
    )
    assert signatures[0].alg == "SHA512"


@pytest.mark.asyncio
async def test_verify_payload_returns_false_without_signatures():
    signer = OpenPGPSigner()
    assert (
        await signer._verify_payload(
            b"payload",
            [],
            require=None,
            opts={"pubkeys": []},
            payload_kind="bytes",
        )
        is False
    )


@pytest.mark.asyncio
async def test_verify_payload_requires_pubkeys():
    signer = OpenPGPSigner()
    with pytest.raises(RuntimeError):
        await signer._verify_payload(
            b"payload",
            [Signature(None, None, "fmt", "detached", "alg", b"sig")],
            require=None,
            opts={},
            payload_kind="bytes",
        )


@pytest.mark.asyncio
async def test_verify_payload_accepts_valid_signature(pgp_material):
    signer = OpenPGPSigner()
    signatures = await signer._sign_payload(
        pgp_material,
        b"payload",
        alg=None,
        opts=None,
        payload_kind="bytes",
    )
    assert (
        await signer._verify_payload(
            b"payload",
            signatures,
            require=None,
            opts={"pubkeys": [pgp_material.pubkey]},
            payload_kind="bytes",
        )
        is True
    )


@pytest.mark.asyncio
async def test_verify_payload_respects_min_signers(pgp_material):
    signer = OpenPGPSigner()
    signatures = await signer._sign_payload(
        pgp_material,
        b"payload",
        alg=None,
        opts=None,
        payload_kind="bytes",
    )
    assert (
        await signer._verify_payload(
            b"payload",
            signatures,
            require={"min_signers": 2},
            opts={"pubkeys": [pgp_material.pubkey]},
            payload_kind="bytes",
        )
        is False
    )


@pytest.mark.asyncio
async def test_verify_payload_skips_mismatched_payload_kind(pgp_material):
    signer = OpenPGPSigner()
    signatures = await signer._sign_payload(
        pgp_material,
        b"payload",
        alg=None,
        opts=None,
        payload_kind="digest",
    )
    assert (
        await signer._verify_payload(
            b"payload",
            signatures,
            require=None,
            opts={"pubkeys": [pgp_material.pubkey]},
            payload_kind="bytes",
        )
        is False
    )


@pytest.mark.asyncio
async def test_verify_payload_rejects_signature_for_different_payload(pgp_material):
    signer = OpenPGPSigner()
    signatures = await signer._sign_payload(
        pgp_material,
        b"payload",
        alg=None,
        opts=None,
        payload_kind="bytes",
    )
    assert (
        await signer._verify_payload(
            b"other",
            signatures,
            require=None,
            opts={"pubkeys": [pgp_material.pubkey]},
            payload_kind="bytes",
        )
        is False
    )
