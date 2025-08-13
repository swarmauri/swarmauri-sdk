"""Interface for cryptography plugins."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional

from .types import (
    AEADCiphertext,
    Alg,
    KeyRef,
    MultiRecipientEnvelope,
    Signature,
    WrappedKey,
)


class ICrypto(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def supports(self) -> Dict[str, Iterable[Alg]]: ...

    @abstractmethod
    async def encrypt(
        self,
        key: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> AEADCiphertext: ...

    @abstractmethod
    async def decrypt(
        self,
        key: KeyRef,
        ct: AEADCiphertext,
        *,
        aad: Optional[bytes] = None,
    ) -> bytes: ...

    @abstractmethod
    async def sign(
        self,
        key: KeyRef,
        msg: bytes,
        *,
        alg: Optional[Alg] = None,
    ) -> Signature: ...

    @abstractmethod
    async def verify(
        self,
        key: KeyRef,
        msg: bytes,
        sig: Signature,
    ) -> bool: ...

    @abstractmethod
    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: Optional[bytes] = None,
        wrap_alg: Optional[Alg] = None,
        nonce: Optional[bytes] = None,
    ) -> WrappedKey: ...

    @abstractmethod
    async def unwrap(self, kek: KeyRef, wrapped: WrappedKey) -> bytes: ...

    @abstractmethod
    async def encrypt_for_many(
        self,
        recipients: Iterable[KeyRef],
        pt: bytes,
        *,
        enc_alg: Optional[Alg] = None,
        recipient_wrap_alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> MultiRecipientEnvelope: ...
