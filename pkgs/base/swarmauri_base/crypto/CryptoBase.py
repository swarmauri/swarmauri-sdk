"""Base class for cryptography plugins.

Provides default NotImplementedError overrides for ICrypto methods so that
concrete providers only need to implement what they support.
"""

from __future__ import annotations

from typing import Dict, Iterable, Literal, Optional

from pydantic import Field

from swarmauri_core.crypto.ICrypto import ICrypto
from swarmauri_core.crypto.types import AEADCiphertext, Alg, KeyRef, WrappedKey
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class CryptoBase(ICrypto, ComponentBase):
    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: Literal["CryptoBase"] = "CryptoBase"

    # ─────────────────────────── capabilities ───────────────────────────
    def supports(self) -> Dict[str, Iterable[Alg]]:
        raise NotImplementedError("supports() must be implemented by subclass")

    # ─────────────────────────── symmetric AEAD ─────────────────────────
    async def encrypt(
        self,
        key: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> AEADCiphertext:
        raise NotImplementedError("encrypt() must be implemented by subclass")

    async def decrypt(
        self,
        key: KeyRef,
        ct: AEADCiphertext,
        *,
        aad: Optional[bytes] = None,
    ) -> bytes:
        raise NotImplementedError("decrypt() must be implemented by subclass")

    # ─────────────────────────── wrap / unwrap ──────────────────────────
    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: Optional[bytes] = None,
        wrap_alg: Optional[Alg] = None,
        nonce: Optional[bytes] = None,
        aad: Optional[bytes] = None,
    ) -> WrappedKey:
        raise NotImplementedError("wrap() must be implemented by subclass")

    async def unwrap(self, kek: KeyRef, wrapped: WrappedKey) -> bytes:
        raise NotImplementedError("unwrap() must be implemented by subclass")

    # ─────────────────────────── seal / unseal ──────────────────────────
    async def seal(
        self,
        recipient: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
    ) -> bytes:
        raise NotImplementedError("seal() must be implemented by subclass")

    async def unseal(
        self,
        recipient_priv: KeyRef,
        sealed: bytes,
        *,
        alg: Optional[Alg] = None,
    ) -> bytes:
        raise NotImplementedError("unseal() must be implemented by subclass")
