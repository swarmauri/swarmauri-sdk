import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import AsyncIterator, Iterable

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    serialize_key_and_certificates,
)
from lxml import etree

from swarmauri_core.signing.types import Signature
from swarmauri_signing_xmld.xmld_signer import (
    XMLDSigner,
    _canon_xml,
    _ensure_deps,
    _fingerprint,
    _load_certificate,
    _load_pem,
    _load_private_key,
    _load_public_keys,
    _min_signers,
    _resolve_alg,
    _serialize_signature,
    _stream_to_bytes,
)


@pytest.fixture
def rsa_private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def rsa_certificate(rsa_private_key: rsa.RSAPrivateKey) -> x509.Certificate:
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "Swarmauri"),
            x509.NameAttribute(x509.NameOID.COMMON_NAME, "swarmauri.test"),
        ]
    )
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(rsa_private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=30))
    )
    return builder.sign(private_key=rsa_private_key, algorithm=hashes.SHA256())


@pytest.fixture
def ed25519_private_key() -> ed25519.Ed25519PrivateKey:
    return ed25519.Ed25519PrivateKey.generate()


def test_ensure_deps_raises_when_lxml_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    from swarmauri_signing_xmld import xmld_signer

    monkeypatch.setattr(xmld_signer, "_LXML_OK", False)
    monkeypatch.setattr(xmld_signer, "_CRYPTO_OK", True)

    with pytest.raises(RuntimeError, match="requires 'lxml'"):
        _ensure_deps()


def test_ensure_deps_raises_when_crypto_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from swarmauri_signing_xmld import xmld_signer

    monkeypatch.setattr(xmld_signer, "_LXML_OK", True)
    monkeypatch.setattr(xmld_signer, "_CRYPTO_OK", False)

    with pytest.raises(RuntimeError, match="requires 'cryptography'"):
        _ensure_deps()


@pytest.mark.asyncio
async def test_stream_to_bytes_returns_input_bytes() -> None:
    payload = b"xml"

    result = await _stream_to_bytes(payload)

    assert result == payload


@pytest.mark.asyncio
async def test_stream_to_bytes_reads_async_iterable() -> None:
    async def source() -> AsyncIterator[bytes]:
        yield b"xml"
        yield b"-"
        yield b"sig"

    result = await _stream_to_bytes(source())

    assert result == b"xml-sig"


@pytest.mark.asyncio
async def test_stream_to_bytes_reads_iterable() -> None:
    def source() -> Iterable[bytes]:
        return [b"a", b"b", b"c"]

    result = await _stream_to_bytes(source())

    assert result == b"abc"


@pytest.mark.asyncio
async def test_stream_to_bytes_rejects_unsupported_type() -> None:
    class Bad:
        pass

    with pytest.raises(TypeError, match="Unsupported stream"):
        await _stream_to_bytes(Bad())


def test_canon_xml_default_from_bytes() -> None:
    xml = b"<root><child/></root>"

    canonical = _canon_xml(xml)

    assert canonical == b"<root><child/></root>"


def test_canon_xml_c14n11_from_str() -> None:
    xml = "<root><child attr='1'/></root>"

    canonical = _canon_xml(xml, canon="c14n11")

    expected = etree.tostring(
        etree.fromstring(xml.encode("utf-8")),
        method="c14n",
        exclusive=False,
        with_comments=False,
        c14n_version=1.1,
    )
    assert canonical == expected


def test_canon_xml_exclusive_uses_inclusive_ns() -> None:
    xml = "<ns:root xmlns:ns='urn:test'><ns:child/></ns:root>"

    canonical = _canon_xml(xml, canon="exc-c14n", inclusive_ns=("ns",))

    assert b"xmlns:ns" in canonical


def test_canon_xml_rejects_unknown_profile() -> None:
    with pytest.raises(ValueError, match="Unsupported XML canon"):
        _canon_xml("<root/>", canon="invalid")


def test_load_pem_returns_bytes_when_bytes_provided() -> None:
    pem = b"data"

    assert _load_pem(pem) is pem


def test_load_pem_reads_file(tmp_path: Path) -> None:
    pem_path = tmp_path / "key.pem"
    pem_path.write_text("file-data")

    assert _load_pem(str(pem_path)) == b"file-data"


def test_load_pem_returns_string_bytes_when_not_a_path() -> None:
    text = "string-data"

    assert _load_pem(text) == text.encode()


def test_load_pem_rejects_unknown_type() -> None:
    with pytest.raises(
        TypeError, match="PEM entries must be bytes or filesystem paths"
    ):
        _load_pem(123)


