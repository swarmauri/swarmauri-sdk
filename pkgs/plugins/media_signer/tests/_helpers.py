"""Shared helpers for MediaSigner optional signer integration tests."""

from __future__ import annotations

import asyncio
import datetime as _dt
import hashlib
from typing import AsyncIterator, Callable, Tuple

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption
from cryptography.x509.oid import NameOID

from MediaSigner import MediaSigner
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyUse
from swarmauri_core.keys.types import KeyAlg, KeyClass, KeySpec
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider

try:  # optional dependency used by OpenPGP helpers
    import pgpy
    from pgpy.constants import (
        CompressionAlgorithm,
        HashAlgorithm,
        KeyFlags,
        PubKeyAlgorithm,
        SymmetricKeyAlgorithm,
    )

    _PGPY_AVAILABLE = True
except Exception:  # pragma: no cover - runtime guard
    _PGPY_AVAILABLE = False


def _require_material(value: bytes | str | None) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    raise ValueError("KeyRef did not expose the required material bytes")


def generate_self_signed_rsa(common_name: str) -> Tuple[bytes, bytes]:
    """Produce a private key and certificate pair for RSA-based signers."""

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    now = _dt.datetime.utcnow()
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - _dt.timedelta(days=1))
        .not_valid_after(now + _dt.timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(private_key, hashes.SHA256())
    )
    private_pem = private_key.private_bytes(
        Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        NoEncryption(),
    )
    cert_pem = certificate.public_bytes(Encoding.PEM)
    return private_pem, cert_pem


async def build_media_signer_with_rsa(
    label: str,
) -> tuple[MediaSigner, InMemoryKeyProvider, KeyRef]:
    """Instantiate a ``MediaSigner`` backed by an RSA key pair."""

    provider = InMemoryKeyProvider()
    private_pem, cert_pem = generate_self_signed_rsa(label)
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.RSA_PSS_SHA256,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label=label,
    )
    key_ref = await provider.import_key(spec, private_pem, public=cert_pem)
    signer = MediaSigner(key_provider=provider)
    return signer, provider, key_ref


async def build_media_signer_with_hmac(
    label: str,
) -> tuple[MediaSigner, InMemoryKeyProvider, KeyRef]:
    """Instantiate a ``MediaSigner`` with a symmetric HMAC key."""

    provider = InMemoryKeyProvider()
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.HMAC_SHA256,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label=label,
    )
    key_ref = await provider.create_key(spec)
    signer = MediaSigner(key_provider=provider)
    return signer, provider, key_ref


def cms_key_entry(key_ref: KeyRef) -> dict[str, object]:
    """Translate an RSA ``KeyRef`` into CMS signer key parameters."""

    return {
        "kind": "pem",
        "private_key": _require_material(key_ref.material),
        "certificate": _require_material(key_ref.public),
    }


def cms_trust_opts(key_ref: KeyRef) -> dict[str, object]:
    return {"trusted_certs": [_require_material(key_ref.public)]}


def pdf_sign_opts(attached: bool) -> dict[str, object]:
    return {"attached": attached, "pdf": {}}


def pdf_trust_opts(key_ref: KeyRef) -> dict[str, object]:
    return cms_trust_opts(key_ref)


def xml_key_entry(key_ref: KeyRef) -> dict[str, object]:
    return {
        "kind": "pem",
        "private_key": _require_material(key_ref.material),
        "certificate": _require_material(key_ref.public),
    }


def xml_verify_opts(key_ref: KeyRef) -> dict[str, object]:
    return {"pubkeys": [_require_material(key_ref.public)]}


def jws_hmac_key(key_ref: KeyRef) -> dict[str, object]:
    secret = _require_material(key_ref.material)
    return {"kind": "raw", "key": secret, "kid": key_ref.kid}


def jws_verify_opts(key_ref: KeyRef) -> dict[str, object]:
    secret = _require_material(key_ref.material)
    return {"hmac_keys": [{"kind": "raw", "key": secret, "kid": key_ref.kid}]}


def digest(payload: bytes) -> bytes:
    return hashlib.sha256(payload).digest()


def async_chunks(data: bytes, *, size: int = 5) -> Callable[[], AsyncIterator[bytes]]:
    async def _iterator() -> AsyncIterator[bytes]:
        for idx in range(0, len(data), size):
            await asyncio.sleep(0)
            yield data[idx : idx + size]

    return _iterator


def ensure_pgpy_available() -> None:
    if not _PGPY_AVAILABLE:
        raise RuntimeError("pgpy is required for OpenPGP integration tests")


def generate_openpgp_keypair(common_name: str) -> tuple[str, str]:
    ensure_pgpy_available()
    key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = pgpy.PGPUID.new(common_name)
    key.add_uid(
        uid,
        usage={KeyFlags.Sign},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )
    return str(key), str(key.pubkey)


async def build_media_signer_with_openpgp(
    label: str,
) -> tuple[MediaSigner, InMemoryKeyProvider, KeyRef]:
    """Instantiate ``MediaSigner`` with an OpenPGP key pair."""

    ensure_pgpy_available()
    provider = InMemoryKeyProvider()
    private_armored, public_armored = generate_openpgp_keypair(label)
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.RSA_PSS_SHA256,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label=label,
    )
    key_ref = await provider.import_key(
        spec,
        private_armored.encode("utf-8"),
        public=public_armored.encode("utf-8"),
    )
    signer = MediaSigner(key_provider=provider)
    return signer, provider, key_ref


def openpgp_private_entry(key_ref: KeyRef) -> dict[str, object]:
    return {"kind": "pgpy-key", "data": _require_material(key_ref.material)}


def openpgp_verify_opts(key_ref: KeyRef) -> dict[str, object]:
    return {
        "pubkeys": [{"kind": "pgpy-key", "data": _require_material(key_ref.public)}]
    }
