"""Paramiko-backed crypto provider with sealing support.

This module implements the ``ICrypto`` contract using AES-256-GCM for
symmetric encryption and RSA-OAEP (SHA-256) for key wrapping and direct
sealing of small payloads.

Notes:
    - RSA public keys must be supplied in OpenSSH format via ``KeyRef.public``.
    - For unwrap and unseal operations, ``KeyRef.material`` must contain a
      PEM-encoded RSA private key.
    - Sealing is limited to inputs no larger than ``modulus_bytes -
      2*hash_len - 2``. For larger payloads use
      ``encrypt_for_many(enc_alg="AES-256-GCM")``.
"""

from __future__ import annotations

import secrets
from typing import Any, Dict, Iterable, Literal, Optional
from enum import Enum

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from swarmauri_core.crypto.types import (
    AEADCiphertext,
    Alg,
    MultiRecipientEnvelope,
    RecipientInfo,
    UnsupportedAlgorithm,
    WrappedKey,
    KeyRef,
    IntegrityError,
)

from swarmauri_base.crypto.CryptoBase import CryptoBase
from swarmauri_base.ComponentBase import ComponentBase


_SEAL_ALG = "RSA-OAEP-SHA256-SEAL"
_WRAP_ALG = "RSA-OAEP-SHA256"
_AEAD_DEFAULT = "AES-256-GCM"