def test_load_private_key_from_pem(
    ed25519_private_key: ed25519.Ed25519PrivateKey,
) -> None:
    pem = ed25519_private_key.private_bytes(
        encoding=Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )

    loaded = _load_private_key({"kind": "pem", "private_key": pem})

    assert isinstance(loaded, ed25519.Ed25519PrivateKey)


def test_load_private_key_from_pkcs12(
    rsa_private_key: rsa.RSAPrivateKey, rsa_certificate: x509.Certificate
) -> None:
    bundle = serialize_key_and_certificates(
        name=b"xmld",
        key=rsa_private_key,
        cert=rsa_certificate,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(b"secret"),
    )

    loaded = _load_private_key({"kind": "pkcs12", "data": bundle, "password": "secret"})

    assert isinstance(loaded, rsa.RSAPrivateKey)


def test_load_private_key_rejects_unknown_mapping() -> None:
    with pytest.raises(TypeError):
        _load_private_key({"kind": "unknown"})


def test_load_certificate_returns_certificate(
    rsa_private_key: rsa.RSAPrivateKey, rsa_certificate: x509.Certificate
) -> None:
    pem = rsa_certificate.public_bytes(Encoding.PEM)

    cert = _load_certificate({"certificate": pem})

    assert isinstance(cert, x509.Certificate)


def test_load_certificate_returns_none_when_missing() -> None:
    assert _load_certificate({}) is None


def test_fingerprint_produces_sha256() -> None:
    fingerprint = _fingerprint(b"abc")

    assert fingerprint == hashlib.sha256(b"abc").hexdigest()


def test_resolve_alg_for_rsa_defaults_to_pss(
    rsa_private_key: rsa.RSAPrivateKey,
) -> None:
    name, mode, hash_alg = _resolve_alg(rsa_private_key, None)

    assert name == "RSA-PSS-SHA256"
    assert hash_alg.name == "sha256"
    assert mode.salt_length == mode.MAX_LENGTH


def test_resolve_alg_for_rsa_honors_pkcs1(rsa_private_key: rsa.RSAPrivateKey) -> None:
    name, mode, _ = _resolve_alg(rsa_private_key, "rsa-pkcs1-sha256")

    assert name == "RSA-PKCS1-SHA256"


def test_resolve_alg_for_ecdsa() -> None:
    private = ec.generate_private_key(ec.SECP256R1())

    name, mode, hash_alg = _resolve_alg(private, None)

    assert name == "ECDSA-SHA256"
    assert isinstance(mode, ec.ECDSA)
    assert hash_alg.name == "sha256"


def test_resolve_alg_for_ed25519(
    ed25519_private_key: ed25519.Ed25519PrivateKey,
) -> None:
    name, mode, hash_alg = _resolve_alg(ed25519_private_key, None)

    assert name == "Ed25519"
    assert mode is None
    assert hash_alg is None


def test_resolve_alg_rejects_unknown_key() -> None:
    class Dummy:
        pass

    with pytest.raises(TypeError):
        _resolve_alg(Dummy(), None)


def test_load_public_keys_accepts_direct_instances(
    rsa_private_key: rsa.RSAPrivateKey,
) -> None:
    keys = _load_public_keys([rsa_private_key.public_key()])

    assert len(keys) == 1


