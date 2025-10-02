"""Utilities for MediaSigner integration tests."""

from __future__ import annotations

import hashlib
from typing import Sequence, Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
import pgpy
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)

from MediaSigner import MediaSigner
from swarmauri_core.crypto.types import ExportPolicy, KeyUse
from swarmauri_core.keys.types import KeyAlg, KeyClass, KeySpec
from swarmauri_certs_x509 import X509CertService
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider
from swarmauri_keyprovider_local import LocalKeyProvider


def sha256_digest(data: bytes) -> bytes:
    """Return the SHA-256 digest for ``data``."""

    return hashlib.sha256(data).digest()


def chunk_payload(data: bytes) -> list[bytes]:
    """Split ``data`` into two chunks for streaming tests."""

    midpoint = max(1, len(data) // 2)
    return [data[:midpoint], data[midpoint:]]


def sample_json_envelope(label: str) -> dict[str, object]:
    """Return a deterministic JSON envelope payload."""

    return {"label": label, "value": "swarmauri"}


def sample_pdf_bytes(label: str) -> bytes:
    """Return a minimal PDF-like byte payload."""

    return (
        b"%PDF-1.4\n"
        + f"1 0 obj<< /Title ({label}) >>\nendobj\n".encode("utf-8")
        + b"trailer<<>>\n%%EOF"
    )


def sample_xml_document(label: str) -> str:
    """Return a simple XML document."""

    return f"<document><label>{label}</label><value>swarmauri</value></document>"


async def build_rsa_cert_bundle(
    label: str,
) -> Tuple[MediaSigner, dict[str, object], bytes]:
    """Create a MediaSigner with an RSA key/certificate bundle."""

    provider = LocalKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.RSA_PSS_SHA256,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label=label,
    )
    key_ref = await provider.create_key(spec)
    cert_service = X509CertService()
    cert_pem = await cert_service.create_self_signed(
        key_ref,
        {"CN": f"{label}.example"},
        extensions={"basic_constraints": {"ca": False}},
    )
    key_entry: dict[str, object] = {
        "kind": "pem",
        "private_key": key_ref.material,
        "certificate": cert_pem,
    }
    return MediaSigner(key_provider=provider), key_entry, cert_pem


async def build_pdf_signer(label: str) -> Tuple[MediaSigner, dict[str, object], bytes]:
    """Return MediaSigner setup for PDF tests."""

    return await build_rsa_cert_bundle(label)


async def build_xmld_signer(
    label: str,
) -> Tuple[MediaSigner, dict[str, object], Sequence[bytes]]:
    """Return MediaSigner setup for XMLD signer tests."""

    signer, key_entry, cert_pem = await build_rsa_cert_bundle(label)
    return signer, key_entry, (cert_pem,)


async def build_openpgp_material(
    label: str,
) -> Tuple[MediaSigner, dict[str, object], Sequence[dict[str, object]]]:
    """Create OpenPGP signing material backed by an InMemory provider."""

    provider = InMemoryKeyProvider()
    key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = pgpy.PGPUID.new(f"{label.title()} Tester", email=f"{label}@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.Sign},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )
    private_str = str(key)
    public_str = str(key.pubkey)
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.RSA_PSS_SHA256,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label=label,
    )
    await provider.import_key(
        spec,
        material=private_str.encode("utf-8"),
        public=public_str.encode("utf-8"),
    )
    private_entry = {"kind": "pgpy-key", "data": private_str}
    public_entries = ({"kind": "pgpy-key", "data": public_str},)
    return MediaSigner(key_provider=provider), private_entry, public_entries


async def build_jws_material(
    label: str,
) -> Tuple[MediaSigner, dict[str, object], dict[str, Sequence[bytes]]]:
    """Create Ed25519 material suitable for the JWS signer."""

    provider = InMemoryKeyProvider()
    sk = ed25519.Ed25519PrivateKey.generate()
    private_bytes = sk.private_bytes(
        serialization.Encoding.Raw,
        serialization.PrivateFormat.Raw,
        serialization.NoEncryption(),
    )
    public_bytes = sk.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label=label,
    )
    await provider.import_key(spec, material=private_bytes, public=public_bytes)
    key_entry = {"kind": "raw_ed25519_sk", "bytes": private_bytes}
    verify_opts = {"ed_pubkeys": (public_bytes,)}
    return MediaSigner(key_provider=provider), key_entry, verify_opts
