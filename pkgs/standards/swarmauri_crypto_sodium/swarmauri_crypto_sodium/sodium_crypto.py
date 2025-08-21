"""Libsodium-backed crypto provider (no PyNaCl).

Implements the ICrypto contract using:
- XChaCha20-Poly1305-IETF for symmetric AEAD
- Ed25519 for sign/verify
- X25519 sealed boxes for:
    • sealing/unsealing data (X25519-SEALEDBOX)
    • wrapping/unwrapping DEKs (X25519-SEAL-WRAP)
- encrypt_for_many:
    • sealed-style (enc_alg="X25519-SEALEDBOX")
    • KEM+AEAD (enc_alg="XCHACHA20-POLY1305", recipient_wrap_alg="X25519-SEAL-WRAP")

This implementation calls libsodium via ctypes and does not depend on PyNaCl.
"""

from __future__ import annotations

import os
import secrets
import sys
from ctypes import (
    CDLL,
    POINTER,
    byref,
    c_int,
    c_ubyte,
    c_ulonglong,
    create_string_buffer,
)
from functools import lru_cache
from typing import Any, Dict, Iterable, Literal, Optional

from swarmauri_core.crypto.types import (
    AEADCiphertext,
    Alg,
    KeyRef,
    MultiRecipientEnvelope,
    RecipientInfo,
    Signature,
    UnsupportedAlgorithm,
    WrappedKey,
    IntegrityError,
)
from swarmauri_base.crypto.CryptoBase import CryptoBase


# ---------- libsodium constants ----------
_XCHACHA_KEYBYTES = 32
_XCHACHA_NPUBBYTES = 24
_XCHACHA_ABYTES = 16

_CRYPTO_BOX_PUBLICKEYBYTES = 32
_CRYPTO_BOX_SECRETKEYBYTES = 32
_CRYPTO_BOX_SEALBYTES = 48  # 32 (pk) + 16 (mac)

_CRYPTO_SIGN_PUBLICKEYBYTES = 32
_CRYPTO_SIGN_SECRETKEYBYTES = 64
_CRYPTO_SIGN_BYTES = 64

_AEAD_DEFAULT = "XCHACHA20-POLY1305"
_SEAL_ALG = "X25519-SEALEDBOX"
_WRAP_ALG = "X25519-SEAL-WRAP"
_SIGN_ALG = "ED25519"


# ---------- libsodium loader ----------
def _load_libsodium() -> CDLL:
    """Load the libsodium shared library."""
    env = os.environ.get("LIBSODIUM_PATH")
    if env and os.path.exists(env):
        return CDLL(env)

    names: list[str] = []
    if sys.platform.startswith("linux"):
        names = ["libsodium.so.23", "libsodium.so"]
    elif sys.platform == "darwin":
        names = ["libsodium.23.dylib", "libsodium.dylib", "lib/libsodium.dylib"]
    elif sys.platform.startswith("win"):
        names = ["libsodium.dll", "sodium.dll"]
    for n in names:
        try:
            return CDLL(n)
        except OSError:
            continue
    raise RuntimeError(
        "Could not load libsodium. Set LIBSODIUM_PATH or install libsodium."
    )


