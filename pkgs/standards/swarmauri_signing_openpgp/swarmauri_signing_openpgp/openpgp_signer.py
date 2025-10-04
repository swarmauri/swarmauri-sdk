"""OpenPGP SigningBase implementation backed by the :mod:`pgpy` toolkit."""

from __future__ import annotations

import json
from pathlib import Path
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

try:  # pragma: no cover - runtime import guard
    import pgpy
    from pgpy.constants import HashAlgorithm, SignatureType

    _PGPY_AVAILABLE = True
except Exception:  # pragma: no cover - runtime check
    _PGPY_AVAILABLE = False


def _ensure_pgpy() -> None:
    if not _PGPY_AVAILABLE:
        raise RuntimeError(
            "OpenPGPSigner requires the 'pgpy' package. Install with: pip install pgpy"
        )


async def _stream_to_bytes(stream: StreamLike) -> bytes:
    if isinstance(stream, (bytes, bytearray)):
        return bytes(stream)
    if isinstance(stream, AsyncIterable):
        parts = [bytes(chunk) async for chunk in stream]
        return b"".join(parts)
    if isinstance(stream, Iterable):
        return b"".join(bytes(chunk) for chunk in stream)
    raise TypeError("Unsupported stream payload for OpenPGPSigner")


def _canon_json(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _load_private_key(key_ref: KeyRef) -> pgpy.PGPKey:
    _ensure_pgpy()
    if isinstance(key_ref, pgpy.PGPKey):
        return key_ref
    if isinstance(key_ref, Mapping):
        kind = key_ref.get("kind")
        passphrase = key_ref.get("passphrase")
        if kind == "pgpy-key":
            data = key_ref.get("data")
            if isinstance(data, bytes):
                blob = data
            elif isinstance(data, str):
                blob = data.encode("utf-8")
            else:
                raise TypeError("pgpy-key 'data' must be bytes or str")
            key, _ = pgpy.PGPKey.from_blob(blob)
        elif kind == "pgpy-file":
            path = key_ref.get("path")
            if not isinstance(path, (str, Path)):
                raise TypeError("pgpy-file 'path' must be a filesystem path")
            blob = Path(path).read_bytes()
            key, _ = pgpy.PGPKey.from_blob(blob)
        else:
            raise TypeError("Unsupported KeyRef for OpenPGP private key")
        if key.is_protected and passphrase is not None:
            key.unlock(str(passphrase))
        elif key.is_protected:
            raise RuntimeError(
                "OpenPGP key is passphrase protected; supply 'passphrase'"
            )
        return key
    raise TypeError("OpenPGP KeyRef must be a mapping or pgpy.PGPKey instance")


def _load_public_keys(entries: Optional[Iterable[Any]]) -> list[pgpy.PGPKey]:
    _ensure_pgpy()
    keys: list[pgpy.PGPKey] = []
    for entry in entries or []:
        if isinstance(entry, pgpy.PGPKey):
            keys.append(entry)
            continue
        if isinstance(entry, Mapping):
            kind = entry.get("kind")
            if kind == "pgpy-key":
                data = entry.get("data")
                blob = data.encode("utf-8") if isinstance(data, str) else bytes(data)
                key, _ = pgpy.PGPKey.from_blob(blob)
                keys.append(key)
                continue
            if kind == "pgpy-file":
                path = entry.get("path")
                blob = Path(path).read_bytes()
                key, _ = pgpy.PGPKey.from_blob(blob)
                keys.append(key)
                continue
        if isinstance(entry, (str, bytes)):
            blob = entry.encode("utf-8") if isinstance(entry, str) else entry
            key, _ = pgpy.PGPKey.from_blob(blob)
            keys.append(key)
            continue
        raise TypeError("Unsupported entry in OpenPGP verification key list")
    return keys


def _hash_from_alg(alg: Optional[Alg]) -> HashAlgorithm:
    if alg is None:
        return HashAlgorithm.SHA256
    normalized = str(alg).replace("-", "_").upper()
    try:
        return HashAlgorithm[normalized]
    except KeyError as exc:
        raise ValueError(f"Unsupported OpenPGP hash algorithm: {alg}") from exc


def _serialize_signature(
    signature: pgpy.PGPSignature,
    *,
    payload_kind: str,
    keyid: Optional[str],
    hash_alg: HashAlgorithm,
) -> Signature:
    artifact = str(signature).encode("utf-8")
    meta: MutableMapping[str, Any] = {
        "payload_kind": payload_kind,
        "signature_type": signature.type.name,
    }
    return Signature(
        kid=keyid,
        version=None,
        format="openpgp-armored",
        mode="detached",
        alg=hash_alg.name,
        artifact=artifact,
        meta=meta,
    )


def _load_signature(artifact: Signature | Mapping[str, Any]) -> pgpy.PGPSignature:
    raw: Any
    if isinstance(artifact, Signature):
        raw = artifact.artifact
    else:
        raw = artifact.get("artifact") or artifact.get("sig")
    if isinstance(raw, str):
        blob = raw.encode("utf-8")
    elif isinstance(raw, (bytes, bytearray)):
        blob = bytes(raw)
    else:
        raise TypeError("OpenPGP signatures must provide 'artifact' bytes or str")
    _ensure_pgpy()
    sig = pgpy.PGPSignature.from_blob(blob)
    return sig


def _min_signers(require: Optional[Mapping[str, object]]) -> int:
    if not require:
        return 1
    try:
        return max(1, int(require.get("min_signers", 1)))
    except (TypeError, ValueError):
        return 1


@register_type(resource_type=SigningBase)
class OpenPGPSigner(SigningBase):
    """Produce detached OpenPGP signatures for bytes, digests and structured envelopes."""

    def __init__(
        self,
        key_provider: Optional[IKeyProvider] = None,
    ) -> None:
        self._key_provider = key_provider

    def set_key_provider(self, provider: IKeyProvider) -> None:
        self._key_provider = provider

    # ------------------------------------------------------------------
    def supports(self, key_ref: Optional[str] = None) -> Mapping[str, Iterable[str]]:
        base_caps: Mapping[str, Iterable[str]] = {
            "signs": ("bytes", "digest", "envelope", "stream"),
            "verifies": ("bytes", "digest", "envelope", "stream"),
            "envelopes": ("structured-json", "detached-bytes"),
            "algs": tuple(hash_alg.name for hash_alg in HashAlgorithm),
            "canons": ("json",),
            "features": ("detached", "armored"),
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
            payload_kind="bytes",
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
            payload_kind="digest",
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
            payload_kind="stream",
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
            payload_kind="envelope",
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
        raise ValueError(f"Unsupported canon for OpenPGPSigner: {canon}")

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
        pgp_key = _load_private_key(key)
        hash_alg = _hash_from_alg(alg or (opts or {}).get("hash_alg"))
        data = bytes(payload)
        sig = pgp_key.sign(
            data,
            detached=True,
            hash=hash_alg,
            signature_type=SignatureType.BinaryDocument,
        )
        keyid = None
        if pgp_key.fingerprint:
            keyid = pgp_key.fingerprint.keyid
        return [
            _serialize_signature(
                sig,
                payload_kind=payload_kind,
                keyid=keyid,
                hash_alg=hash_alg,
            )
        ]

    async def _verify_payload(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]],
        opts: Optional[Mapping[str, object]],
        payload_kind: str,
    ) -> bool:
        if not signatures:
            return False
        payload_bytes = bytes(payload)
        keys = _load_public_keys((opts or {}).get("pubkeys"))
        if not keys:
            raise RuntimeError("OpenPGP verification requires opts['pubkeys'] entries")
        min_ok = _min_signers(require)
        accepted = 0
        for sig in signatures:
            meta = sig.meta if isinstance(sig, Signature) else sig.get("meta")
            kind = meta.get("payload_kind") if isinstance(meta, Mapping) else None
            if kind not in (None, payload_kind):
                continue
            pgp_sig = _load_signature(sig)
            for key in keys:
                if key.verify(payload_bytes, pgp_sig):
                    accepted += 1
                    break
            if accepted >= min_ok:
                return True
        return False
