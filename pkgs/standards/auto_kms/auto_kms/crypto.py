from __future__ import annotations

from typing import Optional

from swarmauri_core.crypto.types import AEADCiphertext
from swarmauri_base.crypto.CryptoBase import CryptoBase
from swarmauri_base.secrets.SecretDriveBase import SecretDriveBase


class ParamikoCryptoAdapter:
    """Adapter exposing a simple kid-based API on top of a ``CryptoBase`` provider.

    The KMS expects providers to implement ``encrypt``/``decrypt`` methods that
    accept a ``kid`` and raw bytes.  ``ParamikoCrypto`` operates on ``KeyRef``
    and ``AEADCiphertext`` objects instead.  This adapter bridges the two
    interfaces so that ``ParamikoCrypto`` can be used by the service.
    """

    def __init__(self, *, secrets: SecretDriveBase, crypto: CryptoBase):
        self._secrets = secrets
        self._crypto = crypto

    async def encrypt(
        self,
        *,
        kid: str,
        plaintext: bytes,
        alg,
        aad: Optional[bytes] = None,
        nonce: Optional[bytes] = None,
    ):
        key = await self._secrets.load_key(kid=kid, require_private=True)
        return await self._crypto.encrypt(key, plaintext, alg=alg, aad=aad, nonce=nonce)

    async def decrypt(
        self,
        *,
        kid: str,
        ciphertext: bytes,
        nonce: bytes,
        tag: Optional[bytes] = None,
        aad: Optional[bytes] = None,
        alg: Optional[str] = None,
    ) -> bytes:
        key = await self._secrets.load_key(kid=kid, require_private=True)
        ct = AEADCiphertext(
            kid=kid,
            version=key.version,
            alg=alg or "AES-256-GCM",
            nonce=nonce,
            ct=ciphertext,
            tag=tag,
            aad=aad,
        )
        return await self._crypto.decrypt(key, ct, aad=aad)
