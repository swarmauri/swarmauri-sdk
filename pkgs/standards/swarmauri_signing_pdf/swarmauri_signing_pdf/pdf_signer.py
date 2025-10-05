"""PDF signer built on top of the CMS signer implementation."""

from __future__ import annotations

import json
from typing import Iterable, Mapping, Optional, Sequence

from swarmauri_base import register_type
from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.keys.IKeyProvider import IKeyProvider
from swarmauri_core.signing.ISigning import Canon, Envelope, StreamLike
from swarmauri_core.signing.types import Signature

from swarmauri_signing_cms import CMSSigner


def _canon_json(obj: Mapping[str, object]) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _adapt_signature(
    sig: Signature, *, payload_kind: str, pdf_meta: Mapping[str, object]
) -> Signature:
    meta = {}
    if sig.meta:
        meta.update(dict(sig.meta))
    meta.update(pdf_meta)
    meta["payload_kind"] = payload_kind
    return Signature(
        kid=sig.kid,
        version=sig.version,
        format="pdf-cms",
        mode=sig.mode,
        alg=sig.alg,
        artifact=sig.artifact,
        hash_alg=sig.hash_alg,
        cert_chain_der=sig.cert_chain_der,
        headers=sig.headers,
        meta=meta,
        ts=sig.ts,
        sig=sig.sig,
        chain=sig.chain,
    )


def _pdf_meta(opts: Optional[Mapping[str, object]]) -> Mapping[str, object]:
    if not opts:
        return {"attached": True, "pdf": {}}
    pdf_info = dict(opts.get("pdf", {}) or {})
    attached = bool(opts.get("attached", True))
    pdf_info.setdefault("reason", opts.get("reason"))
    pdf_info.setdefault("location", opts.get("location"))
    pdf_info.setdefault("contact", opts.get("contact"))
    return {
        "attached": attached,
        "pdf": {k: v for k, v in pdf_info.items() if v is not None},
    }


def _ensure_bytes(data: bytes | bytearray | memoryview | str) -> bytes:
    if isinstance(data, (bytes, bytearray, memoryview)):
        return bytes(data)
    if isinstance(data, str):
        return data.encode("utf-8")
    raise TypeError("PDF payloads must be bytes or str")


@register_type(resource_type=SigningBase)
class PDFSigner(SigningBase):
    """High-level PDF signer that leverages the CMS signer for cryptography."""

    def __init__(self, key_provider: Optional[IKeyProvider] = None) -> None:
        self._cms = CMSSigner(key_provider=key_provider)

    def set_key_provider(self, provider: IKeyProvider) -> None:
        self._cms.set_key_provider(provider)

    # ------------------------------------------------------------------
    def supports(self, key_ref: Optional[str] = None) -> Mapping[str, Iterable[str]]:
        base_caps = {
            "signs": ("bytes", "digest", "envelope", "stream"),
            "verifies": ("bytes", "digest", "envelope", "stream"),
            "envelopes": ("pdf", "structured-json"),
            "algs": ("SHA256", "SHA384", "SHA512"),
            "canons": ("pdf", "json"),
            "features": ("attached", "visual", "timestamp_optional"),
            "status": ("beta",),
        }
        if key_ref is None:
            return base_caps
        return {**base_caps, "key_refs": (key_ref,)}

    # ------------------------------------------------------------------
    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        pdf_opts = dict(opts or {})
        pdf_opts.setdefault("attached", True)
        cms_sigs = await self._cms.sign_bytes(
            key, _ensure_bytes(payload), alg=alg, opts=pdf_opts
        )
        pdf_meta = _pdf_meta(pdf_opts)
        return [
            _adapt_signature(sig, payload_kind="bytes", pdf_meta=pdf_meta)
            for sig in cms_sigs
        ]

    async def sign_digest(
        self,
        key: KeyRef,
        digest: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        pdf_opts = dict(opts or {})
        pdf_opts.setdefault("attached", True)
        cms_sigs = await self._cms.sign_digest(key, digest, alg=alg, opts=pdf_opts)
        pdf_meta = _pdf_meta(pdf_opts)
        return [
            _adapt_signature(sig, payload_kind="digest", pdf_meta=pdf_meta)
            for sig in cms_sigs
        ]

    async def sign_stream(
        self,
        key: KeyRef,
        payload: StreamLike,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        pdf_opts = dict(opts or {})
        pdf_opts.setdefault("attached", True)
        cms_sigs = await self._cms.sign_stream(key, payload, alg=alg, opts=pdf_opts)
        pdf_meta = _pdf_meta(pdf_opts)
        return [
            _adapt_signature(sig, payload_kind="stream", pdf_meta=pdf_meta)
            for sig in cms_sigs
        ]

    async def sign_envelope(
        self,
        key: KeyRef,
        env: Envelope,
        *,
        alg: Optional[Alg] = None,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        canonical = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        pdf_opts = dict(opts or {})
        pdf_opts.setdefault("attached", True)
        cms_sigs = await self._cms.sign_bytes(key, canonical, alg=alg, opts=pdf_opts)
        pdf_meta = _pdf_meta(pdf_opts)
        return [
            _adapt_signature(sig, payload_kind="envelope", pdf_meta=pdf_meta)
            for sig in cms_sigs
        ]

    # ------------------------------------------------------------------
    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await self._cms.verify_bytes(
            _ensure_bytes(payload), signatures, require=require, opts=opts
        )

    async def verify_digest(
        self,
        digest: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await self._cms.verify_digest(
            digest, signatures, require=require, opts=opts
        )

    async def verify_stream(
        self,
        payload: StreamLike,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await self._cms.verify_stream(
            payload, signatures, require=require, opts=opts
        )

    async def verify_envelope(
        self,
        env: Envelope,
        signatures: Sequence[Signature],
        *,
        canon: Optional[Canon] = None,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        canonical = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self._cms.verify_envelope(
            canonical,
            signatures,
            canon="raw",
            require=require,
            opts=opts,
        )

    # ------------------------------------------------------------------
    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        if canon in (None, "pdf"):
            if isinstance(env, (bytes, bytearray)):
                return bytes(env)
            raise TypeError("PDF envelopes require bytes payloads")
        if canon == "json":
            if isinstance(env, Mapping):
                return _canon_json(env)
            raise TypeError("json canon expects mapping envelope for PDFSigner")
        raise ValueError(f"Unsupported canon for PDFSigner: {canon}")
