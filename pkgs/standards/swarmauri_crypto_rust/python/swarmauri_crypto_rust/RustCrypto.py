"""Rust-backed crypto provider using ring and maturin.

Implements the ICrypto contract using:
- ChaCha20-Poly1305 for symmetric AEAD
- X25519 for key agreement (simplified implementation)
- High-performance Rust backend via ring crate

This implementation uses Rust's ring cryptography library through
Python bindings created with maturin/PyO3.
"""

from __future__ import annotations

import secrets
import warnings
from typing import Dict, Iterable, Literal, Optional

from swarmauri_core.crypto.types import (
    AEADCiphertext as CoreAEADCiphertext,
    Alg,
    IntegrityError,
    KeyRef,
    MultiRecipientEnvelope,
    RecipientInfo,
    UnsupportedAlgorithm,
    WrappedKey as CoreWrappedKey,
)
from swarmauri_core.crypto.types import (
    KeyType,
    KeyUse,
    ExportPolicy,
)  # re-export for tests
from swarmauri_base.crypto.CryptoBase import CryptoBase

# Try to import the Rust extension
try:
    from swarmauri_crypto_rust._rust_crypto import (
        RustCrypto as _RustCrypto,
        AEADCiphertext as _RustAEADCiphertext,
        WrappedKey as _RustWrappedKey,
        KeyRef as _RustKeyRef,
    )

    _RUST_AVAILABLE = True
except ImportError as e:
    warnings.warn(
        f"Rust crypto backend not available: {e}. Using fallback implementation."
    )
    _RUST_AVAILABLE = False

    # Create dummy classes for development
    class _RustCrypto:
        def __init__(self):
            raise ImportError("Rust backend not available")


# ---------- Constants ----------
_AEAD_DEFAULT = "CHACHA20-POLY1305"
_WRAP_ALG = "ECDH-ES+A256KW"
_SEAL_ALG = "X25519-SEAL"


def _convert_key_to_rust(key: KeyRef) -> "_RustKeyRef":
    """Convert swarmauri KeyRef to Rust KeyRef"""
    uses = [use.value if hasattr(use, "value") else str(use) for use in key.uses]
    key_type = key.type.value if hasattr(key.type, "value") else str(key.type)

    return _RustKeyRef(
        kid=key.kid,
        version=key.version,
        key_type=key_type,
        uses=uses,
        material=key.material,
        public=key.public,
    )


def _convert_rust_to_core_ciphertext(
    rust_ct: "_RustAEADCiphertext",
) -> CoreAEADCiphertext:
    """Convert Rust AEADCiphertext to core AEADCiphertext"""
    return CoreAEADCiphertext(
        kid=rust_ct.kid,
        version=rust_ct.version,
        alg=rust_ct.alg,
        nonce=bytes(rust_ct.nonce),
        ct=bytes(rust_ct.ct),
        tag=bytes(rust_ct.tag),
        aad=bytes(rust_ct.aad) if rust_ct.aad else None,
    )


def _convert_core_to_rust_ciphertext(
    core_ct: CoreAEADCiphertext,
) -> "_RustAEADCiphertext":
    """Convert core AEADCiphertext to Rust AEADCiphertext"""
    return _RustAEADCiphertext(
        kid=core_ct.kid,
        version=core_ct.version,
        alg=core_ct.alg,
        nonce=list(core_ct.nonce),
        ct=list(core_ct.ct),
        tag=list(core_ct.tag),
        aad=list(core_ct.aad) if core_ct.aad else None,
    )