@ComponentBase.register_type(CryptoBase, "ParamikoCrypto")
class ParamikoCrypto(CryptoBase):
    """Crypto provider backed by Paramiko and cryptography.

    Implements AES-256-GCM for symmetric operations and RSA-OAEP for key
    wrapping and sealing.
    """

    type: Literal["ParamikoCrypto"] = "ParamikoCrypto"

    def supports(self) -> Dict[str, Iterable[Alg]]:
        """Return the algorithms supported by this provider.

        Returns:
            Dict[str, Iterable[Alg]]: Mapping of operation names to the
                algorithms the provider can execute.
        """

        return {
            "encrypt": (_AEAD_DEFAULT,),
            "decrypt": (_AEAD_DEFAULT,),
            "wrap": (_WRAP_ALG,),
            "unwrap": (_WRAP_ALG,),
            "seal": (_SEAL_ALG,),
            "unseal": (_SEAL_ALG,),
        }

    # ────────────────────────── helpers ──────────────────────────

    def _normalize_aead_alg(self, alg: Any) -> Alg:
        if isinstance(alg, Enum):
            alg = alg.value
        alg = alg or _AEAD_DEFAULT
        if alg == "AES256_GCM":
            alg = _AEAD_DEFAULT
        return alg

    @staticmethod
    def _load_rsa_pub_ssh(pub_bytes: bytes):
        return serialization.load_ssh_public_key(pub_bytes)

    @staticmethod
    def _load_rsa_priv_pem(pem_bytes: bytes):
        return serialization.load_pem_private_key(pem_bytes, password=None)

    @staticmethod
    def _seal_size_check(pubkey, pt_len: int):
        # RSA OAEP max input: k - 2*hLen - 2
        if not isinstance(pubkey, rsa.RSAPublicKey):
            raise UnsupportedAlgorithm("Sealing requires an RSA public key")
        k = (pubkey.key_size + 7) // 8
        hlen = hashes.SHA256().digest_size
        max_in = k - 2 * hlen - 2
        if pt_len > max_in:
            raise IntegrityError(
                f"Plaintext too large for {_SEAL_ALG}: {pt_len} > {max_in}. "
                f"Use encrypt_for_many(enc_alg='{_AEAD_DEFAULT}') instead."
            )

    # ────────────────────────── symmetric AEAD ──────────────────────────

    async def encrypt(
        self,
        key: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> AEADCiphertext:
        """Encrypt plaintext with AES-GCM.

        Args:
            key (KeyRef): Symmetric key reference containing the key bytes.
            pt (bytes): Plaintext to encrypt.
            alg (Optional[Alg]): AEAD algorithm to use. Defaults to
                ``AES-256-GCM`` when not provided.
            aad (Optional[bytes]): Additional authenticated data.
            nonce (Optional[bytes]): Nonce for AES-GCM. Random when omitted.

        Returns:
            AEADCiphertext: Ciphertext container with nonce and tag.

        Raises:
            UnsupportedAlgorithm: If an unsupported algorithm is requested.
            ValueError: If the key material is missing or invalid.
        """

        alg = self._normalize_aead_alg(alg)
        if alg != _AEAD_DEFAULT:
            raise UnsupportedAlgorithm(f"Unsupported AEAD algorithm: {alg}")

        if key.material is None:
            raise ValueError(
                "KeyRef.material must contain symmetric key bytes for AEAD"
            )
        if len(key.material) not in (16, 24, 32):
            raise ValueError("KeyRef.material must be 16/24/32 bytes for AES-GCM")

        nonce = nonce or secrets.token_bytes(12)
        aead = AESGCM(key.material)
        ct_with_tag = aead.encrypt(nonce, pt, aad)
        ct, tag = ct_with_tag[:-16], ct_with_tag[-16:]
        return AEADCiphertext(
            kid=key.kid,
            version=key.version,
            alg=alg,
            nonce=nonce,
            ct=ct,
            tag=tag,
            aad=aad,
        )

    async def decrypt(
        self,
        key: KeyRef,
        ct: AEADCiphertext,
        *,
        aad: Optional[bytes] = None,
    ) -> bytes:
        """Decrypt ciphertext produced by :meth:`encrypt`.

        Args:
            key (KeyRef): Symmetric key reference containing the key bytes.
            ct (AEADCiphertext): Ciphertext container to decrypt.
            aad (Optional[bytes]): Additional authenticated data. Defaults to
                the value stored in ``ct`` when omitted.

        Returns:
            bytes: Decrypted plaintext.

        Raises:
            UnsupportedAlgorithm: If an unsupported algorithm is requested.
            ValueError: If the key material is missing.
        """

        if self._normalize_aead_alg(ct.alg) != _AEAD_DEFAULT:
            raise UnsupportedAlgorithm(f"Unsupported AEAD algorithm: {ct.alg}")
        if key.material is None:
            raise ValueError(
                "KeyRef.material must contain symmetric key bytes for AEAD"
            )

        aead = AESGCM(key.material)
        blob = ct.ct + ct.tag
        return aead.decrypt(ct.nonce, blob, aad or ct.aad)

    # ─────────────────────────── sealing ───────────────────────────
    # (direct RSA-OAEP of plaintext; for small payloads only)

    async def seal(
        self,
        recipient: KeyRef,
        pt: bytes,
        *,
        alg: Optional[Alg] = _SEAL_ALG,
    ) -> bytes:
        """Seal a small plaintext to a recipient's RSA public key.

        Args:
            recipient (KeyRef): Recipient key reference with OpenSSH RSA
                public key bytes in ``KeyRef.public``.
            pt (bytes): Plaintext to encrypt.
            alg (Optional[Alg]): Sealing algorithm identifier. Defaults to
                ``RSA-OAEP-SHA256-SEAL``.

        Returns:
            bytes: Sealed ciphertext produced by RSA-OAEP.

        Raises:
            UnsupportedAlgorithm: If an unsupported algorithm is requested.
            ValueError: If the recipient public key is missing.
            IntegrityError: If the plaintext exceeds the RSA-OAEP size limit.
        """

        if alg != _SEAL_ALG:
            raise UnsupportedAlgorithm(f"Unsupported seal alg: {alg}")
        if recipient.public is None:
            raise ValueError("KeyRef.public must contain OpenSSH RSA public key bytes")

        rsa_pub = self._load_rsa_pub_ssh(recipient.public)
        self._seal_size_check(rsa_pub, len(pt))

        sealed = rsa_pub.encrypt(
            pt,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return sealed

    async def unseal(
        self,
        recipient_priv: KeyRef,
        sealed: bytes,
        *,
        alg: Optional[Alg] = _SEAL_ALG,
    ) -> bytes:
        """Unseal ciphertext using the recipient's RSA private key.

        Args:
            recipient_priv (KeyRef): Recipient key reference containing a
                PEM-encoded RSA private key in ``KeyRef.material``.
            sealed (bytes): Ciphertext produced by :meth:`seal`.
            alg (Optional[Alg]): Sealing algorithm identifier. Defaults to
                ``RSA-OAEP-SHA256-SEAL``.

        Returns:
            bytes: Decrypted plaintext.

        Raises:
            UnsupportedAlgorithm: If an unsupported algorithm is requested.
            ValueError: If the private key material is missing.
        """

        if alg != _SEAL_ALG:
            raise UnsupportedAlgorithm(f"Unsupported seal alg: {alg}")
        if recipient_priv.material is None:
            raise ValueError(
                "KeyRef.material must contain PEM-encoded RSA private key bytes"
            )

        priv = self._load_rsa_priv_pem(recipient_priv.material)
        return priv.decrypt(
            sealed,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    # ───────────── hybrid encrypt-for-many via RSA-OAEP (KEM+AEAD) ─────────────

    async def encrypt_for_many(
        self,
        recipients: Iterable[KeyRef],
        pt: bytes,
        *,
        enc_alg: Optional[Alg] = None,
        recipient_wrap_alg: Optional[Alg] = None,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ) -> MultiRecipientEnvelope:
        """Encrypt plaintext for multiple recipients.

        Operates in two modes:
        1. **Sealed**: Each recipient receives an individual RSA-OAEP sealed
           ciphertext when ``enc_alg`` is ``_SEAL_ALG``.
        2. **KEM+AEAD**: Generates a shared AES-GCM ciphertext and wraps the
           session key for each recipient using RSA-OAEP.

        Args:
            recipients (Iterable[KeyRef]): Sequence of recipients.
            pt (bytes): Plaintext to encrypt.
            enc_alg (Optional[Alg]): Encryption algorithm for the shared
                ciphertext. Defaults to ``AES-256-GCM``.
            recipient_wrap_alg (Optional[Alg]): Wrapping algorithm for the
                session key. Defaults to ``RSA-OAEP-SHA256``.
            aad (Optional[bytes]): Additional authenticated data for AES-GCM.
            nonce (Optional[bytes]): Nonce for AES-GCM. Random when omitted.

        Returns:
            MultiRecipientEnvelope: Envelope containing ciphertext and per-
                recipient wrapped keys.

        Raises:
            UnsupportedAlgorithm: If an unsupported algorithm is requested.
            ValueError: If required key material is missing.
        """

        # 1) Sealed-style variant (per-recipient ciphertext; no shared ct)
        if enc_alg == _SEAL_ALG:
            recip_infos: list[RecipientInfo] = []
            for r in recipients:
                if r.public is None:
                    raise ValueError(
                        "Recipient KeyRef.public must contain OpenSSH RSA public key bytes"
                    )
                rsa_pub = self._load_rsa_pub_ssh(r.public)
                self._seal_size_check(rsa_pub, len(pt))
                sealed = rsa_pub.encrypt(
                    pt,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                )
                recip_infos.append(
                    RecipientInfo(
                        kid=r.kid,
                        version=r.version,
                        wrap_alg=_SEAL_ALG,
                        wrapped_key=sealed,
                        nonce=None,
                    )
                )

            # Shared fields empty for sealed variant
            return MultiRecipientEnvelope(
                enc_alg=_SEAL_ALG,
                nonce=b"",
                ct=b"",
                tag=b"",
                recipients=tuple(recip_infos),
                aad=None,  # AAD is not bound in RSA-seal mode
            )

        # 2) Default KEM+AEAD path (shared AES-GCM ct + RSA-wrapped CEK)
        enc_alg = self._normalize_aead_alg(enc_alg)
        if enc_alg != _AEAD_DEFAULT:
            raise UnsupportedAlgorithm(f"Unsupported enc_alg: {enc_alg}")
        wrap_alg = recipient_wrap_alg or _WRAP_ALG
        if wrap_alg != _WRAP_ALG:
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrap_alg}")

        k = secrets.token_bytes(32)  # 256-bit session key
        iv = nonce or secrets.token_bytes(12)
        aead = AESGCM(k)
        ct_with_tag = aead.encrypt(iv, pt, aad)
        ct, tag = ct_with_tag[:-16], ct_with_tag[-16:]

        recip_infos: list[RecipientInfo] = []
        for r in recipients:
            if r.public is None:
                raise ValueError(
                    "Recipient KeyRef.public must contain OpenSSH RSA public key bytes"
                )
            rsa_pub = self._load_rsa_pub_ssh(r.public)
            enc_k = rsa_pub.encrypt(
                k,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            recip_infos.append(
                RecipientInfo(
                    kid=r.kid,
                    version=r.version,
                    wrap_alg=wrap_alg,
                    wrapped_key=enc_k,
                )
            )

        return MultiRecipientEnvelope(
            enc_alg=enc_alg,
            nonce=iv,
            ct=ct,
            tag=tag,
            recipients=tuple(recip_infos),
            aad=aad,
        )

    # ────────────────────────── raw RSA wrap/unwrap ─────────────────────

    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: Optional[bytes] = None,
        wrap_alg: Optional[Alg] = None,
        nonce: Optional[bytes] = None,
        aad: Optional[bytes] = None,
    ) -> WrappedKey:
        """Wrap a data-encryption key with the given key-encryption key.

        Args:
            kek (KeyRef): Key-encryption key reference. Provide an OpenSSH
                RSA public key in ``KeyRef.public`` for RSA-OAEP wrapping or
                symmetric key bytes in ``KeyRef.material`` for AES-GCM.
            dek (Optional[bytes]): Data-encryption key to wrap. A random key
                is generated when omitted.
            wrap_alg (Optional[Alg]): Wrapping algorithm to use. Defaults to
                ``RSA-OAEP-SHA256``.
            nonce (Optional[bytes]): Nonce for AES-GCM wrapping. Random when
                omitted.
            aad (Optional[bytes]): Additional authenticated data for AES-GCM
                wrapping.

        Returns:
            WrappedKey: Container with the wrapped key material.

        Raises:
            UnsupportedAlgorithm: If an unsupported wrapping algorithm is
                requested.
            ValueError: If required key material is missing or invalid.
        """

        wrap_alg = wrap_alg or _WRAP_ALG
        if wrap_alg == _WRAP_ALG:
            if kek.public is None:
                raise ValueError(
                    "KeyRef.public must contain OpenSSH RSA public key bytes"
                )
            rsa_pub = self._load_rsa_pub_ssh(kek.public)
            if dek is None:
                dek = secrets.token_bytes(32)
            wrapped = rsa_pub.encrypt(
                dek,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            return WrappedKey(
                kek_kid=kek.kid,
                kek_version=kek.version,
                wrap_alg=wrap_alg,
                nonce=nonce,
                wrapped=wrapped,
            )

        alg = self._normalize_aead_alg(wrap_alg)
        if alg != _AEAD_DEFAULT:
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrap_alg}")
        if kek.material is None:
            raise ValueError(
                "KeyRef.material must contain symmetric key bytes for AES-GCM wrap"
            )
        if len(kek.material) not in (16, 24, 32):
            raise ValueError("KeyRef.material must be 16/24/32 bytes for AES-GCM")
        if dek is None:
            dek = secrets.token_bytes(32)
        nonce = nonce or secrets.token_bytes(12)
        aead = AESGCM(kek.material)
        ct_with_tag = aead.encrypt(nonce, dek, aad)
        ct, tag = ct_with_tag[:-16], ct_with_tag[-16:]
        return WrappedKey(
            kek_kid=kek.kid,
            kek_version=kek.version,
            wrap_alg=wrap_alg,
            nonce=nonce,
            wrapped=ct,
            tag=tag,
        )

    async def unwrap(
        self,
        kek: KeyRef,
        wrapped: WrappedKey,
        *,
        aad: Optional[bytes] = None,
    ) -> bytes:
        """Unwrap a previously wrapped key.

        Args:
            kek (KeyRef): Key-encryption key reference. Must contain the RSA
                private key or symmetric key bytes corresponding to the
                wrapping algorithm used.
            wrapped (WrappedKey): Wrapped key to unwrap.
            aad (Optional[bytes]): Additional authenticated data for AES-GCM
                unwrapping.

        Returns:
            bytes: The unwrapped data-encryption key.

        Raises:
            UnsupportedAlgorithm: If an unsupported wrapping algorithm is
                requested.
            ValueError: If key material or required fields are missing.
        """

        if wrapped.wrap_alg == _WRAP_ALG:
            if kek.material is None:
                raise ValueError(
                    "KeyRef.material must contain PEM-encoded RSA private key bytes"
                )
            priv = self._load_rsa_priv_pem(kek.material)
            return priv.decrypt(
                wrapped.wrapped,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

        alg = self._normalize_aead_alg(wrapped.wrap_alg)
        if alg != _AEAD_DEFAULT:
            raise UnsupportedAlgorithm(f"Unsupported wrap_alg: {wrapped.wrap_alg}")
        if kek.material is None:
            raise ValueError(
                "KeyRef.material must contain symmetric key bytes for AES-GCM unwrap"
            )
        if wrapped.nonce is None:
            raise ValueError("WrappedKey.nonce required for AES-GCM unwrap")
        if wrapped.tag is None:
            raise ValueError("WrappedKey.tag required for AES-GCM unwrap")
        aead = AESGCM(kek.material)
        blob = wrapped.wrapped + wrapped.tag
        return aead.decrypt(wrapped.nonce, blob, aad)
