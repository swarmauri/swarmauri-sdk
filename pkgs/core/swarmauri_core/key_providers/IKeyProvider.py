from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Iterable, Mapping, Optional, Tuple

from ..crypto.types import KeyRef
from .types import KeySpec


class IKeyProvider(ABC):
    """Stable, minimal surface for key lifecycle and randomness/KDF utilities.

    Implementations MUST populate the ``fingerprint`` attribute on returned
    :class:`~swarmauri_core.crypto.types.KeyRef` instances. The fingerprint is a
    provider-defined stable identifier derived from the key's material or public
    representation.
    """

    @abstractmethod
    def supports(self) -> Mapping[str, Iterable[str]]:
        """Return capability map for this provider."""

    @abstractmethod
    async def create_key(self, spec: KeySpec) -> KeyRef:
        """Generate a new key and return a :class:`KeyRef`."""

    @abstractmethod
    async def import_key(
        self,
        spec: KeySpec,
        material: bytes,
        *,
        public: Optional[bytes] = None,
    ) -> KeyRef:
        """Import an existing key and return its :class:`KeyRef`."""

    @abstractmethod
    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ) -> KeyRef:
        """Create a new version for an existing key."""

    @abstractmethod
    async def destroy_key(self, kid: str, version: Optional[int] = None) -> bool:
        """Destroy a key or specific version."""

    @abstractmethod
    async def get_key(
        self,
        kid: str,
        version: Optional[int] = None,
        *,
        include_secret: bool = False,
    ) -> KeyRef:
        """Fetch a :class:`KeyRef` for the given key id/version."""

    async def get_key_by_ref(
        self,
        key_ref: str,
        *,
        include_secret: bool = False,
    ) -> KeyRef:
        """Resolve an opaque key reference into a :class:`KeyRef` instance."""

        raise NotImplementedError(
            "get_key_by_ref() is not implemented for this provider"
        )

    @abstractmethod
    async def list_versions(self, kid: str) -> Tuple[int, ...]:
        """Return available versions for a key."""

    @abstractmethod
    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        """Return an RFC 7517 JWK for the public portion of the key."""

    @abstractmethod
    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        """Return a JWKS document containing the latest versions of keys."""

    @abstractmethod
    async def random_bytes(self, n: int) -> bytes:
        """Return ``n`` cryptographically secure random bytes."""

    @abstractmethod
    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        """Derive key material using HKDF-SHA256."""
