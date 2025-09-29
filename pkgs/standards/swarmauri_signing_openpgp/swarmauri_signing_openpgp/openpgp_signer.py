"""Stub OpenPGP signer registered with the Swarmauri registry."""

from __future__ import annotations

from typing import Iterable, Mapping, Optional, Sequence

from swarmauri_base import register_type
from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.keys.IKeyProvider import IKeyProvider
from swarmauri_core.signing.ISigning import Canon, Envelope
from swarmauri_core.signing.types import Signature


@register_type(resource_type=SigningBase, type_name="openpgp")
class OpenPGPSigner(SigningBase):
    """Placeholder OpenPGP signer exposing registry metadata."""

    def __init__(self, key_provider: Optional[IKeyProvider] = None) -> None:
        self._key_provider = key_provider

    def set_key_provider(self, provider: IKeyProvider) -> None:
        self._key_provider = provider

    def supports(self, key_ref: Optional[str] = None) -> Mapping[str, Iterable[str]]:
        base_caps: Mapping[str, Iterable[str]] = {
            "algs": ("openpgp",),
            "canons": ("rfc4880",),
            "signs": ("bytes", "envelope"),
            "verifies": ("bytes", "envelope"),
            "envelopes": ("openpgp",),
            "features": ("detached", "attached"),
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
        raise NotImplementedError("OpenPGPSigner.sign_bytes is not implemented yet")

    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        raise NotImplementedError("OpenPGPSigner.verify_bytes is not implemented yet")

    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        raise NotImplementedError(
            "OpenPGPSigner.canonicalize_envelope is not implemented yet"
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
        raise NotImplementedError("OpenPGPSigner.sign_envelope is not implemented yet")

    async def verify_envelope(
        self,
        env: Envelope,
        signatures: Sequence[Signature],
        *,
        canon: Optional[Canon] = None,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        raise NotImplementedError(
            "OpenPGPSigner.verify_envelope is not implemented yet"
        )
