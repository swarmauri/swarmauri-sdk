from __future__ import annotations

from typing import Dict, Iterable, Mapping, Optional, Tuple, Literal
import secrets
import hashlib
import hmac

from swarmauri_base.key_providers.KeyProviderBase import KeyProviderBase
from swarmauri_core.crypto.types import KeyRef, KeyType, ExportPolicy
from swarmauri_core.key_providers.types import KeySpec, KeyClass


class InMemoryKeyProvider(KeyProviderBase):
    """Simple in-memory key provider for testing or ephemeral usage."""

    type: Literal["InMemoryKeyProvider"] = "InMemoryKeyProvider"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._store: Dict[str, Dict[int, KeyRef]] = {}

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "class": ("sym", "asym"),
            "algs": (),
            "features": ("create", "import", "rotate"),
        }

    async def create_key(self, spec: KeySpec) -> KeyRef:
        kid = secrets.token_hex(8)
        version = 1
        material = secrets.token_bytes(32)
        ref = KeyRef(
            kid=kid,
            version=version,
            type=(
                KeyType.SYMMETRIC
                if spec.klass == KeyClass.symmetric
                else KeyType.OPAQUE
            ),
            uses=tuple(spec.uses),
            export_policy=spec.export_policy,
            material=(material if spec.export_policy != ExportPolicy.NONE else None),
            tags={"label": spec.label or "", **(spec.tags or {})},
        )
        self._store.setdefault(kid, {})[version] = ref
        return ref

    async def import_key(
        self,
        spec: KeySpec,
        material: bytes,
        *,
        public: Optional[bytes] = None,
    ) -> KeyRef:
        kid = secrets.token_hex(8)
        version = 1
        ref = KeyRef(
            kid=kid,
            version=version,
            type=(
                KeyType.SYMMETRIC
                if spec.klass == KeyClass.symmetric
                else KeyType.OPAQUE
            ),
            uses=tuple(spec.uses),
            export_policy=spec.export_policy,
            material=(material if spec.export_policy != ExportPolicy.NONE else None),
            public=public,
            tags={"label": spec.label or "", **(spec.tags or {})},
        )
        self._store.setdefault(kid, {})[version] = ref
        return ref

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ) -> KeyRef:
        bucket = self._store.get(kid)
        if not bucket:
            raise KeyError(f"Unknown kid: {kid}")
        latest = max(bucket)
        base = bucket[latest]
        material = secrets.token_bytes(len(base.material or b"\x00" * 32))
        version = latest + 1
        ref = KeyRef(
            kid=kid,
            version=version,
            type=base.type,
            uses=base.uses,
            export_policy=base.export_policy,
            material=(material if base.export_policy != ExportPolicy.NONE else None),
            public=base.public,
            tags=base.tags,
            uri=base.uri,
        )
        bucket[version] = ref
        return ref

    async def destroy_key(self, kid: str, version: Optional[int] = None) -> bool:
        bucket = self._store.get(kid)
        if not bucket:
            return False
        if version is None:
            del self._store[kid]
            return True
        bucket.pop(version, None)
        if not bucket:
            del self._store[kid]
        return True

    async def get_key(
        self,
        kid: str,
        version: Optional[int] = None,
        *,
        include_secret: bool = False,
    ) -> KeyRef:
        bucket = self._store[kid]
        v = version or max(bucket)
        return bucket[v]

    async def list_versions(self, kid: str) -> Tuple[int, ...]:
        bucket = self._store.get(kid)
        if not bucket:
            raise KeyError(f"Unknown kid: {kid}")
        return tuple(sorted(bucket.keys()))

    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        raise NotImplementedError("JWK export not supported")

    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        raise NotImplementedError("JWKS export not supported")

    async def random_bytes(self, n: int) -> bytes:
        return secrets.token_bytes(n)

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        """Derive key material using HKDF-SHA256."""
        prk = hmac.new(salt, ikm, hashlib.sha256).digest()
        t = b""
        okm = b""
        counter = 1
        while len(okm) < length:
            t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
            okm += t
            counter += 1
        return okm[:length]
