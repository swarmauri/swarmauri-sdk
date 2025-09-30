"""JWS SigningBase implementation backed by :class:`JwsSignerVerifier`."""

from __future__ import annotations

import json
from typing import (
    Any,
    AsyncIterable,
    Iterable,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
)

from swarmauri_base import register_type
from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.keys.IKeyProvider import IKeyProvider
from swarmauri_core.signing.ISigning import Canon, Envelope, StreamLike
from swarmauri_core.signing.types import Signature

from .JwsSignerVerifier import JwsResult, JwsSignerVerifier

__all__ = ["JWSSigner"]


def _canon_json(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


async def _stream_to_bytes(stream: StreamLike) -> bytes:
    if isinstance(stream, (bytes, bytearray)):
        return bytes(stream)
    if isinstance(stream, AsyncIterable):
        parts = [bytes(chunk) async for chunk in stream]
        return b"".join(parts)
    if isinstance(stream, Iterable):
        return b"".join(bytes(chunk) for chunk in stream)
    raise TypeError("Unsupported stream type for JWSSigner")


def _extract_compact(signature: Signature | Mapping[str, Any]) -> str:
    value: Mapping[str, Any]
    if isinstance(signature, Signature):
        value = {key: signature[key] for key in signature}
    else:
        value = signature
    artifact = value.get("artifact")
    if isinstance(artifact, (bytes, bytearray)):
        return artifact.decode("ascii")
    if isinstance(artifact, str):
        return artifact
    payload = value.get("compact")
    if isinstance(payload, str):
        return payload
    raise TypeError("Signature artifact must be compact JWS serialization")


def _allowed_from_require(
    require: Optional[Mapping[str, object]],
) -> Optional[set[str]]:
    if not require:
        return None
    raw = require.get("algs")
    if not raw:
        return None
    return {str(entry) for entry in raw if entry is not None}


def _min_signers(require: Optional[Mapping[str, object]]) -> int:
    if not require:
        return 1
    try:
        return max(1, int(require.get("min_signers", 1)))
    except (TypeError, ValueError):
        return 1


def _meta_dict(signature: Signature | Mapping[str, Any]) -> MutableMapping[str, Any]:
    if isinstance(signature, Signature):
        meta = signature.meta
    else:
        meta = signature.get("meta")  # type: ignore[attr-defined]
    if isinstance(meta, MutableMapping):
        return meta
    if isinstance(meta, Mapping):
        return dict(meta)
    return {}


def _payload_kind(signature: Signature | Mapping[str, Any]) -> str:
    meta = _meta_dict(signature)
    kind = meta.get("payload_kind")
    if isinstance(kind, str):
        return kind
    return "bytes"


@register_type(resource_type=SigningBase)
class JWSSigner(SigningBase):
    """Sign and verify payloads using JSON Web Signatures."""

    def __init__(
        self,
        key_provider: Optional[IKeyProvider] = None,
        *,
        verifier: Optional[JwsSignerVerifier] = None,
    ) -> None:
        self._key_provider = key_provider
        self._jws = verifier or JwsSignerVerifier()

    def set_key_provider(self, provider: IKeyProvider) -> None:
        self._key_provider = provider

    # ------------------------------------------------------------------
    def supports(self, key_ref: Optional[str] = None) -> Mapping[str, Iterable[str]]:
        base = {
            "signs": ("bytes", "digest", "envelope", "stream"),
            "verifies": ("bytes", "digest", "envelope", "stream"),
            "envelopes": ("structured-json", "detached-bytes"),
            "algs": (
                "HS256",
                "HS384",
                "HS512",
                "RS256",
                "RS384",
                "RS512",
                "PS256",
                "PS384",
                "PS512",
                "ES256",
                "ES256K",
                "ES384",
                "ES512",
                "EdDSA",
            ),
            "canons": ("json",),
            "features": ("attached", "compact", "detached"),
            "status": ("beta",),
        }
        if key_ref is None:
            return base
        return {**base, "key_refs": (key_ref,)}

    # ------------------------------------------------------------------
    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        return await self._sign_payload(
            key,
            payload,
            alg=alg,
            opts=opts,
            payload_kind="bytes",
        )

    async def sign_digest(
        self,
        key: KeyRef,
        digest: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        return await self._sign_payload(
            key,
            digest,
            alg=alg,
            opts=opts,
            payload_kind="digest",
        )

    async def sign_stream(
        self,
        key: KeyRef,
        payload: StreamLike,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        data = await _stream_to_bytes(payload)
        return await self._sign_payload(
            key,
            data,
            alg=alg,
            opts=opts,
            payload_kind="stream",
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
        canonical = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self._sign_payload(
            key,
            canonical,
            alg=alg,
            opts=opts,
            payload_kind="envelope",
        )

    # ------------------------------------------------------------------
    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await self._verify_payload(
            payload,
            signatures,
            require=require,
            opts=opts,
            expect_kind="bytes",
        )

    async def verify_digest(
        self,
        digest: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        return await self._verify_payload(
            digest,
            signatures,
            require=require,
            opts=opts,
            expect_kind="digest",
        )

    async def verify_stream(
        self,
        payload: StreamLike,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        data = await _stream_to_bytes(payload)
        return await self._verify_payload(
            data,
            signatures,
            require=require,
            opts=opts,
            expect_kind="stream",
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
        return await self._verify_payload(
            canonical,
            signatures,
            require=require,
            opts=opts,
            expect_kind="envelope",
        )

    # ------------------------------------------------------------------
    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        if canon in (None, "json"):
            return _canon_json(env)
        if canon == "raw":
            if isinstance(env, (bytes, bytearray)):
                return bytes(env)
            raise TypeError("raw canon expects bytes envelope")
        raise ValueError(f"Unsupported canon for JWSSigner: {canon}")

    # ------------------------------------------------------------------
    async def _sign_payload(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg],
        opts: Optional[Mapping[str, object]],
        payload_kind: str,
    ) -> Sequence[Signature]:
        options = dict(opts or {})
        alg_token = str(alg or options.pop("alg", "HS256"))
        kid = options.pop("kid", None)
        typ = options.pop("typ", None)
        header_extra = options.pop("header", None)
        if header_extra is not None and not isinstance(header_extra, Mapping):
            raise TypeError("opts['header'] must be a mapping when provided")
        compact = await self._jws.sign_compact(
            payload=payload,
            alg=alg_token,
            key=key,  # type: ignore[arg-type]
            kid=str(kid) if kid is not None else None,
            header_extra=None if header_extra is None else dict(header_extra),
            typ=str(typ) if typ is not None else None,
        )
        header = {"alg": alg_token}
        if kid is not None:
            header["kid"] = kid
        if typ is not None:
            header["typ"] = typ
        if header_extra:
            header.update(dict(header_extra))
        meta = options.pop("meta", {}) or {}
        if not isinstance(meta, Mapping):
            raise TypeError("opts['meta'] must be a mapping when provided")
        final_meta = dict(meta)
        final_meta.setdefault("payload_kind", payload_kind)
        final_meta.setdefault("header", header)
        return [
            Signature(
                kid=str(kid) if kid is not None else None,
                version=None,
                format="jws-compact",
                mode="attached",
                alg=alg_token,
                artifact=compact.encode("ascii"),
                headers=header,
                meta=final_meta,
            )
        ]

    async def _verify_payload(
        self,
        expected: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]],
        opts: Optional[Mapping[str, object]],
        expect_kind: str,
    ) -> bool:
        if not signatures:
            return False
        allowed = _allowed_from_require(require)
        min_ok = _min_signers(require)
        verifier_opts = dict(opts or {})
        accepted = 0
        for sig in signatures:
            kind = _payload_kind(sig)
            allowed_kinds = {expect_kind}
            if expect_kind == "stream":
                allowed_kinds.add("bytes")
            if kind not in allowed_kinds:
                continue
            compact = _extract_compact(sig)
            try:
                result = await self._verify_compact(compact, allowed, verifier_opts)
            except Exception:
                continue
            if result.payload != expected:
                continue
            accepted += 1
            if accepted >= min_ok:
                return True
        return False

    async def _verify_compact(
        self,
        compact: str,
        allowed: Optional[set[str]],
        opts: Mapping[str, object],
    ) -> JwsResult:
        kwargs: dict[str, object] = {}
        if allowed:
            kwargs["alg_allowlist"] = tuple(allowed)
        for key in (
            "hmac_keys",
            "rsa_pubkeys",
            "ec_pubkeys",
            "ed_pubkeys",
            "k1_pubkeys",
            "jwks_resolver",
        ):
            if key in opts and opts[key] is not None:
                kwargs[key] = opts[key]
        return await self._jws.verify_compact(compact, **kwargs)
