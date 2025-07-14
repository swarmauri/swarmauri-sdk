"""
peagen.plugins.cryptography.paramiko_crypto
────────────────────────────────────────────
SSH-RSA public-key provider that complies **exactly** with
:class:`peagen.plugins.cryptography.CryptoBase`.

* Generates a 4096-bit RSA key-pair on first use (idempotent)
* Stores keys under ``~/.peagen/keys`` (or caller-supplied path)
* Implements hybrid **encrypt-for-many** via RSA-OAEP + AES-256-GCM
* Fingerprint format: RFC 4716 / GitHub-style ``SHA256:…``

External deps
-------------
    ▸ paramiko ≥ 3.4           (key-gen, OpenSSH serialisation)  
    ▸ cryptography             (RSA-OAEP, AES-GCM primitives)
"""

from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Final, Iterable

import paramiko
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .crypto_base import CryptoBase, HybridEnvelope


class ParamikoCrypto(CryptoBase):
    """Concrete SSH-RSA implementation of the :class:`CryptoBase` contract."""

    _PUB_FILE:  Final[str] = "ssh-public"
    _PRIV_FILE: Final[str] = "ssh-private"

    # ────────────────────────── key paths ──────────────────────────────

    @property
    def private_key_path(self) -> Path:  # noqa: D401
        return self.key_dir / self._PRIV_FILE

    @property
    def public_key_path(self) -> Path:  # noqa: D401
        return self.key_dir / self._PUB_FILE

    # ───────────────────── key provisioning (idempotent) ───────────────

    def _ensure_keys(self) -> None:
        """Generate RSA-4096 key-pair iff absent."""
        if self.private_key_path.exists() and self.public_key_path.exists():
            return

        key = paramiko.RSAKey.generate(4096)

        # private − PEM (encrypted when passphrase supplied)
        key.write_private_key_file(
            str(self.private_key_path),
            password=self.passphrase,
        )
        os.chmod(self.private_key_path, 0o600)

        # public − single-line OpenSSH format
        self.public_key_path.write_text(f"{key.get_name()} {key.get_base64()}\n")

    # ────────────────────────── fingerprint ────────────────────────────

    def fingerprint(self) -> str:
        """RFC 4716 / SHA-256 fingerprint of the **public** key."""
        return self.ssh_fingerprint(self.public_key_str())

    # ────────────────── hybrid encrypt / decrypt API ───────────────────

    def encrypt_for(self, recipients: Iterable[str], plaintext: bytes) -> bytes:
        """
        Encrypt *plaintext* for **all** *recipients* (OpenSSH public-key lines).

        Hybrid scheme:
        1. Random 256-bit session key ``k`` + 96-bit nonce ``iv``.
        2. AES-256-GCM(k) → ciphertext ``ct``.
        3. RSA-OAEP(SHA-256) encrypt ``k`` for *each* recipient.
        4. Pack everything via :class:`HybridEnvelope`.
        """
        # symmetric layer
        k  = secrets.token_bytes(32)   # AES-256
        iv = secrets.token_bytes(12)   # GCM standard nonce
        ct = AESGCM(k).encrypt(iv, plaintext, None)

        # asymmetric wrap
        wraps: dict[str, bytes] = {}
        for pub_line in recipients:
            rsa_pub = serialization.load_ssh_public_key(pub_line.encode())
            enc_k = rsa_pub.encrypt(
                k,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            wraps[self.ssh_fingerprint(pub_line)] = enc_k

        return HybridEnvelope.pack(iv, ct, wraps)

    def decrypt(self, blob: bytes) -> bytes:
        """
        Decrypt *blob* produced by :meth:`encrypt_for`.

        Raises ``RuntimeError`` when the envelope is not addressed
        to this key or integrity/authentication fails.
        """
        env = HybridEnvelope.unpack(blob)
        enc_k = env["keys"].get(self.fingerprint())
        if enc_k is None:
            raise RuntimeError("Envelope not addressed to this key")

        # load private key
        priv = serialization.load_pem_private_key(
            self.private_key_bytes(),
            password=self.passphrase.encode() if self.passphrase else None,
        )
        k = priv.decrypt(
            enc_k,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        return AESGCM(k).decrypt(env["iv"], env["ct"], None)


    # ──────────────────────── convenience API ─────────────────────────
    # Delegates to the default implementation in CryptoBase; explicit
    # override keeps IDEs happy and documents parity with PGPCrypto.
    def encrypt(self, plaintext: bytes) -> bytes:          # noqa: D401
        return super().encrypt(plaintext)


    # ─────────────────────── STRING-SUGAR ALIASES ───────────────────────
    encrypt_text       = CryptoBase.encrypt_text               # type: ignore[assignment]
    encrypt_for_text   = CryptoBase.encrypt_for_text           # type: ignore[assignment]
    decrypt_text       = CryptoBase.decrypt_text               # type: ignore[assignment]
