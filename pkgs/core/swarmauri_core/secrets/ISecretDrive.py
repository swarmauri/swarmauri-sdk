"""Interface for secrets storage drivers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional

from swarmauri_core.crypto.types import (
    ExportPolicy,
    KeyDescriptor,
    KeyId,
    KeyRef,
    KeyState,
    KeyType,
    KeyUse,
    KeyVersion,
    Page,
)


class ISecretDrive(ABC):
    @abstractmethod
    async def store_key(
        self,
        *,
        key_type: KeyType,
        uses: Iterable[KeyUse],
        name: Optional[str] = None,
        material: Optional[bytes] = None,
        export_policy: ExportPolicy = ExportPolicy.PUBLIC_ONLY,
        tags: Optional[Dict[str, str]] = None,
        tenant: Optional[str] = None,
    ) -> KeyDescriptor: ...

    @abstractmethod
    async def load_key(
        self,
        *,
        kid: KeyId,
        version: Optional[KeyVersion] = None,
        require_private: bool = False,
        tenant: Optional[str] = None,
    ) -> KeyRef: ...

    @abstractmethod
    async def list(
        self,
        *,
        name_prefix: Optional[str] = None,
        types: Optional[Iterable[KeyType]] = None,
        states: Optional[Iterable[KeyState]] = (KeyState.ENABLED,),
        tags: Optional[Dict[str, str]] = None,
        limit: int = 100,
        cursor: Optional[str] = None,
        tenant: Optional[str] = None,
    ) -> Page: ...

    @abstractmethod
    async def describe(
        self, *, kid: KeyId, tenant: Optional[str] = None
    ) -> KeyDescriptor: ...

    @abstractmethod
    async def rotate(
        self,
        *,
        kid: KeyId,
        material: Optional[bytes] = None,
        make_primary: bool = True,
        tags: Optional[Dict[str, str]] = None,
        tenant: Optional[str] = None,
    ) -> KeyDescriptor: ...

    @abstractmethod
    async def set_state(
        self,
        *,
        kid: KeyId,
        state: KeyState,
        tenant: Optional[str] = None,
    ) -> KeyDescriptor: ...
