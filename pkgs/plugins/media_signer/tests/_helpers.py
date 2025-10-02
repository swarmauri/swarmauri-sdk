"""Shared helpers for MediaSigner optional signer integration tests."""

from __future__ import annotations

import asyncio
import hashlib
from typing import AsyncIterator, Callable, Tuple

from MediaSigner import MediaSigner
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyUse
from swarmauri_core.keys.types import KeyAlg, KeyClass, KeySpec
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider

CMS_FORMAT = "CMSSigner"
JWS_FORMAT = "JWSSigner"
OPENPGP_FORMAT = "OpenPGPSigner"
PDF_FORMAT = "PDFSigner"
XMLD_FORMAT = "XMLDSigner"

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


_RSA_PRIVATE_KEY = b"""-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCaqBvzwvcVs3je\nN2Aue3+qy7jiq2d8ByUjguLlSTTILkc5k8QphGaTOUazqrF1Rk6vGo/CV3ovvKQE\naKOeFsO/u2Dbbmy3y7xjZMaidFdCgI5gxIB+7rluC9pIbkO/4WUBkZ/DJd4iGBo4\n8dlYSQxO1D97mfWhdFTMbNQhIGqhg0eQeEWD8hOYaUA7v4jLtPDXalaw1zeZm2fX\nw/E0X5FGNz2xNJVrEhqBvNgiM1YF2p9p4ZHL5l0ETEh+Q9IpWDcpghadJkpwsNTx\n9c+YWRkdd+gv+aeVW1BWxeVaJOFisz+YIZK6tydhq7s30XwXteqh6mey15JAZac8\nfCJWGWp/AgMBAAECggEACH+hvuzBHyl+7tckKz8Qw5Xw/E5m9WMpy0sZ+iI3taMK\nuZiWeEw/nBTS/x8reUJPzezWZtuKagJ3u4ufJ292JPHAX3kwnY5N3+MId0zlWVDZ\n12oflYS7c9dQO21eaQuTEq7/Pyi0ODNoMtDiHKkxn/NR5GeQHpCB8xSCjlTLB0JV\nmTocwK/H08HGrxvJGksqcmJ6hdHhudIHHOVgGWlTvIIXNp6eJCAJZ7uVADgjd+Sw\n2I4Pf5C54mZ2X43PtcXmIEMRZHxzVdF6YOmRoXnzZ6zsrIb5LKEaIxttthDRynWL\n4oB+21aL8AmoFNhWNGYtJSazOnMixIc6DOsrCdIOQQKBgQDYTsPb8UG54mMWGXrf\npUvlI38vyf2FCEs5TgUAX2nofMJfBimazWdMW687zSGurxtIUkUDyetlPFpmYH+V\nbXXzKWDzeuzCN2uxLZCstsXy5EZ6jqsvLjdKm3nAe//Yh0xrxtDwV9wDD0lM6v9c\naGAXpE8miwGUUJD7r6M0KyU3pwKBgQC3CTyQnOMdp1BkpRQGE29wJ2Olsh/Fo7fN\n8HPN8cQaTB9l9owDzdmcyOjItA1Q5cI5z8Bgrqcsoqv5wz0iOaMOAxPYYlq3vJOy\ntvCpKDcmfKceq5FbzsM+xi468KLpiUZXRg557VL+szsWvECD0JNqfxYoJZUrvUQj\nJt9g4DCRaQKBgC/bnXH4OvaJpCqrkIgS5mvYIrfMFQ9t+la/cFPYyHHryIWFs4bQ\nk15NmsO8awtfKsYhjat87VwEsmucRh4ljcczDIRSWjfOU0FsN2o/NiS7ZOyQzEcw\nDoOvSozP4pdhuALQhkHm7oKuyyT9iWpEnZ4deHWqo7rQ6IMHJTDRqvZZAoGBAJBK\nZ8RY6XHnBClTOYXQrHjtlFB7KzDS74MZmzEu9jkE6Xun8JjPHk3K1DfkONsdRQ/u\nBuowxPkbBBfRIdBpP3E8W9ipMHrH3md0cCPp4BAnFFfJSL3nMWO7N5afPM59uUXz\npFXaESNYh6xUm0dOlefOZ9keR4pDmgNcEZx9H8yBAoGBAKhCtxwlkuejk3KSkjKO\nCXdrP8pIoYBzhG4d4sLsu8JlZgnnq7HOsj/eOddPVFV1FV9+36hLItJmE7WUiWtJ\nzCCZQY4MYtANM3+GyDs7AAoHwfDHB/r3CJakhK/PY7+bKGCrapRcSEQgjuNXEKiV\n4XUqiRa96Gph63R3SHodLwCV\n-----END PRIVATE KEY-----\n"""

