from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

from cryptography.hazmat.primitives import serialization


from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.signing.ISigning import Canon, Envelope
from swarmauri_core.signing.types import Signature
from swarmauri_core.crypto.types import KeyRef, Alg

try:  # pragma: no cover - optional dependency
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.exceptions import InvalidSignature

    _CRYPTOGRAPHY_OK = True
except Exception:  # pragma: no cover - runtime check
    _CRYPTOGRAPHY_OK = False

try:  # pragma: no cover - optional dependency
    import cbor2

    _CBOR_OK = True
except Exception:  # pragma: no cover - runtime check
    _CBOR_OK = False


# ---------- helpers ----------
def _canon_json(obj: Any) -> bytes:
    """Deterministic JSON canonicalization."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _canon_cbor(obj: Any) -> bytes:
    if not _CBOR_OK:
        raise RuntimeError("CBOR canonicalization requires 'cbor2'.")
    return cbor2.dumps(obj)


def _ensure_crypto() -> None:
    if not _CRYPTOGRAPHY_OK:
        raise RuntimeError(
            "Ed25519EnvelopeSigner requires 'cryptography'. Install with: pip install cryptography"
        )


def _keyref_to_private(key: KeyRef) -> Ed25519PrivateKey:
    _ensure_crypto()
    if isinstance(key, dict):
        kind = key.get("kind")
        if kind == "cryptography_obj" and isinstance(key.get("obj"), Ed25519PrivateKey):
            return key["obj"]  # type: ignore[return-value]
        if kind == "raw_ed25519_sk":
            data = key.get("bytes")
            if not isinstance(data, (bytes, bytearray)):
                raise TypeError("raw_ed25519_sk expects 'bytes' field with key seed.")
            if len(data) == 32:
                return Ed25519PrivateKey.from_private_bytes(bytes(data))
            if len(data) == 64:
                return Ed25519PrivateKey.from_private_bytes(bytes(data[:32]))
            raise ValueError(
                "Unsupported Ed25519 private key length; expected 32 or 64 bytes."
            )
    raise TypeError("Unsupported KeyRef for Ed25519 private key.")


def _keyref_to_public_from_private(sk: Ed25519PrivateKey) -> Ed25519PublicKey:
    return sk.public_key()




def _keyid_from_public(pk: Ed25519PublicKey) -> str:
    raw = pk.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class _Sig:
    data: Dict[str, Any]

    def __getitem__(self, k: str) -> object:
        return self.data[k]

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.data)

    def get(self, k: str, default: Any = None) -> Any:
        return self.data.get(k, default)


class Ed25519EnvelopeSigner(SigningBase):
    """Detached signatures over bytes and envelopes using Ed25519."""

    # ------------------------------------------------------------------
    def supports(self) -> Mapping[str, Iterable[str]]:
        algs = ("Ed25519",)
        canons = ("json", "cbor") if _CBOR_OK else ("json",)
        return {"algs": algs, "canons": canons, "features": ("multi", "detached_only")}

    # ------------------------------------------------------------------
    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        _ensure_crypto()
        if alg not in (None, "Ed25519"):
            raise ValueError("Unsupported alg for Ed25519EnvelopeSigner.")
        sk = _keyref_to_private(key)
        sig = sk.sign(payload)
        kid = _keyid_from_public(_keyref_to_public_from_private(sk))
        return [_Sig({"alg": "Ed25519", "kid": kid, "sig": sig})]

    # ------------------------------------------------------------------
    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        _ensure_crypto()
        min_signers = int(require.get("min_signers", 1)) if require else 1
        accepted = 0

        pubs: list[Ed25519PublicKey] = []
        if opts and "pubkeys" in opts:
            for item in opts["pubkeys"]:  # type: ignore[index]
                if _CRYPTOGRAPHY_OK and isinstance(item, Ed25519PublicKey):
                    pubs.append(item)
                elif isinstance(item, (bytes, bytearray)) and len(item) == 32:
                    pubs.append(Ed25519PublicKey.from_public_bytes(bytes(item)))
                elif (
                    isinstance(item, dict)
                    and item.get("kind") == "cryptography_obj"
                    and isinstance(item.get("obj"), Ed25519PublicKey)
                ):
                    pubs.append(item["obj"])
                else:
                    raise TypeError("Unsupported public key entry in opts['pubkeys'].")

        for sig in signatures:
            if sig.get("alg") != "Ed25519":
                continue
            sig_bytes = sig.get("sig")
            if not isinstance(sig_bytes, (bytes, bytearray)):
                continue
            ok_one = False
            for pk in pubs:
                try:
                    pk.verify(sig_bytes, payload)
                    ok_one = True
                    break
                except InvalidSignature:
                    continue
            if ok_one:
                accepted += 1
            if accepted >= min_signers:
                return True
        return False

    # ------------------------------------------------------------------
    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        if canon in (None, "json"):
            return _canon_json(env)  # type: ignore[arg-type]
        if canon == "cbor":
            return _canon_cbor(env)  # type: ignore[arg-type]
        raise ValueError(f"Unsupported canon: {canon}")

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
        return await self.sign_bytes(key, payload, alg="Ed25519", opts=opts)

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
