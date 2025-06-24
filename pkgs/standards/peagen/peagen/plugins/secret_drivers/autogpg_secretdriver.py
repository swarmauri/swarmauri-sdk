from __future__ import annotations

from pathlib import Path
from typing import Iterable
import subprocess
import tempfile
import warnings

from cryptography.utils import CryptographyDeprecationWarning
import pgpy
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)
from .base import SecretDriverBase

warnings.filterwarnings(
    "ignore", category=CryptographyDeprecationWarning, module="pgpy.constants"
)


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
        msg = pgpy.PGPMessage.new(plaintext, compression=CompressionAlgorithm.ZLIB)
        sig = self.private.sign(msg)
        msg |= sig
        keys = [self.public]
        for r in recipients:
            k = pgpy.PGPKey()
            try:
                p = Path(r)
                if p.exists():
                    k.parse(p.read_text())
                else:
                    raise OSError
            except OSError:
                k.parse(str(r))
            keys.append(k)
        sessionkey = SymmetricKeyAlgorithm.AES256.gen_key()
        enc_msg = msg
        for k in keys:
            enc_msg = k.encrypt(
                enc_msg,
                cipher=SymmetricKeyAlgorithm.AES256,
                compression=CompressionAlgorithm.ZLIB,
                sessionkey=sessionkey,
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

    # ------------------------------------------------------------------
    @staticmethod
    def decrypt_and_verify(
        ciphertext: bytes,
        priv_key: str | Path,
        user_pub: str | Path,
        passphrase: str | None = None,
    ) -> bytes:
        """Decrypt ``ciphertext`` with ``priv_key`` and verify ``user_pub``."""
        priv = pgpy.PGPKey()
        p = Path(priv_key)
        if isinstance(priv_key, Path) or p.exists():
            priv.parse(p.read_text())
        else:
            priv.parse(str(priv_key))

        if passphrase:
            priv.unlock(passphrase)

        pub = pgpy.PGPKey()
        up = Path(user_pub)
        if isinstance(user_pub, Path) or up.exists():
            pub.parse(up.read_text())
        else:
            pub.parse(str(user_pub))

        message = pgpy.PGPMessage.from_blob(ciphertext)
        decrypted = priv.decrypt(message)
        if not decrypted:
            raise ValueError("decryption failed")
        if not pub.verify(decrypted):
            raise ValueError("signature verification failed")
        return decrypted.message.encode()

    # ─── Convenience helpers used by keys_core ──────────────────────────

    def create_keypair(self) -> dict:
        """Ensure keys exist and return their paths."""
        self._ensure_keys()
        return {"private": str(self.priv_path), "public": str(self.pub_path)}

    def list_keys(self) -> dict[str, str]:
        """List fingerprints for public keys under ``key_dir``."""
        keys: dict[str, str] = {}

        def _add(pub: Path) -> None:
            if not pub.exists():
                return
            key = pgpy.PGPKey()
            key.parse(pub.read_text())
            keys[key.fingerprint] = str(pub)

        if (self.key_dir / "public.asc").exists():
            _add(self.key_dir / "public.asc")
        else:
            for sub in self.key_dir.iterdir():
                if not sub.is_dir():
                    continue
                _add(sub / "public.asc")

        return keys

    def export_public_key(self, fingerprint: str, fmt: str = "armor") -> str:
        """Return ``fingerprint`` key in ``fmt`` format."""
        keys = self.list_keys()
        pub_path_str = keys.get(fingerprint)
        if not pub_path_str:
            raise ValueError(f"unknown key: {fingerprint}")

        pub_path = Path(pub_path_str)
        if fmt == "openssh":
            with tempfile.TemporaryDirectory() as gpg_home:
                subprocess.run(
                    ["gpg", "--homedir", gpg_home, "--import", str(pub_path)],
                    check=True,
                    capture_output=True,
                )
                out = subprocess.run(
                    ["gpg", "--homedir", gpg_home, "--export-ssh-key", fingerprint],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            return out
        return pub_path.read_text()

    def add_key(
        self,
        public_key: Path,
        *,
        private_key: Path | None = None,
        name: str | None = None,
    ) -> dict:
        """Store ``public_key`` (and optional ``private_key``) under ``key_dir``."""
        text = Path(public_key).read_text()
        key = pgpy.PGPKey()
        key.parse(text)
        fingerprint = key.fingerprint

        if (self.key_dir / "public.asc").exists() and not name:
            dest = self.key_dir
        else:
            dest = self.key_dir / (name or fingerprint)
            dest.mkdir(parents=True, exist_ok=True)

        (dest / "public.asc").write_text(text)
        if private_key is not None:
            (dest / "private.asc").write_text(Path(private_key).read_text())

        return {"fingerprint": fingerprint, "path": str(dest)}
