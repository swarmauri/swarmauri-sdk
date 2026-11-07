"""Base class for cryptography plugins.

Provides default NotImplementedError overrides for ICrypto methods so that
concrete providers only need to implement what they support.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from pydantic import Field
from swarmauri_core.crypto.ICrypto import ICrypto
from swarmauri_core.crypto.types import AEADCiphertext, Alg, KeyRef, WrappedKey

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class CryptoBase(ICrypto, ComponentBase):
    resource: str | None = Field(
        default=ResourceTypes.CRYPTO.value, frozen=True
    )
    type: Literal["CryptoBase"] = "CryptoBase"

    # ─────────────────────────── capabilities ───────────────────────────
    def supports(self) -> dict[str, Iterable[Alg]]:
        raise NotImplementedError("supports() must be implemented by subclass")

    # ─────────────────────────── symmetric AEAD ─────────────────────────
    async def encrypt(
        self,
        key: KeyRef,
        pt: bytes,
        *,
        alg: Alg | None = None,
        aad: bytes | None = None,
        nonce: bytes | None = None,
    ) -> AEADCiphertext:
        raise NotImplementedError("encrypt() must be implemented by subclass")

    async def decrypt(
        self,
        key: KeyRef,
        ct: AEADCiphertext,
        *,
        aad: bytes | None = None,
    ) -> bytes:
        raise NotImplementedError("decrypt() must be implemented by subclass")

    # ─────────────────────────── wrap / unwrap ──────────────────────────
    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: bytes | None = None,
        wrap_alg: Alg | None = None,
        nonce: bytes | None = None,
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
        alg: Alg | None = None,
    ) -> bytes:
        raise NotImplementedError("seal() must be implemented by subclass")

    async def unseal(
        self,
        recipient_priv: KeyRef,
        sealed: bytes,
        *,
        alg: Alg | None = None,
    ) -> bytes:
        raise NotImplementedError("unseal() must be implemented by subclass")

    # ─────────────────────────── encaps / decaps ─────────────────────────
    async def encaps(
        self,
        recipient: KeyRef,
        *,
        alg: Alg | None = None,
    ) -> tuple[bytes, bytes]:
        raise NotImplementedError("encaps() must be implemented by subclass")

    async def decaps(
        self,
        recipient_priv: KeyRef,
        encapsulated_key: bytes,
        *,
        alg: Alg | None = None,
    ) -> bytes:
        raise NotImplementedError("decaps() must be implemented by subclass")