class RustCrypto(CryptoBase):
    """Rust-backed crypto provider using ring crate."""

    type: Literal["RustCrypto"] = "RustCrypto"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not _RUST_AVAILABLE:
            raise ImportError(
                "Rust crypto backend is not available. "
                "Please ensure the package was built with maturin."
            )
        self._rust_crypto = _RustCrypto()

    # ---------------- capabilities ----------------
    def supports(self) -> Dict[str, Iterable[Alg]]:
        if not _RUST_AVAILABLE:
            return {}

        rust_supports = self._rust_crypto.supports()
        return {key: tuple(algs) for key, algs in rust_supports.items()}

    # ---------------- AEAD: ChaCha20-Poly1305 ----------------
    async def encrypt(
        self,
        key: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> CoreAEADCiphertext:
        alg = alg or _AEAD_DEFAULT
        if alg != _AEAD_DEFAULT:
            raise UnsupportedAlgorithm(f"Unsupported AEAD algorithm: {alg}")

        if not key.material or len(key.material) != 32:
            raise IntegrityError("Key material must be 32 bytes")

        try:
            rust_key = _convert_key_to_rust(key)
            rust_ct = self._rust_crypto.encrypt(rust_key, pt, nonce, aad)
            return _convert_rust_to_core_ciphertext(rust_ct)
        except Exception as e:
            raise IntegrityError(f"Encryption failed: {e}")

    async def decrypt(
        self,
        key: KeyRef,
        ct: CoreAEADCiphertext,
        *,
        aad: Optional[bytes] = None,
    ) -> bytes:
        if ct.alg != _AEAD_DEFAULT:
            raise UnsupportedAlgorithm(f"Unsupported AEAD algorithm: {ct.alg}")

        if not key.material or len(key.material) != 32:
            raise IntegrityError("Key material must be 32 bytes")

        try:
            rust_key = _convert_key_to_rust(key)
            rust_ct = _convert_core_to_rust_ciphertext(ct)
            return bytes(self._rust_crypto.decrypt(rust_key, rust_ct, aad))
        except Exception as e:
            raise IntegrityError(f"Decryption failed: {e}")

    # ---------------- wrap / unwrap using simplified ECDH ----------------
    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: Optional[bytes] = None,
        wrap_alg: Optional[Alg] = None,
        nonce: Optional[bytes] = None,
    ) -> CoreWrappedKey:
        wrap_alg = wrap_alg or _WRAP_ALG
        if wrap_alg != _WRAP_ALG:
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrap_alg}")

        dek = dek or secrets.token_bytes(32)
        if len(dek) != 32:
            raise IntegrityError("DEK must be 32 bytes")

        try:
            rust_kek = _convert_key_to_rust(kek)
            rust_wrapped = self._rust_crypto.wrap(rust_kek, dek)
            return CoreWrappedKey(
                kek_kid=kek.kid,
                kek_version=kek.version,
                wrap_alg=_WRAP_ALG,
                wrapped=bytes(rust_wrapped.wrapped),
            )
        except Exception as e:
            raise IntegrityError(f"Key wrapping failed: {e}")

    async def unwrap(self, kek: KeyRef, wrapped: CoreWrappedKey) -> bytes:
        if wrapped.wrap_alg != _WRAP_ALG:
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrapped.wrap_alg}")

        try:
            rust_kek = _convert_key_to_rust(kek)
            rust_wrapped = _RustWrappedKey(
                kek_kid=wrapped.kek_kid,
                kek_version=wrapped.kek_version,
                wrap_alg=wrapped.wrap_alg,
                wrapped=list(wrapped.wrapped),
            )
            return bytes(self._rust_crypto.unwrap(rust_kek, rust_wrapped))
        except Exception as e:
            raise IntegrityError(f"Key unwrapping failed: {e}")

    # ---------------- seal / unseal (placeholder) ----------------
    async def seal(
        self,
        recipient: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = _SEAL_ALG,
    ) -> bytes:
        if alg != _SEAL_ALG:
            raise UnsupportedAlgorithm(f"Unsupported seal alg: {alg}")

        # For now, use encrypt as a placeholder
        # In a full implementation, this would use X25519 sealed boxes
        try:
            # Generate a random nonce and encrypt
            nonce = secrets.token_bytes(12)
            ct = await self.encrypt(recipient, pt, nonce=nonce)
            # Return the entire encrypted structure as sealed data
            import json

            sealed_data = {
                "nonce": list(ct.nonce),
                "ct": list(ct.ct),
                "tag": list(ct.tag),
            }
            return json.dumps(sealed_data).encode()
        except Exception as e:
            raise IntegrityError(f"Sealing failed: {e}")

    async def unseal(
        self,
        recipient_priv: KeyRef,
        sealed: bytes,
        *,
        alg: Optional[Alg] = _SEAL_ALG,
    ) -> bytes:
        if alg != _SEAL_ALG:
            raise UnsupportedAlgorithm(f"Unsupported seal alg: {alg}")

        try:
            # Parse the sealed data and decrypt
            import json

            sealed_data = json.loads(sealed.decode())

            ct = CoreAEADCiphertext(
                kid=recipient_priv.kid,
                version=recipient_priv.version,
                alg=_AEAD_DEFAULT,
                nonce=bytes(sealed_data["nonce"]),
                ct=bytes(sealed_data["ct"]),
                tag=bytes(sealed_data["tag"]),
                aad=None,
            )
            return await self.decrypt(recipient_priv, ct)
        except Exception as e:
            raise IntegrityError(f"Unsealing failed: {e}")

    # ---------------- hybrid encrypt-for-many (simplified) ----------------
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
        # Simplified implementation using seal for each recipient
        enc_alg = enc_alg or _AEAD_DEFAULT

        if enc_alg == _SEAL_ALG:
            # Sealed-style variant
            infos: list[RecipientInfo] = []
            for r in recipients:
                sealed = await self.seal(r, pt)
                infos.append(
                    RecipientInfo(
                        kid=r.kid,
                        version=r.version,
                        wrap_alg=_SEAL_ALG,
                        wrapped_key=sealed,
                        nonce=None,
                    )
                )
            return MultiRecipientEnvelope(
                enc_alg=_SEAL_ALG,
                nonce=b"",
                ct=b"",
                tag=b"",
                recipients=tuple(infos),
                aad=None,
            )

        # KEM+AEAD variant (simplified)
        if enc_alg != _AEAD_DEFAULT:
            raise UnsupportedAlgorithm(f"Unsupported enc_alg: {enc_alg}")

        # Generate content encryption key
        cek_material = secrets.token_bytes(32)
        cek = KeyRef(
            kid="cek",
            version=1,
            type=KeyType.SYMMETRIC,
            uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=cek_material,
        )

        # Encrypt the content
        aead_ct = await self.encrypt(cek, pt, alg=_AEAD_DEFAULT, aad=aad, nonce=nonce)

        # Wrap the CEK for each recipient
        infos = []
        for r in recipients:
            wrapped = await self.wrap(r, dek=cek_material, wrap_alg=_WRAP_ALG)
            infos.append(
                RecipientInfo(
                    kid=r.kid,
                    version=r.version,
                    wrap_alg=_WRAP_ALG,
                    wrapped_key=wrapped.wrapped,
                    nonce=None,
                )
            )

        return MultiRecipientEnvelope(
            enc_alg=_AEAD_DEFAULT,
            nonce=aead_ct.nonce,
            ct=aead_ct.ct,
            tag=aead_ct.tag,
            recipients=tuple(infos),
            aad=aad,
        )

    # ---------------- utility methods ----------------
    def get_version_info(self) -> Dict[str, str]:
        """Get version information about the Rust crypto backend."""
        if not _RUST_AVAILABLE:
            return {"error": "Rust backend not available"}
        return self._rust_crypto.get_version_info()

    def generate_key(self, size: int = 32) -> bytes:
        """Generate a random key of the specified size."""
        if _RUST_AVAILABLE:
            return bytes(self._rust_crypto.generate_key(size))
        else:
            return secrets.token_bytes(size)