_RSA_CERTIFICATE = b"""-----BEGIN CERTIFICATE-----\nMIIDFzCCAf+gAwIBAgIUJkJhcD0UvfAwxNAmraCQQmIxvGswDQYJKoZIhvcNAQEL\nBQAwGzEZMBcGA1UEAwwQTWVkaWFTaWduZXIgVGVzdDAeFw0yNTEwMDIxNjQ5Mjda\nFw0yNjEwMDIxNjQ5MjdaMBsxGTAXBgNVBAMMEE1lZGlhU2lnbmVyIFRlc3QwggEi\nMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCaqBvzwvcVs3jeN2Aue3+qy7ji\nq2d8ByUjguLlSTTILkc5k8QphGaTOUazqrF1Rk6vGo/CV3ovvKQEaKOeFsO/u2Db\nbmy3y7xjZMaidFdCgI5gxIB+7rluC9pIbkO/4WUBkZ/DJd4iGBo48dlYSQxO1D97\nmfWhdFTMbNQhIGqhg0eQeEWD8hOYaUA7v4jLtPDXalaw1zeZm2fXw/E0X5FGNz2x\nNJVrEhqBvNgiM1YF2p9p4ZHL5l0ETEh+Q9IpWDcpghadJkpwsNTx9c+YWRkdd+gv\n+aeVW1BWxeVaJOFisz+YIZK6tydhq7s30XwXteqh6mey15JAZac8fCJWGWp/AgMB\nAAGjUzBRMB0GA1UdDgQWBBTBBqfopWu9a3Ut88PYjQYUdzQWsjAfBgNVHSMEGDAW\ngBTBBqfopWu9a3Ut88PYjQYUdzQWsjAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3\nDQEBCwUAA4IBAQBrg0eE/WU+O3AsKdOszx3PMaqhtlDNQ0jYqqrebCX6q903NcJk\nDsiJ+m+WxN/BY9ccIMv2/2u1z12OHQQ1o+x6NXXiVZr8IojWojDuB6r6w3V3wqxz\nde4wgeHXATLS9WCCc9wY3puhf9xSobUAezFjGy40/vB6QWMzN+iIwxSkCS+CQFxZ\nKovSujkZYzFkY58VYLugrIFBOaZmeTyKhGyXyzJuaVDEU3qAX5W4w1/eXQNEzeEi\nQCWd+WI9U00/+1GTW+mmGF5VnHRq1LDiLrJQi7Si/aGY8sazZYEEC8lrzn0XGlU4\n25Q0q5Bq960uTrmz38T3a9waiwZNSUi05zT5\n-----END CERTIFICATE-----\n"""


def generate_self_signed_rsa(_common_name: str) -> Tuple[bytes, bytes]:
    """Return a reusable self-signed RSA key pair for tests.

    The helper previously generated keys dynamically using ``cryptography``, but
    that dependency is not available in the constrained test environment. A
    static key pair is sufficient for exercising the MediaSigner facades, so we
    reuse deterministic PEM payloads to avoid the heavy runtime requirement.
    """

    return _RSA_PRIVATE_KEY, _RSA_CERTIFICATE


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
