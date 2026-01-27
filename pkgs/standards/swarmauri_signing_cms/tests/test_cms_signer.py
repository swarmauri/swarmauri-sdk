"""Unit tests for :mod:`swarmauri_signing_cms.cms_signer`."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Iterable

import pytest

from swarmauri_core.signing.types import Signature

from swarmauri_signing_cms.cms_signer import (
    CMSSigner,
    _canon_json,
    _ensure_crypto,
    _hash_from_alg,
    _is_pem_signature,
    _load_certificates,
    _load_pem,
    _load_pkcs7,
    _load_signing_material,
    _min_signers,
    _openssl_verify,
    _serialize_certs,
    _serialize_signature,
    _stream_to_bytes,
    _verify_pkcs7,
)


# ---------------------------------------------------------------------------
# Helpers


def _build_certificates() -> tuple[Any, Any, list[Any]]:
    """Create a private key, signing certificate and an extra certificate."""

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [x509.NameAttribute(x509.NameOID.COMMON_NAME, "Test Certificate")]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc) - timedelta(days=1))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=1))
        .sign(key, hashes.SHA256())
    )

    extra_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    extra_cert = (
        x509.CertificateBuilder()
        .subject_name(
            x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, "Extra Cert")])
        )
        .issuer_name(issuer)
        .public_key(extra_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc) - timedelta(days=1))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=1))
        .sign(key, hashes.SHA256())
    )

    return key, cert, [extra_cert]


class _AsyncStream:
    def __init__(self, data: Iterable[bytes]):
        self._iter = iter(data)

    def __aiter__(self) -> AsyncIterator[bytes]:
        return self

    async def __anext__(self) -> bytes:
        try:
            return next(self._iter)
        except StopIteration as exc:  # pragma: no cover - async protocol
            raise StopAsyncIteration from exc


# ---------------------------------------------------------------------------
# Tests for helper utilities


def test_ensure_crypto_requires_dependency(monkeypatch):
    monkeypatch.setattr("swarmauri_signing_cms.cms_signer._CRYPTO_OK", False)
    with pytest.raises(RuntimeError) as exc:
        _ensure_crypto()
    assert "cryptography" in str(exc.value)


def test_canon_json_produces_stable_representation():
    payload = {"b": 2, "a": 1}
    assert _canon_json(payload) == b'{"a":1,"b":2}'


@pytest.mark.asyncio
async def test_stream_to_bytes_handles_bytes_and_iterables():
    assert await _stream_to_bytes(b"abc") == b"abc"
    assert await _stream_to_bytes([b"a", b"b", b"c"]) == b"abc"


@pytest.mark.asyncio
async def test_stream_to_bytes_accepts_async_iterables():
    stream = _AsyncStream([b"ab", b"c"])
    assert await _stream_to_bytes(stream) == b"abc"


@pytest.mark.asyncio
async def test_stream_to_bytes_rejects_unknown_payload():
    with pytest.raises(TypeError):
        await _stream_to_bytes(123)  # type: ignore[arg-type]


def test_hash_from_alg_defaults_and_known_values():
    default = _hash_from_alg(None)
    assert default.name == "sha256"
    explicit = _hash_from_alg("sha-512")
    assert explicit.name == "sha512"


def test_hash_from_alg_rejects_unknown_algorithm():
    with pytest.raises(ValueError):
        _hash_from_alg("md5")


def test_load_pem_supports_bytes_and_paths(tmp_path: Path):
    data = b"content"
    assert _load_pem(data) == data

    file_path = tmp_path / "data.pem"
    file_path.write_bytes(data)
    assert _load_pem(str(file_path)) == data

    assert _load_pem("inline") == b"inline"


def test_load_pem_requires_known_type():
    with pytest.raises(TypeError):
        _load_pem(object())  # type: ignore[arg-type]


def test_load_signing_material_from_pem(tmp_path: Path):
    key, cert, extras = _build_certificates()

    from cryptography.hazmat.primitives import serialization

    key_path = tmp_path / "key.pem"
    cert_path = tmp_path / "cert.pem"
    extra_path = tmp_path / "extra.pem"

    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        )
    )
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    extra_path.write_bytes(extras[0].public_bytes(serialization.Encoding.PEM))

    private_key, loaded_cert, loaded_extras = _load_signing_material(
        {
            "kind": "pem",
            "private_key": str(key_path),
            "certificate": str(cert_path),
            "extra_certificates": [str(extra_path)],
        }
    )

    assert loaded_cert.fingerprint(_hash_from_alg("sha256")).hex()
    assert len(loaded_extras) == 1
    assert private_key.private_numbers() == key.private_numbers()


def test_load_signing_material_from_pkcs12():
    key, cert, extras = _build_certificates()

    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.serialization import pkcs12

    bundle = pkcs12.serialize_key_and_certificates(
        name=b"bundle",
        key=key,
        cert=cert,
        cas=extras,
        encryption_algorithm=serialization.BestAvailableEncryption(b"pass"),
    )

    private_key, loaded_cert, loaded_extras = _load_signing_material(
        {"kind": "pkcs12", "data": bundle, "password": "pass"}
    )

    assert loaded_cert.subject == cert.subject
    assert len(loaded_extras) == len(extras)
    assert private_key.private_numbers() == key.private_numbers()


def test_load_signing_material_requires_mapping():
    with pytest.raises(TypeError):
        _load_signing_material("not-a-mapping")  # type: ignore[arg-type]


def test_load_certificates_supports_iterables(tmp_path: Path):
    key, cert, extras = _build_certificates()

    from cryptography.hazmat.primitives import serialization

    extra = extras[0]
    cert_path = tmp_path / "cert.pem"
    extra_path = tmp_path / "extra.pem"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    extra_path.write_bytes(extra.public_bytes(serialization.Encoding.PEM))

    certs = _load_certificates([str(cert_path), extra_path.read_bytes()])
    assert [c.subject for c in certs]


def test_serialize_signature_captures_metadata():
    _, cert, extras = _build_certificates()

    from cryptography.hazmat.primitives import hashes, serialization

    signature = _serialize_signature(
        b"artifact",
        payload_kind="bytes",
        attached=True,
        cert=cert,
        extras=extras,
        hash_alg=hashes.SHA256(),
    )

    assert signature.meta["payload_kind"] == "bytes"
    assert signature.meta["attached"] is True
    assert signature.mode == "attached"
    assert signature.cert_chain_der[0] == cert.public_bytes(serialization.Encoding.DER)


def test_load_pkcs7_supports_der_and_pem():
    key, cert, extras = _build_certificates()

    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.serialization import pkcs7

    builder = pkcs7.PKCS7SignatureBuilder().set_data(b"payload")
    builder = builder.add_signer(cert, key, hashes.SHA256())
    builder = builder.add_certificate(extras[0])

    artifact_der = builder.sign(serialization.Encoding.DER, [])
    artifact_pem = builder.sign(serialization.Encoding.PEM, [])

    assert _load_pkcs7(artifact_der)
    assert _load_pkcs7(artifact_pem)


def test_is_pem_signature_detects_begin_marker():
    assert _is_pem_signature(b"-----BEGIN CERTIFICATE-----\n")
    assert not _is_pem_signature(b"binary")


def test_serialize_certs_concatenates_chain():
    _, cert, extras = _build_certificates()
    from cryptography.hazmat.primitives import serialization

    expected = cert.public_bytes(serialization.Encoding.PEM) + extras[0].public_bytes(
        serialization.Encoding.PEM
    )
    assert _serialize_certs([cert, extras[0]]) == expected


def test_openssl_verify_requires_trust():
    assert _openssl_verify(b"payload", b"sig", attached=False, trusted=[]) is False


def test_openssl_verify_invokes_openssl(monkeypatch):
    _, cert, _ = _build_certificates()

    called = {}

    def fake_which(cmd: str) -> str:
        assert cmd == "openssl"
        return "/usr/bin/openssl"

    class Proc:
        def __init__(self, stdout: bytes):
            self.returncode = 0
            self.stdout = stdout

    def fake_run(cmd: list[str], capture_output: bool) -> Proc:
        called["cmd"] = cmd
        if "-content" in cmd:
            return Proc(stdout=b"")
        return Proc(stdout=b"payload")

    monkeypatch.setattr("swarmauri_signing_cms.cms_signer.shutil.which", fake_which)
    monkeypatch.setattr("swarmauri_signing_cms.cms_signer.subprocess.run", fake_run)

    assert _openssl_verify(b"payload", b"-----BEGIN", attached=True, trusted=[cert])
    cmd = called["cmd"]
    assert "-inform" in cmd and "-CAfile" in cmd

    called.clear()
    assert _openssl_verify(b"payload", b"data", attached=False, trusted=[cert])
    assert "-content" in called["cmd"]


@pytest.mark.asyncio
async def test_verify_pkcs7_uses_loader(monkeypatch):
    invoked = {}

    class Dummy:
        def verify(self, *args, **kwargs):
            invoked["called"] = (args, kwargs)

    monkeypatch.setattr(
        "swarmauri_signing_cms.cms_signer._HAS_PKCS7_SIGNED_LOADER", True
    )
    from cryptography.hazmat.primitives.serialization import pkcs7 as pkcs7_module

    monkeypatch.setattr(
        "swarmauri_signing_cms.cms_signer.pkcs7.load_der_pkcs7_signed_data",
        lambda data: Dummy(),
    )

    result = await _verify_pkcs7(
        b"payload", b"artifact", attached=False, trusted=[object()]
    )
    assert result is True
    assert invoked["called"][1]["options"] == [
        pkcs7_module.PKCS7Options.DetachedSignature
    ]


@pytest.mark.asyncio
async def test_verify_pkcs7_falls_back_to_openssl(monkeypatch):
    monkeypatch.setattr(
        "swarmauri_signing_cms.cms_signer._HAS_PKCS7_SIGNED_LOADER", False
    )

    async def fake_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    monkeypatch.setattr("asyncio.to_thread", fake_to_thread)
    monkeypatch.setattr(
        "swarmauri_signing_cms.cms_signer._openssl_verify", lambda *a, **k: True
    )

    assert await _verify_pkcs7(
        b"payload", b"artifact", attached=True, trusted=[object()]
    )


def test_min_signers_interprets_requirements():
    assert _min_signers(None) == 1
    assert _min_signers({"min_signers": 3}) == 3
    assert _min_signers({"min_signers": "bad"}) == 1


# ---------------------------------------------------------------------------
# Tests for CMSSigner public interface


def test_signer_supports_reports_capabilities():
    signer = CMSSigner()
    support = signer.supports()
    assert "signs" in support
    assert signer.supports("ref")["key_refs"] == ("ref",)


def test_signer_key_provider_mutation():
    signer = CMSSigner()
    provider = object()
    signer.set_key_provider(provider)
    assert signer._key_provider is provider


@pytest.mark.asyncio
async def test_sign_methods_delegate_to_sign_payload(monkeypatch):
    signer = CMSSigner()
    called = {}

    async def fake_sign(key, payload, *, alg, opts, payload_kind):
        called.setdefault(payload_kind, (key, payload))
        return [Signature("kid", None, "cms", "attached", "SHA256", b"art")]  # type: ignore[arg-type]

    async def fake_canon(env, *, canon, opts):
        assert canon is None
        assert opts == {"opt": 1}
        return b"canon"

    monkeypatch.setattr(CMSSigner, "_sign_payload", fake_sign)
    monkeypatch.setattr(CMSSigner, "canonicalize_envelope", fake_canon)

    async def fake_stream_to_bytes(payload):
        return b"stream"

    monkeypatch.setattr(
        "swarmauri_signing_cms.cms_signer._stream_to_bytes", fake_stream_to_bytes
    )

    await signer.sign_bytes("key", b"data")
    await signer.sign_digest("key", b"digest")
    await signer.sign_stream("key", [b"s"])
    await signer.sign_envelope("key", {"a": 1}, opts={"opt": 1})

    assert called["bytes"][1] == b"data"
    assert called["digest"][1] == b"digest"
    assert called["stream"][1] == b"stream"
    assert called["envelope"][1] == b"canon"


@pytest.mark.asyncio
async def test_verify_methods_delegate_to_verify_payload(monkeypatch):
    signer = CMSSigner()
    called = {}

    async def fake_verify(payload, signatures, *, require, opts, payload_kind):
        called[payload_kind] = (payload, signatures, require)
        return True

    async def fake_canon(env, *, canon, opts):
        assert canon == "json"
        assert opts == {"opt": 1}
        return b"canon"

    monkeypatch.setattr(CMSSigner, "_verify_payload", fake_verify)
    monkeypatch.setattr(CMSSigner, "canonicalize_envelope", fake_canon)

    async def fake_stream_to_bytes(payload):
        return b"stream"

    monkeypatch.setattr(
        "swarmauri_signing_cms.cms_signer._stream_to_bytes", fake_stream_to_bytes
    )

    sigs = [Signature("kid", None, "cms", "attached", "SHA256", b"art")]  # type: ignore[arg-type]
    await signer.verify_bytes(b"data", sigs)
    await signer.verify_digest(b"digest", sigs, require={})
    await signer.verify_stream([b"s"], sigs)
    await signer.verify_envelope({"a": 1}, sigs, canon="json", opts={"opt": 1})

    assert called["bytes"][0] == b"data"
    assert called["digest"][0] == b"digest"
    assert called["stream"][0] == b"stream"
    assert called["envelope"][0] == b"canon"


@pytest.mark.asyncio
async def test_canonicalize_envelope_supports_json_and_raw():
    signer = CMSSigner()
    assert await signer.canonicalize_envelope({"b": 2, "a": 1}) == b'{"a":1,"b":2}'

    raw = await signer.canonicalize_envelope(b"raw", canon="raw")
    assert raw == b"raw"

    with pytest.raises(TypeError):
        await signer.canonicalize_envelope("string", canon="raw")

    with pytest.raises(ValueError):
        await signer.canonicalize_envelope({}, canon="unknown")


@pytest.mark.asyncio
async def test_sign_payload_builds_signature(tmp_path: Path):
    signer = CMSSigner()
    key, cert, extras = _build_certificates()

    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.serialization import pkcs12

    bundle = pkcs12.serialize_key_and_certificates(
        name=b"bundle",
        key=key,
        cert=cert,
        cas=extras,
        encryption_algorithm=serialization.NoEncryption(),
    )

    signatures = await signer._sign_payload(
        {"kind": "pkcs12", "data": bundle},
        b"payload",
        alg=None,
        opts={"attached": True, "encoding": "pem"},
        payload_kind="bytes",
    )

    assert len(signatures) == 1
    assert signatures[0].meta["attached"] is True

    with pytest.raises(ValueError):
        await signer._sign_payload(
            {"kind": "pkcs12", "data": bundle},
            b"payload",
            alg=None,
            opts={"encoding": "bogus"},
            payload_kind="bytes",
        )


@pytest.mark.asyncio
async def test_verify_payload_validates_signatures(monkeypatch):
    signer = CMSSigner()
    artifact = b"sig"

    async def fake_verify(payload, artifact_bytes, *, attached, trusted):
        assert payload == b"payload"
        assert attached is True
        return artifact_bytes == artifact

    monkeypatch.setattr("swarmauri_signing_cms.cms_signer._verify_pkcs7", fake_verify)

    signatures = [
        Signature(
            kid="kid",
            version=None,
            format="cms",
            mode="attached",
            alg="SHA256",
            artifact=artifact,
            meta={"payload_kind": "bytes", "attached": True},
        )
    ]

    assert await signer._verify_payload(
        b"payload",
        signatures,
        require={"min_signers": 1},
        opts={"trusted_certs": []},
        payload_kind="bytes",
    )

    assert not await signer._verify_payload(
        b"payload",
        [],
        require=None,
        opts=None,
        payload_kind="bytes",
    )

    bad_meta = [
        Signature(
            kid="kid",
            version=None,
            format="cms",
            mode="attached",
            alg="SHA256",
            artifact=b"ignored",
            meta={"payload_kind": "digest"},
        )
    ]
    assert not await signer._verify_payload(
        b"payload",
        bad_meta,
        require=None,
        opts=None,
        payload_kind="bytes",
    )


@pytest.mark.asyncio
async def test_verify_payload_handles_str_artifacts_and_errors(monkeypatch):
    signer = CMSSigner()

    async def fake_verify(payload, artifact_bytes, *, attached, trusted):
        if artifact_bytes == b"bad":
            raise RuntimeError("boom")
        return True

    monkeypatch.setattr("swarmauri_signing_cms.cms_signer._verify_pkcs7", fake_verify)

    signatures = [
        Signature(
            kid="kid",
            version=None,
            format="cms",
            mode="attached",
            alg="SHA256",
            artifact="text",
            meta={"payload_kind": "bytes", "attached": False},
        ),
        Signature(
            kid="kid2",
            version=None,
            format="cms",
            mode="attached",
            alg="SHA256",
            artifact=b"bad",
            meta={"payload_kind": "bytes", "attached": False},
        ),
    ]

    assert await signer._verify_payload(
        b"payload",
        signatures,
        require={"min_signers": 1},
        opts=None,
        payload_kind="bytes",
    )