@lru_cache(maxsize=1)
def _sodium() -> CDLL:
    """Initialize libsodium and configure function prototypes."""
    lib = _load_libsodium()

    # int sodium_init(void)
    lib.sodium_init.restype = c_int
    if lib.sodium_init() < 0:
        raise RuntimeError("sodium_init failed")

    # AEAD XChaCha20-Poly1305-IETF
    lib.crypto_aead_xchacha20poly1305_ietf_encrypt.restype = c_int
    lib.crypto_aead_xchacha20poly1305_ietf_encrypt.argtypes = [
        POINTER(c_ubyte),
        POINTER(c_ulonglong),
        POINTER(c_ubyte),
        c_ulonglong,
        POINTER(c_ubyte),
        c_ulonglong,
        POINTER(c_ubyte),
        POINTER(c_ubyte),
        POINTER(c_ubyte),
    ]

    lib.crypto_aead_xchacha20poly1305_ietf_decrypt.restype = c_int
    lib.crypto_aead_xchacha20poly1305_ietf_decrypt.argtypes = [
        POINTER(c_ubyte),
        POINTER(c_ulonglong),
        POINTER(c_ubyte),
        POINTER(c_ubyte),
        c_ulonglong,
        POINTER(c_ubyte),
        c_ulonglong,
        POINTER(c_ubyte),
        POINTER(c_ubyte),
    ]

    # Sealed boxes
    lib.crypto_box_seal.restype = c_int
    lib.crypto_box_seal.argtypes = [
        POINTER(c_ubyte),
        POINTER(c_ubyte),
        c_ulonglong,
        POINTER(c_ubyte),
    ]

    lib.crypto_box_seal_open.restype = c_int
    lib.crypto_box_seal_open.argtypes = [
        POINTER(c_ubyte),
        POINTER(c_ubyte),
        c_ulonglong,
        POINTER(c_ubyte),
        POINTER(c_ubyte),
    ]

    # Ed25519
    lib.crypto_sign_ed25519_detached.restype = c_int
    lib.crypto_sign_ed25519_detached.argtypes = [
        POINTER(c_ubyte),
        POINTER(c_ulonglong),
        POINTER(c_ubyte),
        c_ulonglong,
        POINTER(c_ubyte),
    ]

    lib.crypto_sign_ed25519_verify_detached.restype = c_int
    lib.crypto_sign_ed25519_verify_detached.argtypes = [
        POINTER(c_ubyte),
        POINTER(c_ubyte),
        c_ulonglong,
        POINTER(c_ubyte),
    ]

    return lib


# ---------- helpers ----------
def _as_ubytes(b: bytes) -> POINTER(c_ubyte):
    return (c_ubyte * len(b)).from_buffer_copy(b)


def _ensure_len(name: str, b: Optional[bytes], *sizes: int) -> bytes:
    if b is None:
        raise ValueError(f"{name} is required")
    if len(sizes) and len(b) not in sizes:
        raise IntegrityError(f"{name} must be one of lengths {sizes}, got {len(b)}")
    return b


def _normalize_aead_alg(alg: Any) -> Alg:
    a = (alg.value if hasattr(alg, "value") else alg) or _AEAD_DEFAULT
    if a.upper() in ("XCHACHA20_POLY1305", "XCHACHA20-POLY1305"):
        return _AEAD_DEFAULT
    return a


# =========================== Provider ===========================


