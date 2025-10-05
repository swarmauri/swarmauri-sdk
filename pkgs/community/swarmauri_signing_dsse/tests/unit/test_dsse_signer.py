import base64
from typing import Iterable, Mapping, Optional, Sequence

import pytest

from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.signing.types import Signature
from swarmauri_signing_dsse import DSSESigner
from swarmauri_signing_dsse.types import DSSEEnvelope
from swarmauri_base.signing.SigningBase import SigningBase, _stream_to_bytes


class DummySigner(SigningBase):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[tuple[str, bytes]] = []

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "algs": ("Dummy",),
            "canons": ("json",),
            "signs": ("bytes", "envelope"),
            "verifies": ("bytes", "envelope"),
            "envelopes": ("mapping",),
            "features": (),
        }

    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        self.calls.append(("sign_bytes", payload))
        return [
            Signature(
                kid=None,
                version=None,
                format="raw",
                mode="detached",
                alg=alg or "Dummy",
                artifact=payload,
            )
        ]

    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        self.calls.append(("verify_bytes", payload))
        return bool(signatures) and signatures[0].artifact == payload

    async def sign_digest(
        self,
        key: KeyRef,
        digest: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        return await self.sign_bytes(key, digest, alg=alg, opts=opts)

    async def verify_digest(
        self,
        digest: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await self.verify_bytes(digest, signatures, require=require, opts=opts)

    async def canonicalize_envelope(
        self,
        env: DSSEEnvelope | Mapping[str, object],
        *,
        canon: Optional[str] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        self.calls.append(("canonicalize", b"inner"))
        return b"inner"

    async def sign_envelope(
        self,
        key: KeyRef,
        env: DSSEEnvelope | Mapping[str, object],
        *,
        alg: Optional[Alg] = None,
        canon: Optional[str] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        pae = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self.sign_bytes(key, pae, alg=alg, opts=opts)

    async def verify_envelope(
        self,
        env: DSSEEnvelope | Mapping[str, object],
        signatures: Sequence[Signature],
        *,
        canon: Optional[str] = None,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        pae = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self.verify_bytes(pae, signatures, require=require, opts=opts)

    async def sign_stream(
        self,
        key: KeyRef,
        payload,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        data = await _stream_to_bytes(payload)
        return await self.sign_bytes(key, data, alg=alg, opts=opts)

    async def verify_stream(
        self,
        payload,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        data = await _stream_to_bytes(payload)
        return await self.verify_bytes(data, signatures, require=require, opts=opts)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_canonicalize_envelope_mapping() -> None:
    inner = DummySigner()
    signer = DSSESigner(inner)
    envelope = {
        "payloadType": "text/plain",
        "payload": base64.urlsafe_b64encode(b"hello").decode("ascii").rstrip("="),
        "signatures": [{"sig": "ZmFrZVNpZw"}],
    }

    pae = await signer.canonicalize_envelope(envelope)
    assert pae == b"DSSEv1 10 text/plain 5 hello"
    assert inner.calls == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sign_and_verify_delegates_to_inner() -> None:
    inner = DummySigner()
    signer = DSSESigner(inner)
    key_ref = {"kind": "dummy"}
    payload = base64.urlsafe_b64encode(b"payload").decode("ascii").rstrip("=")
    envelope = DSSEEnvelope(payload_type="text/plain", payload_b64=payload)

    signatures = await signer.sign_envelope(key_ref, envelope)
    assert signatures and signatures[0].artifact.startswith(b"DSSEv1")
    assert inner.calls[0][0] == "sign_bytes"

    verified = await signer.verify_envelope(envelope, signatures)
    assert verified is True
    assert inner.calls[1][0] == "verify_bytes"


@pytest.mark.unit
def test_supports_merges_dsse_features() -> None:
    inner = DummySigner()
    signer = DSSESigner(inner)

    capabilities = signer.supports()
    assert "dsse-pae" in capabilities["canons"]
    assert "envelope" in capabilities["signs"]
    assert "detached_only" in capabilities["features"]
