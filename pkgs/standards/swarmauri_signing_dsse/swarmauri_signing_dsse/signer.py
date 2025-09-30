"""DSSE signer adapter that wraps an inner Swarmauri signer."""

from __future__ import annotations

import base64
from typing import Iterable, Mapping, Optional, Sequence

from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.signing.ISigning import ByteStream, Canon, Envelope
from swarmauri_core.signing.types import Signature
from swarmauri_base.ComponentBase import ResourceTypes
from swarmauri_base.signing.SigningBase import SigningBase

from .codec_json import DSSEJsonCodec
from .types import DSSEEnvelope

_SP = b" "


def _i2b(value: int) -> bytes:
    """Convert an integer to its ASCII byte representation."""

    return str(value).encode("ascii")


def _b64d(data: str) -> bytes:
    """Decode URL-safe base64 strings that may omit padding."""

    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def dsse_pae(payload_type: str, payload: bytes) -> bytes:
    """Compute the DSSE Pre-Authentication Encoding (PAE)."""

    encoded_type = payload_type.encode("utf-8")
    return (
        b"DSSEv1"
        + _SP
        + _i2b(len(encoded_type))
        + _SP
        + encoded_type
        + _SP
        + _i2b(len(payload))
        + _SP
        + payload
    )


class DSSESigner(SigningBase):
    """Wrap an inner :class:`SigningBase` with DSSE envelope support."""

    type: str = "DSSESigner"
    resource: Optional[str] = ResourceTypes.CRYPTO.value

    def __init__(
        self, inner: SigningBase, *, codec: Optional[DSSEJsonCodec] = None
    ) -> None:
        """Initialize the adapter with an inner signer and optional codec."""

        super().__init__()
        self._inner = inner
        self._codec = codec or DSSEJsonCodec()

    # --------------------------- Capability surface ---------------------------
    def supports(self) -> Mapping[str, Iterable[str]]:
        """Return the merged capability matrix from the inner signer and DSSE."""

        inner = self._inner.supports()
        return {
            "algs": inner.get("algs", ()),
            "canons": tuple(set(inner.get("canons", ())) | {"dsse-pae"}),
            "signs": tuple(
                set(inner.get("signs", ())) | {"envelope", "bytes", "digest", "stream"}
            ),
            "verifies": tuple(
                set(inner.get("verifies", ()))
                | {"envelope", "bytes", "digest", "stream"}
            ),
            "envelopes": tuple(set(inner.get("envelopes", ())) | {"mapping"}),
            "features": tuple(
                set(inner.get("features", ())) | {"detached_only", "multi"}
            ),
        }

    # --------------------------- Bytes / Digest / Stream ---------------------------
    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        """Delegate raw byte signing to the wrapped signer."""

        return await self._inner.sign_bytes(key, payload, alg=alg, opts=opts)

    async def sign_digest(
        self,
        key: KeyRef,
        digest: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        """Delegate digest signing to the wrapped signer."""

        return await self._inner.sign_digest(key, digest, alg=alg, opts=opts)

    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        """Delegate byte verification to the wrapped signer."""

        return await self._inner.verify_bytes(
            payload, signatures, require=require, opts=opts
        )

    async def sign_stream(
        self,
        key: KeyRef,
        payload: ByteStream,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        """Delegate stream signing to the wrapped signer."""

        return await self._inner.sign_stream(key, payload, alg=alg, opts=opts)

    async def verify_stream(
        self,
        payload: ByteStream,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        """Delegate stream verification to the wrapped signer."""

        return await self._inner.verify_stream(
            payload, signatures, require=require, opts=opts
        )

    # --------------------------- Envelopes (DSSE) ---------------------------
    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        """Canonicalize an envelope using DSSE PAE when requested."""

        if canon not in (None, "dsse-pae"):
            return await self._inner.canonicalize_envelope(env, canon=canon, opts=opts)

        envelope = self.decode_envelope(env)
        payload = _b64d(envelope.payload_b64)
        return dsse_pae(envelope.payload_type, payload)

    async def sign_envelope(
        self,
        key: KeyRef,
        env: Envelope,
        *,
        alg: Optional[Alg] = None,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        """Sign a DSSE envelope by delegating to the wrapped signer over the PAE."""

        pae = await self.canonicalize_envelope(
            env, canon=canon or "dsse-pae", opts=opts
        )
        return await self._inner.sign_bytes(key, pae, alg=alg, opts=opts)

    async def verify_envelope(
        self,
        env: Envelope,
        signatures: Sequence[Signature],
        *,
        canon: Optional[Canon] = None,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        """Verify a DSSE envelope by delegating to the wrapped signer over the PAE."""

        pae = await self.canonicalize_envelope(
            env, canon=canon or "dsse-pae", opts=opts
        )
        return await self._inner.verify_bytes(
            pae, signatures, require=require, opts=opts
        )

    # --------------------------- Helpers for (de)serialization ---------------------------
    def encode_envelope(self, envelope: DSSEEnvelope | Mapping[str, object]) -> bytes:
        """Encode an envelope (object or mapping) into JSON bytes."""

        return self._codec.encode(self.decode_envelope(envelope))

    def decode_envelope(
        self,
        blob: Envelope | bytes | bytearray | str | Mapping[str, object] | DSSEEnvelope,
    ) -> DSSEEnvelope:
        """Decode envelope inputs into a :class:`DSSEEnvelope` instance."""

        return self._codec.decode(blob)


__all__ = ["DSSESigner", "DSSEEnvelope", "dsse_pae"]
