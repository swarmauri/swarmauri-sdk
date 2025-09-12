"""In-memory key provider plugin storing keys solely in process memory."""

from __future__ import annotations

from typing import Dict, Iterable, Mapping, Optional, Tuple, Literal
import secrets
import hashlib
import hmac

from swarmauri_base.keys.KeyProviderBase import KeyProviderBase
from swarmauri_core.crypto.types import KeyRef, KeyType, ExportPolicy
from swarmauri_core.keys.types import KeySpec, KeyClass


class InMemoryKeyProvider(KeyProviderBase):
    """In-memory key provider for testing or ephemeral environments.

    Keys are held only in the Python process and disappear when the process
    terminates. This makes the provider suitable for CI pipelines or local
    development where persistence is undesirable.
    """

    type: Literal["InMemoryKeyProvider"] = "InMemoryKeyProvider"

    def __init__(self, **kwargs) -> None:
        """Initialize the provider.

        **kwargs (Any): Additional arguments forwarded to the base class.
        """
        super().__init__(**kwargs)
        self._store: Dict[str, Dict[int, KeyRef]] = {}

    def supports(self) -> Mapping[str, Iterable[str]]:
        """Describe supported key classes, algorithms, and features.

        RETURNS (Mapping[str, Iterable[str]]): Provider capability mapping.
        """
        return {
            "class": ("sym", "asym"),
            "algs": (),
            "features": ("create", "import", "rotate"),
        }

    async def create_key(self, spec: KeySpec) -> KeyRef:
        """Create a new key.

        spec (KeySpec): Specification for the key to create.
        RETURNS (KeyRef): Reference to the created key.
        """
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
        """Import existing key material.

        spec (KeySpec): Specification of the key to import.
        material (bytes): Secret key material.
        public (bytes): Optional public component.
        RETURNS (KeyRef): Reference to the imported key.
        """
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
        """Rotate an existing key to a new version.

        kid (str): Identifier of the key to rotate.
        spec_overrides (dict): Optional overrides for the key spec.
        RETURNS (KeyRef): Reference to the rotated key.
        RAISES (KeyError): If the key identifier is unknown.
        """
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
        """Destroy key versions.

        kid (str): Key identifier.
        version (int): Specific version to delete. Deletes all if not provided.
        RETURNS (bool): True if a key was removed.
        """
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
        """Retrieve a key version.

        kid (str): Key identifier.
        version (int): Specific version. Defaults to latest.
        include_secret (bool): When False, secret material may be omitted.
        RETURNS (KeyRef): Requested key reference.
        """
        bucket = self._store[kid]
        v = version or max(bucket)
        return bucket[v]

    async def list_versions(self, kid: str) -> Tuple[int, ...]:
        """List available versions for a key.

        kid (str): Key identifier.
        RETURNS (Tuple[int, ...]): Sorted tuple of versions.
        RAISES (KeyError): If the key identifier is unknown.
        """
        bucket = self._store.get(kid)
        if not bucket:
            raise KeyError(f"Unknown kid: {kid}")
        return tuple(sorted(bucket.keys()))

    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        """Export a public key in JWK format.

        kid (str): Key identifier.
        version (int): Specific version.
        RAISES (NotImplementedError): JWK export is not supported.
        """
        raise NotImplementedError("JWK export not supported")

    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        """Return all public keys in JWKS format.

        prefix_kids (str): Optional key ID prefix filter.
        RAISES (NotImplementedError): JWKS export is not supported.
        """
        raise NotImplementedError("JWKS export not supported")

    async def random_bytes(self, n: int) -> bytes:
        """Return cryptographically secure random bytes.

        n (int): Number of bytes to generate.
        RETURNS (bytes): Random byte string.
        """
        return secrets.token_bytes(n)

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        """Derive key material using HKDF-SHA256.

        ikm (bytes): Input keying material.
        salt (bytes): Salt value.
        info (bytes): Context-specific information.
        length (int): Desired output length in bytes.
        RETURNS (bytes): Derived key material.
        """
        prk = hmac.new(salt, ikm, hashlib.sha256).digest()
        t = b""
        okm = b""
        counter = 1
        while len(okm) < length:
            t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha256).digest()
            okm += t
            counter += 1
        return okm[:length]
