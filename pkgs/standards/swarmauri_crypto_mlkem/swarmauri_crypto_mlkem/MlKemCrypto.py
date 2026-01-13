"""ML-KEM based crypto provider."""

from __future__ import annotations

import base64
import binascii
import json
from typing import Dict, Iterable, Literal, Optional

from pqcrypto.kem import kyber768

from swarmauri_core.crypto.types import (
    Alg,
    IntegrityError,
    KeyRef,
    KeyType,
    KeyUse,
    PermissionDenied,
    UnsupportedAlgorithm,
    WrappedKey,
)
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.crypto.CryptoBase import CryptoBase

_MLKEM_ALG = "ML-KEM-768"
_SHARED_SECRET_SIZE = 32


def _type_value(t: object) -> str:
    return t.value if hasattr(t, "value") else str(t)


def _ensure_mlkem_key(key: KeyRef) -> None:
    if _type_value(key.type) != KeyType.MLKEM.value:
        raise ValueError("KeyRef.type must be KeyType.MLKEM for ML-KEM operations")


def _ensure_use(key: KeyRef, expected: KeyUse) -> None:
    uses = {_type_value(use) for use in key.uses}
    if expected.value not in uses:
        raise PermissionDenied(
            f"KeyRef.uses must include {expected.value!r} for ML-KEM operations"
        )


def _coerce_bytes(value: bytes | str | None, *, field: str) -> bytes:
    if value is None:
        raise ValueError(f"{field} must contain ML-KEM key material")
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        try:
            return base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError):
            return value.encode("utf-8")
    raise TypeError(f"{field} must be bytes or str")


def _serialize_wrapped(ciphertext: bytes, shared_secret: bytes) -> bytes:
    payload = {
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        "shared_secret": base64.b64encode(shared_secret).decode("ascii"),
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _deserialize_wrapped(blob: bytes) -> tuple[bytes, bytes]:
    try:
        decoded = blob.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IntegrityError("WrappedKey payload must be UTF-8 text") from exc
    try:
        payload = json.loads(decoded)
    except json.JSONDecodeError as exc:
        raise IntegrityError("WrappedKey payload is not valid JSON") from exc
    try:
        ct_b64 = payload["ciphertext"]
        ss_b64 = payload["shared_secret"]
    except KeyError as exc:
        raise IntegrityError("WrappedKey payload missing ML-KEM fields") from exc
    try:
        ct = base64.b64decode(ct_b64, validate=True)
        ss = base64.b64decode(ss_b64, validate=True)
    except (binascii.Error, TypeError, ValueError) as exc:
        raise IntegrityError("WrappedKey payload contains invalid base64 data") from exc
    return ct, ss


@ComponentBase.register_type(CryptoBase, "MlKemCrypto")
class MlKemCrypto(CryptoBase):
    """Crypto provider backed by ML-KEM (Kyber-768)."""

    type: Literal["MlKemCrypto"] = "MlKemCrypto"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._last_shared_secret: Optional[bytes] = None

    def supports(self) -> Dict[str, Iterable[Alg]]:
        return {
            "wrap": (_MLKEM_ALG,),
            "unwrap": (_MLKEM_ALG,),
            "seal": (_MLKEM_ALG,),
            "unseal": (_MLKEM_ALG,),
        }

    async def seal(
        self, recipient: KeyRef, pt: bytes, *, alg: Optional[Alg] = None
    ) -> bytes:
        del pt  # plaintext is unused for pure KEM operations
        alg = alg or _MLKEM_ALG
        if alg != _MLKEM_ALG:
            raise UnsupportedAlgorithm(f"Unsupported ML-KEM seal algorithm: {alg}")
        _ensure_mlkem_key(recipient)
        _ensure_use(recipient, KeyUse.WRAP)
        public_key = _coerce_bytes(recipient.public, field="KeyRef.public")
        ciphertext, shared_secret = kyber768.encrypt(public_key)
        if len(shared_secret) != _SHARED_SECRET_SIZE:
            raise IntegrityError("ML-KEM shared secret has unexpected length")
        self._last_shared_secret = shared_secret
        return ciphertext

    async def unseal(
        self, recipient_priv: KeyRef, sealed: bytes, *, alg: Optional[Alg] = None
    ) -> bytes:
        alg = alg or _MLKEM_ALG
        if alg != _MLKEM_ALG:
            raise UnsupportedAlgorithm(f"Unsupported ML-KEM seal algorithm: {alg}")
        _ensure_mlkem_key(recipient_priv)
        _ensure_use(recipient_priv, KeyUse.UNWRAP)
        private_key = _coerce_bytes(recipient_priv.material, field="KeyRef.material")
        shared_secret = kyber768.decrypt(private_key, sealed)
        if len(shared_secret) != _SHARED_SECRET_SIZE:
            raise IntegrityError("ML-KEM shared secret has unexpected length")
        return shared_secret

    async def wrap(
        self,
        kek: KeyRef,
        *,
        dek: Optional[bytes] = None,
        wrap_alg: Optional[Alg] = None,
        nonce: Optional[bytes] = None,
    ) -> WrappedKey:
        del nonce
        alg = wrap_alg or _MLKEM_ALG
        if alg != _MLKEM_ALG:
            raise UnsupportedAlgorithm(f"Unsupported ML-KEM wrap algorithm: {alg}")
        if dek is not None:
            raise ValueError("ML-KEM wrap generates secrets; provide dek=None")
        _ensure_mlkem_key(kek)
        _ensure_use(kek, KeyUse.WRAP)
        public_key = _coerce_bytes(kek.public, field="KeyRef.public")
        ciphertext, shared_secret = kyber768.encrypt(public_key)
        if len(shared_secret) != _SHARED_SECRET_SIZE:
            raise IntegrityError("ML-KEM shared secret has unexpected length")
        payload = _serialize_wrapped(ciphertext, shared_secret)
        return WrappedKey(
            kek_kid=kek.kid,
            kek_version=kek.version,
            wrap_alg=alg,
            wrapped=payload,
        )

    async def unwrap(self, kek: KeyRef, wrapped: WrappedKey) -> bytes:
        if wrapped.wrap_alg != _MLKEM_ALG:
            raise UnsupportedAlgorithm(
                f"Unsupported ML-KEM wrap algorithm: {wrapped.wrap_alg}"
            )
        _ensure_mlkem_key(kek)
        _ensure_use(kek, KeyUse.UNWRAP)
        private_key = _coerce_bytes(kek.material, field="KeyRef.material")
        ciphertext, expected_secret = _deserialize_wrapped(wrapped.wrapped)
        shared_secret = kyber768.decrypt(private_key, ciphertext)
        if len(shared_secret) != _SHARED_SECRET_SIZE:
            raise IntegrityError("ML-KEM shared secret has unexpected length")
        if shared_secret != expected_secret:
            raise IntegrityError("Recovered shared secret does not match payload")
        return shared_secret

    @property
    def last_shared_secret(self) -> Optional[bytes]:
        """Last shared secret produced by :meth:`seal`."""

        return self._last_shared_secret
