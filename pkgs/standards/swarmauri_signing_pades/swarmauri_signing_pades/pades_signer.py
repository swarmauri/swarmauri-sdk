"""Stub PAdES signer registered with the Swarmauri registry."""

from __future__ import annotations

from typing import Iterable, Mapping, Optional, Sequence

from swarmauri_base import register_type
from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.keys.IKeyProvider import IKeyProvider
from swarmauri_core.signing.ISigning import Canon, Envelope, StreamLike
from swarmauri_core.signing.types import Signature


@register_type(resource_type=SigningBase, type_name="pades")
class PadesSigner(SigningBase):
    """Placeholder PAdES signer that advertises attached PDF signature support."""

    def __init__(self, key_provider: Optional[IKeyProvider] = None) -> None:
        self._key_provider = key_provider

    def set_key_provider(self, provider: IKeyProvider) -> None:
        self._key_provider = provider

    def supports(self, key_ref: Optional[str] = None) -> Mapping[str, Iterable[str]]:
        base_caps: Mapping[str, Iterable[str]] = {
            "signs": ("envelope",),
            "verifies": ("envelope",),
            "envelopes": ("pdf", "pades"),
            "algs": ("ecdsa", "rsa-pss"),
            "canons": ("pdf",),
            "features": ("attached",),
            "status": ("stub", "not-implemented"),
        }
        if key_ref is None:
            return base_caps
        return {**base_caps, "key_refs": (key_ref,)}

    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        raise NotImplementedError("PadesSigner.sign_bytes is not implemented yet")

    async def sign_digest(
        self,
        key: KeyRef,
        digest: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        raise NotImplementedError("PadesSigner.sign_digest is not implemented yet")

    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        raise NotImplementedError("PadesSigner.verify_bytes is not implemented yet")

    async def verify_digest(
        self,
        digest: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        raise NotImplementedError("PadesSigner.verify_digest is not implemented yet")

    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        raise NotImplementedError(
            "PadesSigner.canonicalize_envelope is not implemented yet"
        )

    async def sign_envelope(
        self,
        key: KeyRef,
        env: Envelope,
        *,
        alg: Optional[Alg] = None,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        raise NotImplementedError("PadesSigner.sign_envelope is not implemented yet")

    async def sign_stream(
        self,
        key: KeyRef,
        payload: StreamLike,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        raise NotImplementedError("PadesSigner.sign_stream is not implemented yet")

    async def verify_envelope(
        self,
        env: Envelope,
        signatures: Sequence[Signature],
        *,
        canon: Optional[Canon] = None,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        raise NotImplementedError("PadesSigner.verify_envelope is not implemented yet")

    async def verify_stream(
        self,
        payload: StreamLike,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        raise NotImplementedError("PadesSigner.verify_stream is not implemented yet")
