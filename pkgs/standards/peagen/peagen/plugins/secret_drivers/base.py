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

    # ------------------------------------------------------------------
    # Key management helpers
    def list_keys(self) -> dict[str, str]:
        """List available public keys."""
        from .autogpg_secretdriver import AutoGpgDriver

        drv = AutoGpgDriver()
        if hasattr(self, "key_dir"):
            drv.key_dir = Path(getattr(self, "key_dir"))
            drv.priv_path = drv.key_dir / "private.asc"
            drv.pub_path = drv.key_dir / "public.asc"
        if hasattr(self, "passphrase"):
            drv.passphrase = getattr(self, "passphrase")
        if hasattr(drv, "_ensure_keys"):
            drv._ensure_keys()
        return drv.list_keys()

    def export_public_key(self, fingerprint: str, fmt: str = "armor") -> str:
        """Return ``fingerprint`` key in ``fmt`` format."""
        from .autogpg_secretdriver import AutoGpgDriver

        drv = AutoGpgDriver()
        if hasattr(self, "key_dir"):
            drv.key_dir = Path(getattr(self, "key_dir"))
            drv.priv_path = drv.key_dir / "private.asc"
            drv.pub_path = drv.key_dir / "public.asc"
        if hasattr(self, "passphrase"):
            drv.passphrase = getattr(self, "passphrase")
        if hasattr(drv, "_ensure_keys"):
            drv._ensure_keys()
        return drv.export_public_key(fingerprint, fmt)

    def add_key(
        self,
        public_key: Path,
        *,
        private_key: Path | None = None,
        name: str | None = None,
    ) -> dict:
        """Store ``public_key`` (and optional ``private_key``) under ``key_dir``."""

        from .autogpg_secretdriver import AutoGpgDriver

        drv = AutoGpgDriver()
        if hasattr(self, "key_dir"):
            drv.key_dir = Path(getattr(self, "key_dir"))
            drv.priv_path = drv.key_dir / "private.asc"
            drv.pub_path = drv.key_dir / "public.asc"
        if hasattr(self, "passphrase"):
            drv.passphrase = getattr(self, "passphrase")
        if hasattr(drv, "_ensure_keys"):
            drv._ensure_keys()
        return drv.add_key(public_key, private_key=private_key, name=name)
