"""Base class for multi-recipient encryption providers."""

from __future__ import annotations

from typing import Dict, Iterable, Mapping, Optional, Sequence

from pydantic import Field

from swarmauri_core.mre_crypto.IMreCrypto import (
    IMreCrypto,
    MreMode,
    MultiRecipientEnvelope,
    RecipientId,
)
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class MreCryptoBase(IMreCrypto, ComponentBase):
    """Default NotImplemented implementations for :class:`IMreCrypto`."""

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: str = "MreCryptoBase"

    # ------------------------------------------------------------------
    def supports(self) -> Dict[str, Iterable[str | MreMode]]:
        raise NotImplementedError("supports() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def encrypt_for_many(
        self,
        recipients: Sequence[KeyRef],
        pt: bytes,
        *,
        payload_alg: Optional[Alg] = None,
        recipient_alg: Optional[Alg] = None,
        mode: Optional[MreMode | str] = None,
        aad: Optional[bytes] = None,
        shared: Optional[Mapping[str, bytes]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> MultiRecipientEnvelope:
        raise NotImplementedError("encrypt_for_many() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def open_for(
        self,
        my_identity: KeyRef,
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        raise NotImplementedError("open_for() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def open_for_many(
        self,
        my_identities: Sequence[KeyRef],
        env: MultiRecipientEnvelope,
        *,
        aad: Optional[bytes] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        raise NotImplementedError("open_for_many() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def rewrap(
        self,
        env: MultiRecipientEnvelope,
        *,
        add: Optional[Sequence[KeyRef]] = None,
        remove: Optional[Sequence[RecipientId]] = None,
        recipient_alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> MultiRecipientEnvelope:
        raise NotImplementedError("rewrap() must be implemented by subclass")