def test_load_public_keys_parses_pem(
    ed25519_private_key: ed25519.Ed25519PrivateKey,
) -> None:
    pem = ed25519_private_key.public_key().public_bytes(
        encoding=Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    keys = _load_public_keys([pem])

    assert isinstance(keys[0], ed25519.Ed25519PublicKey)


def test_load_public_keys_handles_certificates(
    rsa_certificate: x509.Certificate,
) -> None:
    pem = rsa_certificate.public_bytes(Encoding.PEM)

    keys = _load_public_keys([pem])

    assert isinstance(keys[0], rsa.RSAPublicKey)


def test_serialize_signature_includes_cert_details(
    rsa_certificate: x509.Certificate,
) -> None:
    signature = _serialize_signature(
        b"sig",
        payload_kind="bytes",
        alg_name="RSA-PSS-SHA256",
        canon="c14n",
        cert=rsa_certificate,
    )

    assert signature.kid == _fingerprint(rsa_certificate.public_bytes(Encoding.DER))
    assert signature.cert_chain_der == (rsa_certificate.public_bytes(Encoding.DER),)


def test_serialize_signature_without_cert_has_no_kid() -> None:
    signature = _serialize_signature(
        b"sig",
        payload_kind="digest",
        alg_name="Ed25519",
        canon="raw",
        cert=None,
    )

    assert signature.kid is None
    assert signature.cert_chain_der is None


def test_min_signers_defaults_to_one() -> None:
    assert _min_signers(None) == 1


def test_min_signers_uses_configuration() -> None:
    assert _min_signers({"min_signers": 3}) == 3


def test_min_signers_clamps_invalid_values() -> None:
    assert _min_signers({"min_signers": "bad"}) == 1


@pytest.mark.asyncio
async def test_xml_signer_accepts_external_key_provider() -> None:
    signer = XMLDSigner()

    class Provider:
        pass

    provider = Provider()
    signer.set_key_provider(provider)  # Should not raise


def test_xml_signer_supports_returns_capabilities() -> None:
    signer = XMLDSigner()

    capabilities = signer.supports()

    assert "signs" in capabilities
    assert "verifies" in capabilities


def test_xml_signer_supports_includes_key_reference() -> None:
    signer = XMLDSigner()

    capabilities = signer.supports("key-ref")

    assert capabilities["key_refs"] == ("key-ref",)


@pytest.mark.asyncio
async def test_sign_bytes_records_metadata(
    ed25519_private_key: ed25519.Ed25519PrivateKey,
) -> None:
    pem = ed25519_private_key.private_bytes(
        encoding=Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    signer = XMLDSigner()

    signatures = await signer.sign_bytes(
        {"kind": "pem", "private_key": pem}, b"payload"
    )

    assert signatures[0].meta == {"payload_kind": "bytes", "canon": "raw"}


@pytest.mark.asyncio
async def test_sign_digest_records_metadata(
    ed25519_private_key: ed25519.Ed25519PrivateKey,
) -> None:
    pem = ed25519_private_key.private_bytes(
        encoding=Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    signer = XMLDSigner()

    signatures = await signer.sign_digest(
        {"kind": "pem", "private_key": pem}, b"digest"
    )

    assert signatures[0].meta == {"payload_kind": "digest", "canon": "raw"}


@pytest.mark.asyncio
async def test_sign_stream_round_trip(
    ed25519_private_key: ed25519.Ed25519PrivateKey,
) -> None:
    async def source() -> AsyncIterator[bytes]:
        yield b"pay"
        yield b"load"

    pem = ed25519_private_key.private_bytes(
        encoding=Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    signer = XMLDSigner()

    signatures = await signer.sign_stream({"kind": "pem", "private_key": pem}, source())

    assert signatures[0].meta == {"payload_kind": "bytes", "canon": "raw"}


@pytest.mark.asyncio
async def test_sign_envelope_respects_canon(
    ed25519_private_key: ed25519.Ed25519PrivateKey,
) -> None:
    pem = ed25519_private_key.private_bytes(
        encoding=Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    signer = XMLDSigner()

    signatures = await signer.sign_envelope(
        {"kind": "pem", "private_key": pem},
        "<root><child/></root>",
        canon="c14n",
    )

    assert signatures[0].meta == {"payload_kind": "envelope", "canon": "c14n"}


@pytest.mark.asyncio
async def test_canonicalize_envelope_raw_accepts_bytes() -> None:
    signer = XMLDSigner()

    canonical = await signer.canonicalize_envelope(b"payload", canon="raw")

    assert canonical == b"payload"


@pytest.mark.asyncio
async def test_canonicalize_envelope_raw_accepts_str() -> None:
    signer = XMLDSigner()

    canonical = await signer.canonicalize_envelope("payload", canon="raw")

    assert canonical == b"payload"


@pytest.mark.asyncio
async def test_canonicalize_envelope_raw_rejects_other() -> None:
    signer = XMLDSigner()

    with pytest.raises(TypeError, match="raw canon expects bytes or str"):
        await signer.canonicalize_envelope(123, canon="raw")


@pytest.mark.asyncio
async def test_canonicalize_envelope_c14n_returns_canonical_bytes() -> None:
    signer = XMLDSigner()

    canonical = await signer.canonicalize_envelope("<root><child/></root>")

    assert canonical == b"<root><child/></root>"


@pytest.mark.asyncio
async def test_verify_bytes_round_trip(
    ed25519_private_key: ed25519.Ed25519PrivateKey,
) -> None:
    pem = ed25519_private_key.private_bytes(
        encoding=Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    signer = XMLDSigner()
    payload = b"verify"

    signatures = await signer.sign_bytes({"kind": "pem", "private_key": pem}, payload)

    assert await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [ed25519_private_key.public_key()]},
    )


@pytest.mark.asyncio
async def test_verify_bytes_requires_pubkeys(
    ed25519_private_key: ed25519.Ed25519PrivateKey,
) -> None:
    pem = ed25519_private_key.private_bytes(
        encoding=Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    signer = XMLDSigner()
    payload = b"verify"
    signatures = await signer.sign_bytes({"kind": "pem", "private_key": pem}, payload)

    with pytest.raises(RuntimeError, match="requires opts\['pubkeys'\]"):
        await signer.verify_bytes(payload, signatures)


@pytest.mark.asyncio
async def test_verify_bytes_respects_min_signers(
    ed25519_private_key: ed25519.Ed25519PrivateKey,
    rsa_private_key: rsa.RSAPrivateKey,
) -> None:
    ed_pem = ed25519_private_key.private_bytes(
        encoding=Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    rsa_pem = rsa_private_key.private_bytes(
        encoding=Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    signer = XMLDSigner()
    payload = b"threshold"

    ed_sig = await signer.sign_bytes({"kind": "pem", "private_key": ed_pem}, payload)
    rsa_sig = await signer.sign_bytes({"kind": "pem", "private_key": rsa_pem}, payload)

    assert await signer.verify_bytes(
        payload,
        [*ed_sig, *rsa_sig],
        require={"min_signers": 2},
        opts={
            "pubkeys": [
                ed25519_private_key.public_key(),
                rsa_private_key.public_key(),
            ]
        },
    )

    assert not await signer.verify_bytes(
        payload,
        ed_sig,
        require={"min_signers": 2},
        opts={
            "pubkeys": [
                ed25519_private_key.public_key(),
                rsa_private_key.public_key(),
            ]
        },
    )


@pytest.mark.asyncio
async def test_verify_bytes_rejects_meta_mismatch(
    ed25519_private_key: ed25519.Ed25519PrivateKey,
) -> None:
    pem = ed25519_private_key.private_bytes(
        encoding=Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    signer = XMLDSigner()
    payload = b"verify"
    signatures = await signer.sign_bytes({"kind": "pem", "private_key": pem}, payload)
    bad = Signature(
        kid=signatures[0].kid,
        version=signatures[0].version,
        format=signatures[0].format,
        mode=signatures[0].mode,
        alg=signatures[0].alg,
        artifact=signatures[0].artifact,
        cert_chain_der=signatures[0].cert_chain_der,
        meta={"payload_kind": "digest", "canon": "raw"},
    )

    assert not await signer.verify_bytes(
        payload,
        [bad],
        opts={"pubkeys": [ed25519_private_key.public_key()]},
    )


@pytest.mark.asyncio
async def test_verify_envelope_requires_matching_canon(
    ed25519_private_key: ed25519.Ed25519PrivateKey,
) -> None:
    pem = ed25519_private_key.private_bytes(
        encoding=Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    signer = XMLDSigner()
    payload = "<root><child/></root>"
    signatures = await signer.sign_envelope(
        {"kind": "pem", "private_key": pem}, payload, canon="c14n"
    )
    mismatched = Signature(
        kid=signatures[0].kid,
        version=signatures[0].version,
        format=signatures[0].format,
        mode=signatures[0].mode,
        alg=signatures[0].alg,
        artifact=signatures[0].artifact,
        cert_chain_der=signatures[0].cert_chain_der,
        meta={"payload_kind": "envelope", "canon": "raw"},
    )

    assert not await signer.verify_envelope(
        payload,
        [mismatched],
        canon="c14n",
        opts={"pubkeys": [ed25519_private_key.public_key()]},
    )


@pytest.mark.asyncio
async def test_verify_payload_accepts_string_signature(
    ed25519_private_key: ed25519.Ed25519PrivateKey,
) -> None:
    pem = ed25519_private_key.private_bytes(
        encoding=Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    signer = XMLDSigner()
    payload = b"text"
    signatures = await signer.sign_bytes({"kind": "pem", "private_key": pem}, payload)
    text_signature = Signature(
        kid=signatures[0].kid,
        version=signatures[0].version,
        format=signatures[0].format,
        mode=signatures[0].mode,
        alg=signatures[0].alg,
        artifact=signatures[0].artifact.decode("latin1"),
        cert_chain_der=signatures[0].cert_chain_der,
        meta=signatures[0].meta,
    )

    assert await signer.verify_bytes(
        payload,
        [text_signature],
        opts={"pubkeys": [ed25519_private_key.public_key()]},
    )


@pytest.mark.asyncio
async def test_verify_bytes_returns_false_without_signatures() -> None:
    signer = XMLDSigner()

    assert not await signer.verify_bytes(b"payload", [])
