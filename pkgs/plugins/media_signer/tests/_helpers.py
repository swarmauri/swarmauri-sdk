"""Shared helpers for MediaSigner optional signer integration tests."""

from __future__ import annotations

import asyncio
import hashlib
from typing import AsyncIterator, Callable

from MediaSigner import MediaSigner
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyUse
from swarmauri_core.keys.types import KeyAlg, KeyClass, KeySpec
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider

CMS_FORMAT = "CMSSigner"
JWS_FORMAT = "JWSSigner"
OPENPGP_FORMAT = "OpenPGPSigner"
PDF_FORMAT = "PDFSigner"
XMLD_FORMAT = "XMLDSigner"

_RSA_PRIVATE_KEY_PEM = b"""-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDO+kRGknpUpTD9
8ccJ6qkd/NL/TAcaY0shhJ1hUyXAaAqus7wfdsHhDgfJG53q2nLI0tbMp/ksy/b1
yR3fN3xs6wBi3VzCmBuQj3XyoZbDW9cEHttXja7nRZ0sGbHqnrCU4JJg48G88j5M
YwG0dh/nCYGII3FIke3XorpJ1N/Ie2b8eqfrFAqTMT6d5FLnAigLbYhQxbO3AxSA
fQn/IvuA2JZU2lfuoZDzQhQBgBj+KZOvQdOsWo0+Fcprm1Tin/epfHGGpodlZ2Mp
7xxY/IJOdn7Vz9WKQ+/ewHrvyqpvjgPDJjNC49rPwPXbOxpmTSVT/3WGumgwyUDd
a2zQLw4dAgMBAAECggEADwsPB88RH5JTDX3zYLPiv0h3IHGK6Z7SYNkF5EM6EPIu
5pQvJd1IiZ4usC327BEc+x4h2QWTXW9kn2gS6PycKUFqSYU7vvP1uuvGX5BhiAjm
h4jjmck1L192pTQn43zNqkBpOywKknxLzVr7zn0wY+cjuDyVOPhMQFo2LnQPoL8/
zXoUc/qzz9y0vP0X297oAYcY1EG3jI2jzYdo07k7R54BeAYZFJkX3MPp+fL6D1u5
OT8ODLu/0nY07xZ92sZFY6ikCepuihW8q08pprkyBKg9/yr30EDf8YMGbBkWuMtb
fTg+vkPoeD52yCKrgSdXxy1Qk/yan9Ngwhl0vakcQQKBgQD1SQp5Yw6DH1G1d+aL
wH/XYfGRxI0ooF5o6tdz9MxG2E3beR9k2FDc2xO+dl7NLHLEF4fL9+lAWGMx38YR
LHVoBm0/9tKi651nv0UNgCDXmbf9/QLJmElAoJyeJ4+uLjdSxftch5Zz55ujPyad
WdrxwbM3TAtacl/xog0FqsiMwQKBgQDYBNdO8yBtGcvAk2JvzbjHVYrwTsm+0RZZ
KGYpWQgJWtoUWvQ/1nGSEXKysMtUsioCLn4n6M0DTyuYMcmhwC7TMq1k8Fdvcgxe
wu+NWubi8cjGEzXE+gtVuTDHNd6G78NgATnV6VcQPDFcMqKi0Fc5qDGgLSg+BhtZ
H0aMfhLsXQKBgAGTX4raFQzIlbjJtWRubyPOEEQ0dAevyAt6frnS98D4wL9JLudx
8EsK6TyO/BrrTy1tTUUFKa1tI+39FwOjOnnZmLgReNbtFozFEMd+bDeWWDU8e9kZ
rlbI8VievnCLAXX5qZy1jkTeVwSccj4OhraI3QLc7TG+jFk8BkNkDnfBAoGAClpp
C1KhujjjSA6ISD1+3qbd6tiL2MZioNFL3C11MiWVkCYv0KNxfAO0EJZimGOVmdcq
mrUQplj0CO5R8JuqYtrp7o2KU0APEbecDZVOvY/DBKNFD3TAeFJQ4StWx/bT0VUd
tX/ieVe5MecHXnBHze6eukOPyzE1vFbAZdlhBM0CgYEAn6Wakl/MnbEbfdtKw8BJ
r3r7Jum7Kh4Q0/TyUiEynplPg5I53GUyW9zDwvzZ+Ms60TaBIEwiVTfiDFshR5vV
+5gPrMS8OzAuwAGHjyEziblnb6/2K+pUOtHkb91AOhvX4SH1GBLUgjQ7xy6IrEgz
EK+YnZ40o0Iyt7pZOuSe1wI=
-----END PRIVATE KEY-----
"""

_RSA_CERT_PEM = b"""-----BEGIN CERTIFICATE-----
MIIDFzCCAf+gAwIBAgIULnIzyghNG0P24HGvrm7bFHWyIWMwDQYJKoZIhvcNAQEL
BQAwGzEZMBcGA1UEAwwQTWVkaWFTaWduZXIgVGVzdDAeFw0yNTEwMDIxNjQ5NTZa
Fw0yNjEwMDIxNjQ5NTZaMBsxGTAXBgNVBAMMEE1lZGlhU2lnbmVyIFRlc3QwggEi
MA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDO+kRGknpUpTD98ccJ6qkd/NL/
TAcaY0shhJ1hUyXAaAqus7wfdsHhDgfJG53q2nLI0tbMp/ksy/b1yR3fN3xs6wBi
3VzCmBuQj3XyoZbDW9cEHttXja7nRZ0sGbHqnrCU4JJg48G88j5MYwG0dh/nCYGI
I3FIke3XorpJ1N/Ie2b8eqfrFAqTMT6d5FLnAigLbYhQxbO3AxSAfQn/IvuA2JZU
2lfuoZDzQhQBgBj+KZOvQdOsWo0+Fcprm1Tin/epfHGGpodlZ2Mp7xxY/IJOdn7V
z9WKQ+/ewHrvyqpvjgPDJjNC49rPwPXbOxpmTSVT/3WGumgwyUDda2zQLw4dAgMB
AAGjUzBRMB0GA1UdDgQWBBSR2hTsWR+Gyof5a/STime7plN00TAfBgNVHSMEGDAW
gBSR2hTsWR+Gyof5a/STime7plN00TAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3
DQEBCwUAA4IBAQCzGd5+UAEY+ArvjOhOt8agsspH97Ps5vK1dwsYEs02phJWvU3u
anRXSigLHIJr26xp1x2dRyo28J9VQ4Lk4UShrgkB54+LznbWXHvntGk4kLr2JXxE
UxdgkintZ4DJbux8d57ANK6v7HcQ3tWrTJauECN7IyR06oeb3pEdxE6f0BDzB/dw
Ukpm8eVzK8xA6lAPoSU8lnpmH4djQZ4MYDMLifjFXyz39Jx5h/cyf/eGV4q8qKDU
yXywOPB1xeJDrGURsd9ioMgzAEO3v2xVRqM4Wv08e431v8JYdHXpZ5Q5qMdFEG18
MLbFIyUnus65d+EOqmBu9s86D7XyckL2Hgrx
-----END CERTIFICATE-----
"""

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


def generate_self_signed_rsa(common_name: str) -> tuple[bytes, bytes]:
    """Return a deterministic RSA key pair for signer integrations."""

    _ = common_name  # maintained for compatibility with existing helpers
    return _RSA_PRIVATE_KEY_PEM, _RSA_CERT_PEM


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
