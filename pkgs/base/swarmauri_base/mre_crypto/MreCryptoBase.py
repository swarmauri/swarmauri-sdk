"""Base class for multi-recipient encryption providers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from pydantic import Field
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.mre_crypto.IMreCrypto import (
    IMreCrypto,
    MreMode,
    MultiRecipientEnvelope,
    RecipientId,
)

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class MreCryptoBase(IMreCrypto, ComponentBase):
    """Default NotImplemented implementations for :class:`IMreCrypto`."""

    resource: str | None = Field(
        default=ResourceTypes.CRYPTO.value, frozen=True
    )
    type: str = "MreCryptoBase"

    # ------------------------------------------------------------------
    def supports(self) -> dict[str, Iterable[str | MreMode]]:
        raise NotImplementedError("supports() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def encrypt_for_many(
        self,
        recipients: Sequence[KeyRef],
        pt: bytes,
        *,
        payload_alg: Alg | None = None,
        recipient_alg: Alg | None = None,
        mode: MreMode | str | None = None,
        aad: bytes | None = None,
        shared: Mapping[str, bytes] | None = None,
        opts: Mapping[str, object] | None = None,
    ) -> MultiRecipientEnvelope:
        raise NotImplementedError(
            "encrypt_for_many() must be implemented by subclass"
        )

    # ------------------------------------------------------------------
    async def open_for(
        self,
        my_identity: KeyRef,
        env: MultiRecipientEnvelope,
        *,
        aad: bytes | None = None,
        opts: Mapping[str, object] | None = None,
    ) -> bytes:
        raise NotImplementedError("open_for() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def open_for_many(
        self,
        my_identities: Sequence[KeyRef],
        env: MultiRecipientEnvelope,
        *,
        aad: bytes | None = None,
        opts: Mapping[str, object] | None = None,
    ) -> bytes:
        raise NotImplementedError(
            "open_for_many() must be implemented by subclass"
        )

    # ------------------------------------------------------------------
    async def rewrap(
        self,
        env: MultiRecipientEnvelope,
        *,
        add: Sequence[KeyRef] | None = None,
        remove: Sequence[RecipientId] | None = None,
        recipient_alg: Alg | None = None,
        opts: Mapping[str, object] | None = None,
    ) -> MultiRecipientEnvelope:
        raise NotImplementedError("rewrap() must be implemented by subclass")
