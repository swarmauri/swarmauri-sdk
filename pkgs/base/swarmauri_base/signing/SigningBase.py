"""Base class for detached signing providers."""

from __future__ import annotations

from typing import Iterable, Mapping, Optional, Sequence

from pydantic import Field

from swarmauri_core.signing.ISigning import ByteStream, Canon, Envelope, ISigning
from swarmauri_core.signing.types import Signature
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class SigningBase(ISigning, ComponentBase):
    """Default NotImplemented implementations for :class:`ISigning`."""

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: str = "SigningBase"

    # ------------------------------------------------------------------
    def supports(self, key_ref: Optional[str] = None) -> Mapping[str, Iterable[str]]:
        raise NotImplementedError("supports() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        raise NotImplementedError("sign_bytes() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def sign_digest(
        self,
        key: KeyRef,
        digest: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        raise NotImplementedError("sign_digest() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def sign_stream(
        self,
        key: KeyRef,
        stream: ByteStream,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        raise NotImplementedError("sign_stream() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        raise NotImplementedError("verify_bytes() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def verify_digest(
        self,
        digest: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        raise NotImplementedError("verify_digest() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def verify_stream(
        self,
        stream: ByteStream,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        raise NotImplementedError("verify_stream() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        raise NotImplementedError(
            "canonicalize_envelope() must be implemented by subclass"
        )

    # ------------------------------------------------------------------
    async def sign_envelope(
        self,
        key: KeyRef,
        env: Envelope,
        *,
        alg: Optional[Alg] = None,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        raise NotImplementedError("sign_envelope() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def verify_envelope(
        self,
        env: Envelope,
        signatures: Sequence[Signature],
        *,
        canon: Optional[Canon] = None,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        raise NotImplementedError("verify_envelope() must be implemented by subclass")
