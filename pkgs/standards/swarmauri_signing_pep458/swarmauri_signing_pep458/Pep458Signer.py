"""PEP 458 detached signing provider."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)

from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.signing.ISigning import Canon, Envelope
from swarmauri_core.signing.types import Signature

_TUF_JSON_CANON = ("tuf-json", "json")
_SUPPORTED_METHODS = ("ed25519", "rsa-pss-sha256")
_ALLOWED_ALGS = ("Ed25519", "RSA-PSS-SHA256")


def _canon_tuf_json(obj: Any) -> bytes:
    """Return TUF-style canonical JSON."""

    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _method_from_alg(value: str) -> str:
    normalized = value.replace("_", "-").lower()
    if normalized in {"ed25519"}:
        return "ed25519"
    if normalized in {"rsa-pss-sha256", "rsapsssha256", "rsa-psssha256"}:
        return "rsa-pss-sha256"
    raise ValueError(f"Unsupported alg: {value}")


def _alg_from_method(method: str) -> str:
    if method == "ed25519":
        return "Ed25519"
    if method == "rsa-pss-sha256":
        return "RSA-PSS-SHA256"
    raise ValueError(f"Unknown method label: {method}")


def _keyid_for_public_key(pub: Any, method: str) -> str:
    spki = pub.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    hasher = hashes.Hash(hashes.SHA256())
    hasher.update(method.encode("ascii") + b"\x00" + spki)
    return _b64(hasher.finalize())


@dataclass(frozen=True)
class _Sig:
    data: Dict[str, Any]

    def __iter__(self):  # pragma: no cover - trivial helper
        return iter(self.data)

    def __getitem__(self, key: str) -> Any:  # pragma: no cover - trivial helper
        return self.data[key]

    def get(self, key: str, default: Any = None) -> Any:  # pragma: no cover
        return self.data.get(key, default)


class Pep458Signer(SigningBase):
    """Detached signer aligned with the TUF/PEP 458 metadata format."""

    type = "Pep458Signer"

    # ------------------------------------------------------------------
    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "algs": _ALLOWED_ALGS,
            "canons": _TUF_JSON_CANON,
            "signs": ("bytes", "envelope"),
            "verifies": ("bytes", "envelope"),
            "envelopes": ("mapping",),
            "features": ("detached_only", "multi"),
        }

    # ------------------------------------------------------------------
    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        if canon and canon not in _TUF_JSON_CANON:
            raise ValueError(f"Unsupported canon: {canon}")
        return _canon_tuf_json(env)

    # ------------------------------------------------------------------
    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        method = self._resolve_method(key, alg)
        private_key = self._load_private_key(key, method)

        if method == "ed25519":
            signature = private_key.sign(payload)
        else:
            signature = private_key.sign(
                payload,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

        public_key = private_key.public_key()
        sig_map: Dict[str, Any] = {
            "format": "tuf/pep458",
            "method": method,
            "alg": _alg_from_method(method),
            "keyid": _keyid_for_public_key(public_key, method),
            "sig": _b64(signature),
        }
        return [_Sig(sig_map).data]

    # ------------------------------------------------------------------
    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        require = require or {}
        opts = opts or {}

        allowed_methods: Set[str] = set()
        for item in require.get("algs", _ALLOWED_ALGS):
            try:
                allowed_methods.add(_method_from_alg(str(item)))
            except ValueError:
                continue
        if not allowed_methods:
            allowed_methods = {"ed25519", "rsa-pss-sha256"}

        min_signers = int(require.get("min_signers", 1))
        required_kids = {str(k) for k in require.get("kids", [])}

        pubkeys: List[Any] = []
        for container in (require.get("pubkeys"), opts.get("pubkeys")):
            if not container:
                continue
            for entry in container:  # type: ignore[not-an-iterable]
                parsed = self._coerce_public_key(entry)
                if parsed is not None:
                    pubkeys.append(parsed)

        if not pubkeys:
            return False

        key_ring: Dict[str, Tuple[Any, str]] = {}
        for pub in pubkeys:
            methods = self._methods_for_public_key(pub)
            for method in methods:
                key_ring[_keyid_for_public_key(pub, method)] = (pub, method)

        matched: Set[str] = set()
        for sig in signatures:
            if sig.get("format") != "tuf/pep458":
                continue
            method_label = str(sig.get("method"))
            if method_label not in _SUPPORTED_METHODS:
                continue
            if method_label not in allowed_methods:
                continue

            keyid = str(sig.get("keyid"))
            if required_kids and keyid not in required_kids:
                continue

            entry = key_ring.get(keyid)
            if not entry:
                continue

            public_key, method = entry
            signature_bytes = base64.b64decode(str(sig.get("sig", "")))

            try:
                if method == "ed25519" and isinstance(
                    public_key, ed25519.Ed25519PublicKey
                ):
                    public_key.verify(signature_bytes, payload)
                elif method == "rsa-pss-sha256" and isinstance(
                    public_key, rsa.RSAPublicKey
                ):
                    public_key.verify(
                        signature_bytes,
                        payload,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH,
                        ),
                        hashes.SHA256(),
                    )
                else:
                    continue
            except InvalidSignature:
                continue

            matched.add(keyid)
            if len(matched) >= min_signers:
                return True

        return len(matched) >= min_signers

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
        payload = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self.sign_bytes(key, payload, alg=alg, opts=opts)

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
        payload = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self.verify_bytes(payload, signatures, require=require, opts=opts)

    # ------------------------------------------------------------------
    def _resolve_method(self, key: KeyRef, alg: Optional[Alg]) -> str:
        if alg is not None:
            return _method_from_alg(str(alg))

        if isinstance(key, Mapping):
            if "alg" in key:
                return _method_from_alg(str(key["alg"]))
            if key.get("kty"):
                kty = str(key["kty"]).lower()
                if kty in {"rsa"}:
                    return "rsa-pss-sha256"
                if kty in {"ed25519", "okp"}:
                    return "ed25519"

        return "ed25519"

    # ------------------------------------------------------------------
    def _load_private_key(self, key: KeyRef, method: str):
        if isinstance(key, Mapping):
            kind = key.get("kind")
            if kind == "cryptography_obj":
                return key["obj"]
            if kind == "pem":
                data = key.get("priv")
                if isinstance(data, str):
                    data = data.encode("utf-8")
                return load_pem_private_key(data, password=None)
            if kind == "raw_ed25519_sk" and method == "ed25519":
                seed = key.get("bytes")
                if not isinstance(seed, (bytes, bytearray)):
                    raise TypeError("raw_ed25519_sk expects 'bytes' material")
                return ed25519.Ed25519PrivateKey.from_private_bytes(bytes(seed[:32]))
        raise ValueError("Unsupported KeyRef kind for Pep458Signer")

    # ------------------------------------------------------------------
    def _coerce_public_key(self, value: Any) -> Optional[Any]:
        if value is None:
            return None
        if hasattr(value, "public_bytes") and not isinstance(value, (bytes, str)):
            return value
        if isinstance(value, (bytes, bytearray)):
            return load_pem_public_key(bytes(value))
        if isinstance(value, str):
            return load_pem_public_key(value.encode("utf-8"))
        if isinstance(value, Mapping):
            kind = value.get("kind")
            if kind == "cryptography_obj" and "obj" in value:
                return value["obj"]
            if kind == "pem" and "pub" in value:
                data = value["pub"]
                if isinstance(data, str):
                    data = data.encode("utf-8")
                return load_pem_public_key(data)
        return None

    # ------------------------------------------------------------------
    def _methods_for_public_key(self, pub: Any) -> Tuple[str, ...]:
        if isinstance(pub, ed25519.Ed25519PublicKey):
            return ("ed25519",)
        if isinstance(pub, rsa.RSAPublicKey):
            return ("rsa-pss-sha256",)
        return _SUPPORTED_METHODS


__all__ = ["Pep458Signer"]