class SodiumCrypto(CryptoBase):
    """Libsodium-backed provider (no PyNaCl)."""

    type: Literal["SodiumCrypto"] = "SodiumCrypto"

    # ---------------- capabilities ----------------
    def supports(self) -> Dict[str, Iterable[Alg]]:
        return {
            "encrypt": (_AEAD_DEFAULT,),
            "decrypt": (_AEAD_DEFAULT,),
            "wrap": (_WRAP_ALG,),
            "unwrap": (_WRAP_ALG,),
            "sign": (_SIGN_ALG,),
            "verify": (_SIGN_ALG,),
            "seal": (_SEAL_ALG,),
            "unseal": (_SEAL_ALG,),
        }

    # ---------------- AEAD: XChaCha20-Poly1305 ----------------
    async def encrypt(
        self,
        key: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> AEADCiphertext:
        alg = _normalize_aead_alg(alg)
        if alg != _AEAD_DEFAULT:
            raise UnsupportedAlgorithm(f"Unsupported AEAD algorithm: {alg}")

        k = _ensure_len("AEAD key.material", key.material, _XCHACHA_KEYBYTES)
        npub = nonce or secrets.token_bytes(_XCHACHA_NPUBBYTES)
        if len(npub) != _XCHACHA_NPUBBYTES:
            raise IntegrityError(f"nonce must be {_XCHACHA_NPUBBYTES} bytes")

        ad = aad or b""
        m = pt

        c_len = len(m) + _XCHACHA_ABYTES
        c_buf = create_string_buffer(c_len)
        c_len_out = c_ulonglong(0)

        rc = _sodium().crypto_aead_xchacha20poly1305_ietf_encrypt(
            c_buf,
            byref(c_len_out),
            _as_ubytes(m),
            c_ulonglong(len(m)),
            _as_ubytes(ad),
            c_ulonglong(len(ad)),
            None,
            _as_ubytes(npub),
            _as_ubytes(k),
        )
        if rc != 0:
            raise IntegrityError("AEAD encrypt failed")

        c = c_buf.raw[: c_len_out.value]
        ct, tag = c[:-_XCHACHA_ABYTES], c[-_XCHACHA_ABYTES:]

        return AEADCiphertext(
            kid=key.kid,
            version=key.version,
            alg=_AEAD_DEFAULT,
            nonce=npub,
            ct=ct,
            tag=tag,
            aad=ad if ad else None,
        )

    async def decrypt(
        self,
        key: KeyRef,
        ct: AEADCiphertext,
        *,
        aad: Optional[bytes] = None,
    ) -> bytes:
        if _normalize_aead_alg(ct.alg) != _AEAD_DEFAULT:
            raise UnsupportedAlgorithm(f"Unsupported AEAD algorithm: {ct.alg}")

        k = _ensure_len("AEAD key.material", key.material, _XCHACHA_KEYBYTES)
        if len(ct.nonce) != _XCHACHA_NPUBBYTES:
            raise IntegrityError(f"nonce must be {_XCHACHA_NPUBBYTES} bytes")

        ad = aad if aad is not None else (ct.aad or b"")
        blob = ct.ct + ct.tag

        m_buf = create_string_buffer(len(blob))
        m_len_out = c_ulonglong(0)

        rc = _sodium().crypto_aead_xchacha20poly1305_ietf_decrypt(
            m_buf,
            byref(m_len_out),
            None,
            _as_ubytes(blob),
            c_ulonglong(len(blob)),
            _as_ubytes(ad),
            c_ulonglong(len(ad)),
            _as_ubytes(ct.nonce),
            _as_ubytes(k),
        )
        if rc != 0:
            raise IntegrityError("AEAD decrypt failed (auth?)")

        return m_buf.raw[: m_len_out.value]

    # ---------------- sign / verify (Ed25519) ----------------
    async def sign(
        self,
        key: KeyRef,
        msg: bytes,
        *,
        alg: Optional[Alg] = None,
    ) -> Signature:
        alg = (alg or _SIGN_ALG).upper()
        if alg != _SIGN_ALG:
            raise UnsupportedAlgorithm(f"Unsupported sign alg: {alg}")
        sk = _ensure_len(
            "Ed25519 key.material", key.material, _CRYPTO_SIGN_SECRETKEYBYTES
        )

        sig_buf = create_string_buffer(_CRYPTO_SIGN_BYTES)
        sig_len = c_ulonglong(0)
        rc = _sodium().crypto_sign_ed25519_detached(
            sig_buf,
            byref(sig_len),
            _as_ubytes(msg),
            c_ulonglong(len(msg)),
            _as_ubytes(sk),
        )
        if rc != 0:
            raise IntegrityError("sign failed")
        sig = sig_buf.raw[: sig_len.value]
        return Signature(kid=key.kid, alg=_SIGN_ALG, sig=sig)

    async def verify(
        self,
        key: KeyRef,
        msg: bytes,
        sig: Signature,
    ) -> bool:
        if (sig.alg or _SIGN_ALG).upper() != _SIGN_ALG:
            raise UnsupportedAlgorithm(f"Unsupported sign alg: {sig.alg}")
        pk = _ensure_len("Ed25519 key.public", key.public, _CRYPTO_SIGN_PUBLICKEYBYTES)
        rc = _sodium().crypto_sign_ed25519_verify_detached(
            _as_ubytes(sig.sig),
            _as_ubytes(msg),
            c_ulonglong(len(msg)),
            _as_ubytes(pk),
        )
        return rc == 0

    # ---------------- wrap / unwrap (X25519 sealed wrap) ----------------
    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: Optional[bytes] = None,
        wrap_alg: Optional[Alg] = None,
        nonce: Optional[bytes] = None,
    ) -> WrappedKey:
        alg = (wrap_alg or _WRAP_ALG).upper()
        if alg != _WRAP_ALG:
            raise UnsupportedAlgorithm(f"Unsupported wrap alg: {alg}")
        pk = _ensure_len("X25519 kek.public", kek.public, _CRYPTO_BOX_PUBLICKEYBYTES)
        key = dek or secrets.token_bytes(_XCHACHA_KEYBYTES)
        out_len = len(key) + _CRYPTO_BOX_SEALBYTES
        out = create_string_buffer(out_len)
        rc = _sodium().crypto_box_seal(
            out,
            _as_ubytes(key),
            c_ulonglong(len(key)),
            _as_ubytes(pk),
        )
        if rc != 0:
            raise IntegrityError("wrap failed")
        return WrappedKey(
            kek_kid=kek.kid,
            kek_version=kek.version,
            wrap_alg=_WRAP_ALG,
            wrapped=out.raw,
            nonce=None,
        )

    async def unwrap(self, kek: KeyRef, wrapped: WrappedKey) -> bytes:
        if (wrapped.wrap_alg or _WRAP_ALG).upper() != _WRAP_ALG:
            raise UnsupportedAlgorithm(f"Unsupported wrap alg: {wrapped.wrap_alg}")
        pk = _ensure_len("X25519 kek.public", kek.public, _CRYPTO_BOX_PUBLICKEYBYTES)
        sk = _ensure_len(
            "X25519 kek.material", kek.material, _CRYPTO_BOX_SECRETKEYBYTES
        )
        m_buf = create_string_buffer(len(wrapped.wrapped) - _CRYPTO_BOX_SEALBYTES)
        rc = _sodium().crypto_box_seal_open(
            m_buf,
            _as_ubytes(wrapped.wrapped),
            c_ulonglong(len(wrapped.wrapped)),
            _as_ubytes(pk),
            _as_ubytes(sk),
        )
        if rc != 0:
            raise IntegrityError("unwrap failed")
        return m_buf.raw

    # ---------------- seal / unseal data ----------------
    async def seal(
        self,
        recipient: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
    ) -> bytes:
        alg = (alg or _SEAL_ALG).upper()
        if alg != _SEAL_ALG:
            raise UnsupportedAlgorithm(f"Unsupported seal alg: {alg}")
        pk = _ensure_len(
            "X25519 recipient.public", recipient.public, _CRYPTO_BOX_PUBLICKEYBYTES
        )
        out_len = len(pt) + _CRYPTO_BOX_SEALBYTES
        out = create_string_buffer(out_len)
        rc = _sodium().crypto_box_seal(
            out,
            _as_ubytes(pt),
            c_ulonglong(len(pt)),
            _as_ubytes(pk),
        )
        if rc != 0:
            raise IntegrityError("seal failed")
        return out.raw

    async def unseal(
        self,
        recipient_priv: KeyRef,
        sealed: bytes,
        *,
        alg: Optional[Alg] = None,
    ) -> bytes:
        alg = (alg or _SEAL_ALG).upper()
        if alg != _SEAL_ALG:
            raise UnsupportedAlgorithm(f"Unsupported seal alg: {alg}")
        pk = _ensure_len(
            "X25519 recipient.public", recipient_priv.public, _CRYPTO_BOX_PUBLICKEYBYTES
        )
        sk = _ensure_len(
            "X25519 recipient.material",
            recipient_priv.material,
            _CRYPTO_BOX_SECRETKEYBYTES,
        )
        m_buf = create_string_buffer(len(sealed) - _CRYPTO_BOX_SEALBYTES)
        rc = _sodium().crypto_box_seal_open(
            m_buf,
            _as_ubytes(sealed),
            c_ulonglong(len(sealed)),
            _as_ubytes(pk),
            _as_ubytes(sk),
        )
        if rc != 0:
            raise IntegrityError("unseal failed")
        return m_buf.raw

    # ---------------- encrypt for many ----------------
    async def encrypt_for_many(
        self,
        recipients: Iterable[KeyRef],
        pt: bytes,
        *,
        enc_alg: Optional[Alg] = None,
        recipient_wrap_alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> MultiRecipientEnvelope:
        enc_alg = (enc_alg or _AEAD_DEFAULT).upper()
        if enc_alg == _SEAL_ALG:
            infos = []
            for r in recipients:
                pk = _ensure_len(
                    "X25519 recipient.public", r.public, _CRYPTO_BOX_PUBLICKEYBYTES
                )
                out_len = len(pt) + _CRYPTO_BOX_SEALBYTES
                out = create_string_buffer(out_len)
                rc = _sodium().crypto_box_seal(
                    out,
                    _as_ubytes(pt),
                    c_ulonglong(len(pt)),
                    _as_ubytes(pk),
                )
                if rc != 0:
                    raise IntegrityError("seal failed")
                infos.append(
                    RecipientInfo(
                        kid=r.kid,
                        version=r.version,
                        wrap_alg=_SEAL_ALG,
                        wrapped_key=out.raw,
                        nonce=None,
                    )
                )
            return MultiRecipientEnvelope(
                enc_alg=_SEAL_ALG,
                nonce=b"",
                ct=b"",
                tag=b"",
                recipients=tuple(infos),
                aad=aad,
            )

        enc_alg = _normalize_aead_alg(enc_alg)
        if enc_alg != _AEAD_DEFAULT:
            raise UnsupportedAlgorithm(f"Unsupported enc_alg: {enc_alg}")

        wrap_alg = (recipient_wrap_alg or _WRAP_ALG).upper()
        if wrap_alg != _WRAP_ALG:
            raise UnsupportedAlgorithm(f"Unsupported recipient_wrap_alg: {wrap_alg}")

        cek = secrets.token_bytes(_XCHACHA_KEYBYTES)
        npub = nonce or secrets.token_bytes(_XCHACHA_NPUBBYTES)
        ad = aad or b""
        m = pt
        c_len = len(m) + _XCHACHA_ABYTES
        c_buf = create_string_buffer(c_len)
        c_len_out = c_ulonglong(0)
        rc = _sodium().crypto_aead_xchacha20poly1305_ietf_encrypt(
            c_buf,
            byref(c_len_out),
            _as_ubytes(m),
            c_ulonglong(len(m)),
            _as_ubytes(ad),
            c_ulonglong(len(ad)),
            None,
            _as_ubytes(npub),
            _as_ubytes(cek),
        )
        if rc != 0:
            raise IntegrityError("AEAD encrypt failed")
        blob = c_buf.raw[: c_len_out.value]
        shared_ct, tag = blob[:-_XCHACHA_ABYTES], blob[-_XCHACHA_ABYTES:]

        infos = []
        for r in recipients:
            pk = _ensure_len(
                "X25519 recipient.public", r.public, _CRYPTO_BOX_PUBLICKEYBYTES
            )
            out = create_string_buffer(len(cek) + _CRYPTO_BOX_SEALBYTES)
            rc = _sodium().crypto_box_seal(
                out,
                _as_ubytes(cek),
                c_ulonglong(len(cek)),
                _as_ubytes(pk),
            )
            if rc != 0:
                raise IntegrityError("wrap failed")
            infos.append(
                RecipientInfo(
                    kid=r.kid,
                    version=r.version,
                    wrap_alg=_WRAP_ALG,
                    wrapped_key=out.raw,
                    nonce=None,
                )
            )

        return MultiRecipientEnvelope(
            enc_alg=_AEAD_DEFAULT,
            nonce=npub,
            ct=shared_ct,
            tag=tag,
            recipients=tuple(infos),
            aad=ad if ad else None,
        )
