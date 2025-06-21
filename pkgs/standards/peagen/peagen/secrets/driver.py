from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

import pgpy
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)


class SecretDriverBase(ABC):
    """Abstract secret driver."""

    @abstractmethod
    def encrypt(self, plaintext: bytes, recipients: Iterable[str]) -> bytes:
        """Encrypt ``plaintext`` for ``recipients``."""

    @abstractmethod
    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt ``ciphertext`` and verify signature."""

    @staticmethod
    def audit_hash(ciphertext: bytes) -> str:
        """Return SHA-256 hash of ``ciphertext``."""
        return hashlib.sha256(ciphertext).hexdigest()


class AutoGpgDriver(SecretDriverBase):
    """Pure-Python PGP helper using :mod:`pgpy`."""

    def __init__(
        self, key_dir: str | Path | None = None, passphrase: str | None = None
    ) -> None:
        self.key_dir = Path(key_dir or Path.home() / ".peagen" / "keys")
        self.passphrase = passphrase
        self.priv_path = self.key_dir / "private.asc"
        self.pub_path = self.key_dir / "public.asc"
        self._ensure_keys()

    # ─── Key Management ──────────────────────────────────────────────────
    def _ensure_keys(self) -> None:
        self.key_dir.mkdir(parents=True, exist_ok=True)
        if self.priv_path.exists() and self.pub_path.exists():
            self.private = pgpy.PGPKey()
            self.private.parse(self.priv_path.read_text())
            if self.passphrase:
                self.private.unlock(self.passphrase)
            self.public = pgpy.PGPKey()
            self.public.parse(self.pub_path.read_text())
            return

        key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
        uid = pgpy.PGPUID.new("peagen-user")
        key.add_uid(
            uid,
            usage={KeyFlags.Sign, KeyFlags.EncryptCommunications},
            hashes=[HashAlgorithm.SHA256],
            ciphers=[SymmetricKeyAlgorithm.AES256],
            compression=[CompressionAlgorithm.ZLIB],
        )
        if self.passphrase:
            key.protect(
                self.passphrase, SymmetricKeyAlgorithm.AES256, HashAlgorithm.SHA256
            )
        self.private = key
        self.public = key.pubkey
        self.priv_path.write_text(str(self.private))
        self.pub_path.write_text(str(self.public))

    # ─── SecretDriverBase Overrides ──────────────────────────────────────
    def encrypt(self, plaintext: bytes, recipients: Iterable[str]) -> bytes:
        msg = pgpy.PGPMessage.new(plaintext)
        msg |= self.private.sign(msg)
        keys = [self.public]
        for r in recipients:
            k = pgpy.PGPKey()
            p = Path(r)
            if p.exists():
                k.parse(p.read_text())
            else:
                k.parse(r)
            keys.append(k)
        sessionkey = SymmetricKeyAlgorithm.AES256.gen_key()
        enc_msg = msg
        for k in keys:
            enc_msg = k.encrypt(
                enc_msg, cipher=SymmetricKeyAlgorithm.AES256, sessionkey=sessionkey
            )
        return bytes(str(enc_msg), "utf-8")

    def decrypt(self, ciphertext: bytes) -> bytes:
        enc_msg = pgpy.PGPMessage.from_blob(ciphertext)
        with self.private.unlock(self.passphrase or ""):
            decrypted = self.private.decrypt(enc_msg)
        if not decrypted:
            raise ValueError("decryption failed")
        try:
            verified = self.public.verify(decrypted)
            if not verified:
                raise ValueError
        except Exception:
            pass
        return decrypted.message.encode()
