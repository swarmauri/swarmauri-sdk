"""
peagen.plugins.cryptography.pgp_crypto
──────────────────────────────────────
OpenPGP (GnuPG-backed) implementation of :class:`peagen.plugins.cryptography.CryptoBase`.

Highlights
----------
* Generates a **4096-bit RSA** key-pair on first use (idempotent)
* Stores ASCII-armoured keys under ``~/.peagen/keys``
* Optional pass-phrase protection for the private key
* Implements ``encrypt_for``/``decrypt`` using a hybrid RSA–OAEP + AES-256-GCM
  scheme shared with all Peagen cryptography plugins.
"""

from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Final, Iterable

import gnupg                                 # external dependency
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .crypto_base import CryptoBase, HybridEnvelope


class PGPCrypto(CryptoBase):
    """Concrete OpenPGP provider complying with the `CryptoBase` contract."""

    _PUB_FILE:  Final[str] = "pgp-public.asc"
    _PRIV_FILE: Final[str] = "pgp-private.asc"

    # ───────────────────────────── paths ──────────────────────────────

    @property
    def private_key_path(self) -> Path:  # noqa: D401
        return self.key_dir / self._PRIV_FILE

    @property
    def public_key_path(self) -> Path:  # noqa: D401
        return self.key_dir / self._PUB_FILE

    # ─────────────────── key provisioning (idempotent) ─────────────────

    def _ensure_keys(self) -> None:
        """Create a new RSA-4096 key-pair if none exist."""
        if self.private_key_path.exists() and self.public_key_path.exists():
            return

        gpg_home = self.key_dir / "gpg"
        gpg_home.mkdir(exist_ok=True, parents=True)
        os.chmod(gpg_home, 0o700)

        gpg = gnupg.GPG(gnupghome=str(gpg_home))
        key_input = gpg.gen_key_input(
            key_type="RSA",
            key_length=4096,
            name_real="Peagen-PGP",
            name_email="peagen@local",
            passphrase=self.passphrase or "",
        )
        key = gpg.gen_key(key_input)
        if not key.fingerprint:
            raise RuntimeError("GPG key generation failed")

        # export ASCII-armoured keys
        self.public_key_path.write_text(gpg.export_keys(key.fingerprint))
        self.private_key_path.write_text(
            gpg.export_keys(
                key.fingerprint,
                secret=True,
                passphrase=self.passphrase,
                expect_passphrase=bool(self.passphrase),
            )
        )
        os.chmod(self.private_key_path, 0o600)

    # ───────────────────────── fingerprints ────────────────────────────

    def fingerprint(self) -> str:
        """Return canonical OpenPGP fingerprint (grouped 4-chars)."""
        gpg = gnupg.GPG(gnupghome=str(self.key_dir / "gpg"))
        fp = gpg.list_keys()[0]["fingerprint"]
        return self.pgp_fingerprint(fp)

    # ────────────────── hybrid encrypt / decrypt API ───────────────────

    def encrypt_for(self, recipients: Iterable[str], plaintext: bytes) -> bytes:
        """
        Encrypt *plaintext* for *recipients* (fingerprints or user-IDs).

        Hybrid scheme:
        1. Generate random 256-bit session key ``k`` and 96-bit nonce ``iv``.
        2. AES-256-GCM(k) → ciphertext ``ct``.
        3. Encrypt ``k`` for **each** recipient with RSA-OAEP(SHA-256).
        4. Package into canonical :class:`HybridEnvelope` (JSON, binary-safe).
        """
        gpg = gnupg.GPG(gnupghome=str(self.key_dir / "gpg"))

        # symmetric layer
        key   = secrets.token_bytes(32)
        iv    = secrets.token_bytes(12)
        ct    = AESGCM(key).encrypt(iv, plaintext, None)

        # asymmetric wrap
        wraps: dict[str, bytes] = {}
        for r in recipients:
            enc = gpg.encrypt(key, r, armor=False, always_trust=True)
            if not enc.ok:
                raise RuntimeError(f"GPG encrypt failed: {enc.status}")
            wraps[self.pgp_fingerprint(r)] = bytes(enc.data)

        return HybridEnvelope.pack(iv, ct, wraps)

    def decrypt(self, blob: bytes) -> bytes:
        """
        Decrypt *blob* produced by :meth:`encrypt_for`.

        Raises ``RuntimeError`` on integrity or permission failures.
        """
        env = HybridEnvelope.unpack(blob)
        gpg = gnupg.GPG(gnupghome=str(self.key_dir / "gpg"))

        enc_key = env["keys"].get(self.fingerprint())
        if enc_key is None:
            raise RuntimeError("Envelope not addressed to this key")

        dec = gpg.decrypt(enc_key, passphrase=self.passphrase or "")
        if not dec.ok:
            raise RuntimeError(f"GPG decrypt failed: {dec.status}")

        return AESGCM(bytes(dec.data)).decrypt(env["iv"], env["ct"], None)

    # ──────────────────────── convenience API ─────────────────────────
    def encrypt(self, plaintext: bytes) -> bytes:          # noqa: D401
        return super().encrypt(plaintext)

    # ─────────────────────── STRING-SUGAR ALIASES ───────────────────────
    encrypt_text       = CryptoBase.encrypt_text               # type: ignore[assignment]
    encrypt_for_text   = CryptoBase.encrypt_for_text           # type: ignore[assignment]
    decrypt_text       = CryptoBase.decrypt_text               # type: ignore[assignment]