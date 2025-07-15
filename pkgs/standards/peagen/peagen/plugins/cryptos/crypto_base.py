from __future__ import annotations

import abc
import base64
import hashlib
import json
from pathlib import Path
from typing import Final, Iterable

# ──────────────────────────────── envelope ────────────────────────────────
class HybridEnvelope(dict):
    """
    Canonical JSON wrapper for **encrypt-for-many**.

    {
        "alg": "aes-256-gcm",
        "iv":  "<b64>",
        "ct":  "<b64>",
        "keys": { "<fingerprint>": "<b64-wrap-key>", … },
        "v":   1
    }
    """

    @classmethod
    def pack(cls, iv: bytes, ct: bytes, keys: dict[str, bytes]) -> bytes:
        return json.dumps(
            {
                "alg": "aes-256-gcm",
                "iv":  base64.b64encode(iv).decode(),
                "ct":  base64.b64encode(ct).decode(),
                "keys": {k: base64.b64encode(v).decode() for k, v in keys.items()},
                "v":   1,
            },
            separators=(",", ":"),
        ).encode()

    @classmethod
    def unpack(cls, blob: bytes):
        d = json.loads(blob)
        d["iv"]  = base64.b64decode(d["iv"])
        d["ct"]  = base64.b64decode(d["ct"])
        d["keys"] = {k: base64.b64decode(v) for k, v in d["keys"].items()}
        return d
# ───────────────────────────────── base ────────────────────────────────────
class CryptoBase(abc.ABC):
    """Common contract for *any* public-key provider (SSH, PGP, Age…)."""

    _DEFAULT_DIR: Final[Path] = Path.home() / ".peagen" / "keys"

    # ─── ctor ──────────────────────────────────────────────────────────────
    def __init__(
        self,
        key_dir: str | Path | None = None,
        *,
        passphrase: str | None = None,
    ) -> None:
        self.key_dir = Path(key_dir or self._DEFAULT_DIR)
        self.passphrase = passphrase
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_keys()  # idempotent

    # ─── must-implement ────────────────────────────────────────────────────
    @abc.abstractmethod
    def _ensure_keys(self) -> None: ...

    @property
    @abc.abstractmethod
    def private_key_path(self) -> Path: ...

    @property
    @abc.abstractmethod
    def public_key_path(self) -> Path: ...

    # new in v2 – *all* providers must support E-for-many
    @abc.abstractmethod
    def encrypt_for(self, recipients: Iterable[str], plaintext: bytes) -> bytes: ...

    @abc.abstractmethod
    def decrypt(self, ciphertext: bytes) -> bytes: ...

    # ─── helpers / façade ─────────────────────────────────────────────────
    def public_key_str(self) -> str:
        return self.public_key_path.read_text().strip()

    def private_key_bytes(self) -> bytes:
        return self.private_key_path.read_bytes()

    def export_pub(self, dest: Path | str) -> Path:
        dest = Path(dest)
        dest.write_text(self.public_key_str())
        return dest

    def list_recipients(self) -> dict[str, str]:
        """Return {fingerprint: public_key_str} — handy for “encrypt-for-many”."""
        return {self.fingerprint(): self.public_key_str()}

    # ─── fingerprint helpers ------------------------------------------------
    @staticmethod
    def ssh_fingerprint(pub_line: str) -> str:
        """
        RFC 4716 / GitHub-style:

        >>> CryptoBase.ssh_fingerprint("ssh-ed25519 AAAAC3NzaC1...")
        'SHA256:xyz…'
        """
        body = pub_line.split()[1]
        digest = hashlib.sha256(base64.b64decode(body)).digest()
        return "SHA256:" + base64.b64encode(digest).decode().rstrip("=")

    @staticmethod
    def pgp_fingerprint(hex_str: str) -> str:
        """Normalise OpenPGP fingerprint to upper-case & 4-char blocks."""
        h = hex_str.replace(" ", "").upper()
        return " ".join(h[i:i+4] for i in range(0, len(h), 4))

    @abc.abstractmethod
    def fingerprint(self) -> str: ...

    # ─── single-recipient convenience ──────────────────────────────────
    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypt *plaintext* so that **only this key-pair** can decrypt it.

        Implemented once in the base class as a thin wrapper around
        :meth:`encrypt_for`; concrete subclasses inherit the behaviour
        unchanged.
        """
        return self.encrypt_for([self.public_key_str()], plaintext)

    # ──────────────────── STRING-SUGAR HELPERS ──────────────────────────
    def encrypt_text(self, text: str, *, encoding: str = "utf-8") -> bytes:
        """
        Convenience wrapper: encode *text* (UTF-8 by default) and call
        :meth:`encrypt`.
        """
        return self.encrypt(text.encode(encoding))

    def encrypt_for_text(
        self,
        recipients: Iterable[str],
        text: str,
        *,
        encoding: str = "utf-8",
    ) -> bytes:
        """
        Multi-recipient string encryption.  Equivalent to::

            crypto.encrypt_for(recipients, text.encode("utf-8"))
        """
        return self.encrypt_for(recipients, text.encode(encoding))

    def decrypt_text(self, ciphertext: bytes, *, encoding: str = "utf-8") -> str:
        """
        Decrypt *ciphertext* and return a Unicode string (UTF-8 default).
        """
        return self.decrypt(ciphertext).decode(encoding)