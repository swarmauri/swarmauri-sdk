from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable


class SecretDriverBase(ABC):
    """Abstract secret driver."""

    @abstractmethod
    def encrypt(self, plaintext: bytes, recipients: Iterable[str]) -> bytes:
        """Encrypt ``plaintext`` for ``recipients``."""

    @abstractmethod
    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt ``ciphertext`` and verify signature."""

    @staticmethod
    @abstractmethod
    def decrypt_and_verify(
        ciphertext: bytes,
        priv_key: str | Path,
        user_pub: str | Path,
        passphrase: str | None = None,
    ) -> bytes:
        """Decrypt ``ciphertext`` with ``priv_key`` and verify ``user_pub``."""

    @staticmethod
    def audit_hash(ciphertext: bytes) -> str:
        """Return SHA-256 hash of ``ciphertext``."""
        return hashlib.sha256(ciphertext).hexdigest()
