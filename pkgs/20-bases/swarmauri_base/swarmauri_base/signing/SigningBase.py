"""Base class for detached signing providers."""

from __future__ import annotations

from collections.abc import AsyncIterable, Iterable, Mapping, Sequence

from pydantic import Field
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.signing.ISigning import (
    ByteStream,
    Canon,
    Envelope,
    ISigning,
)
from swarmauri_core.signing.types import Signature

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


async def _stream_to_bytes(stream: ByteStream) -> bytes:
    """
    Collect a synchronous or asynchronous byte stream into a single buffer.
    """

    if isinstance(stream, (bytes, bytearray)):
        return bytes(stream)

    chunks = bytearray()

    if isinstance(stream, AsyncIterable):
        async for chunk in stream:
            if not isinstance(chunk, (bytes, bytearray)):
                raise TypeError("Stream yielded non-bytes chunk")
            chunks.extend(chunk)
        return bytes(chunks)

    if isinstance(stream, Iterable):
        for chunk in stream:
            if not isinstance(chunk, (bytes, bytearray)):
                raise TypeError("Stream yielded non-bytes chunk")
            chunks.extend(chunk)
        return bytes(chunks)

    raise TypeError(
        "Unsupported stream type; expected bytes or iterable of bytes"
    )


@ComponentBase.register_model()
class SigningBase(ISigning, ComponentBase):
    """Default NotImplemented implementations for :class:`ISigning`."""

    resource: str | None = Field(
        default=ResourceTypes.CRYPTO.value, frozen=True
    )
    type: str = "SigningBase"

    # ------------------------------------------------------------------
    def supports(self) -> Mapping[str, Iterable[str]]:
        raise NotImplementedError("supports() must be implemented by subclass")

    # ------------------------------------------------------------------
    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Alg | None = None,
        opts: Mapping[str, object] | None = None,
    ) -> Sequence[Signature]:
        raise NotImplementedError(
            "sign_bytes() must be implemented by subclass"
        )

    # ------------------------------------------------------------------
    async def sign_digest(
        self,
        key: KeyRef,
        digest: bytes,
        *,
        alg: Alg | None = None,
        opts: Mapping[str, object] | None = None,
    ) -> Sequence[Signature]:
        """Default digest handling routes through :meth:`sign_bytes`.

        Subclasses that override :meth:`sign_bytes` to call :meth:`sign_digest`
        must also provide their own :meth:`sign_digest` implementation to avoid
        creating a mutual recursion.
        """

        return await self.sign_bytes(key, digest, alg=alg, opts=opts)

    # ------------------------------------------------------------------
    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Mapping[str, object] | None = None,
        opts: Mapping[str, object] | None = None,
    ) -> bool:
        raise NotImplementedError(
            "verify_bytes() must be implemented by subclass"
        )

    # ------------------------------------------------------------------
    async def verify_digest(
        self,
        digest: bytes,
        signatures: Sequence[Signature],
        *,
        require: Mapping[str, object] | None = None,
        opts: Mapping[str, object] | None = None,
    ) -> bool:
        """Default digest verification routes through :meth:`verify_bytes`.

        As with :meth:`sign_digest`, subclasses that redirect
        :meth:`verify_bytes` to :meth:`verify_digest` should override this
        method directly to avoid recursion.
        """

        return await self.verify_bytes(
            digest,
            signatures,
            require=require,
            opts=opts,
        )

    # ------------------------------------------------------------------
    async def sign_stream(
        self,
        key: KeyRef,
        payload: ByteStream,
        *,
        alg: Alg | None = None,
        opts: Mapping[str, object] | None = None,
    ) -> Sequence[Signature]:
        data = await _stream_to_bytes(payload)
        return await self.sign_bytes(key, data, alg=alg, opts=opts)

    # ------------------------------------------------------------------
    async def verify_stream(
        self,
        payload: ByteStream,
        signatures: Sequence[Signature],
        *,
        require: Mapping[str, object] | None = None,
        opts: Mapping[str, object] | None = None,
    ) -> bool:
        data = await _stream_to_bytes(payload)
        return await self.verify_bytes(
            data, signatures, require=require, opts=opts
        )

    # ------------------------------------------------------------------
    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Canon | None = None,
        opts: Mapping[str, object] | None = None,
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
        alg: Alg | None = None,
        canon: Canon | None = None,
        opts: Mapping[str, object] | None = None,
    ) -> Sequence[Signature]:
        raise NotImplementedError(
            "sign_envelope() must be implemented by subclass"
        )

    # ------------------------------------------------------------------
    async def verify_envelope(
        self,
        env: Envelope,
        signatures: Sequence[Signature],
        *,
        canon: Canon | None = None,
        require: Mapping[str, object] | None = None,
        opts: Mapping[str, object] | None = None,
    ) -> bool:
        raise NotImplementedError(
            "verify_envelope() must be implemented by subclass"
        )
