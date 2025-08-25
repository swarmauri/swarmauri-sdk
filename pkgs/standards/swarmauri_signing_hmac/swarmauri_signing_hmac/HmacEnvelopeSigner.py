from __future__ import annotations

import hmac
import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Sequence

from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.signing.ISigning import Signature, Envelope, Canon
from swarmauri_core.crypto.types import JWAAlg, KeyRef

try:  # pragma: no cover - optional canonicalization
    import cbor2

    _CBOR_OK = True
except Exception:  # pragma: no cover - runtime check
    _CBOR_OK = False


# ---------- helpers ----------


def _canon_json(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _canon_cbor(obj: Any) -> bytes:
    if not _CBOR_OK:
        raise RuntimeError(
            "CBOR canonicalization requires 'cbor2'. Install with: pip install cbor2"
        )
    return cbor2.dumps(obj)


def _alg_to_hash(alg: JWAAlg):
    table = {
        JWAAlg.HS256: hashlib.sha256,
        JWAAlg.HS384: hashlib.sha384,
        JWAAlg.HS512: hashlib.sha512,
    }
    if alg not in table:
        raise ValueError(
            f"Unsupported HMAC alg '{alg}'. Use one of: {', '.join(a.value for a in table)}"
        )
    return table[alg]


def _ensure_bytes(b: Any, *, name: str) -> bytes:
    if isinstance(b, (bytes, bytearray)):
        return bytes(b)
    if isinstance(b, str):
        return b.encode("utf-8")
    raise TypeError(f"{name} must be bytes or str")


def _hkdf(
    ikm: bytes,
    *,
    salt: Optional[bytes],
    info: Optional[bytes],
    hash_ctor,
) -> bytes:
    salt = salt or b"\x00" * hash_ctor().digest_size
    prk = hmac.new(salt, ikm, hash_ctor).digest()
    info = info or b""
    t1 = hmac.new(prk, info + b"\x01", hash_ctor).digest()
    return t1


def _fingerprint_key(secret: bytes, hash_ctor) -> str:
    return hash_ctor(secret).hexdigest()


def _resolve_secret(key: KeyRef, *, hash_ctor) -> tuple[bytes, str]:
    if not isinstance(key, dict):
        raise TypeError("HMAC KeyRef must be a dict")

    kind = key.get("kind")
    if kind == "raw":
        secret = _ensure_bytes(key.get("key"), name="key")
    elif kind == "hex":
        secret = bytes.fromhex(str(key.get("key", "")))
    elif kind == "env":
        name = key.get("name")
        if not isinstance(name, str):
            raise TypeError("KeyRef 'env' requires a 'name' string")
        val = os.environ.get(name)
        if val is None:
            raise RuntimeError(f"Environment variable '{name}' is not set")
        secret = _ensure_bytes(val, name="env value")
    elif kind == "derived":
        ikm = _ensure_bytes(key.get("key"), name="key")
        hkdf_cfg = key.get("hkdf", {}) or {}
        salt = hkdf_cfg.get("salt")
        info = hkdf_cfg.get("info")
        salt_b = None if salt is None else _ensure_bytes(salt, name="hkdf.salt")
        info_b = None if info is None else _ensure_bytes(info, name="hkdf.info")
        secret = _hkdf(ikm, salt=salt_b, info=info_b, hash_ctor=hash_ctor)
    else:
        raise TypeError(f"Unsupported HMAC KeyRef kind '{kind}'")

    kid = key.get("kid")
    if isinstance(kid, str) and kid:
        return secret, kid
    return secret, _fingerprint_key(secret, hash_ctor)


@dataclass(frozen=True)
class _Sig:
    data: dict[str, Any]

    def __getitem__(self, k: str) -> object:  # pragma: no cover - trivial
        return self.data[k]

    def __iter__(self):  # pragma: no cover - trivial
        return iter(self.data)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.data)

    def get(self, k: str, default: Any = None) -> Any:
        return self.data.get(k, default)


class HmacEnvelopeSigner(SigningBase):
    """Detached HMAC signatures over bytes and canonicalized envelopes."""

    def supports(self) -> Mapping[str, Iterable[JWAAlg]]:
        canons = ("json", "cbor") if _CBOR_OK else ("json",)
        return {
            "algs": (JWAAlg.HS256, JWAAlg.HS384, JWAAlg.HS512),
            "canons": canons,
            "features": ("multi", "detached_only"),
        }

    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[JWAAlg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        alg_token = alg or JWAAlg.HS256
        hash_ctor = _alg_to_hash(alg_token)
        secret, kid = _resolve_secret(key, hash_ctor=hash_ctor)
        mac = hmac.new(secret, payload, hash_ctor).digest()
        return [_Sig({"alg": alg_token.value, "kid": kid, "sig": mac})]

    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        req = require or {}
        allowed_algs = {
            (a if isinstance(a, JWAAlg) else JWAAlg(a))
            for a in (req.get("algs") or [JWAAlg.HS256, JWAAlg.HS384, JWAAlg.HS512])
        }
        min_signers = int(req.get("min_signers", 1))
        required_kids = set(req.get("kids") or [])

        keys: list[tuple[JWAAlg, str, bytes]] = []
        key_entries = (opts or {}).get("keys") or []
        if not isinstance(key_entries, (list, tuple)) or not key_entries:
            raise RuntimeError(
                "HMAC verification requires opts['keys'] with one or more KeyRef entries."
            )
        for entry in key_entries:  # type: ignore[assignment]
            prefer_alg: Optional[JWAAlg] = None
            if isinstance(entry, dict) and "alg" in entry and entry["alg"] is not None:
                prefer_alg = (
                    entry["alg"]
                    if isinstance(entry["alg"], JWAAlg)
                    else JWAAlg(entry["alg"])
                )
            alg_for_key = prefer_alg or JWAAlg.HS256
            hash_ctor = _alg_to_hash(alg_for_key)
            secret, kid = _resolve_secret(entry, hash_ctor=hash_ctor)
            keys.append((kid, secret))

        accepted = 0
        for sig in signatures:
            sig_alg = sig.get("alg")
            try:
                sig_alg_enum = JWAAlg(sig_alg)
            except Exception:
                continue
            if sig_alg_enum not in allowed_algs:
                continue
            sig_bytes = sig.get("sig")
            if not isinstance(sig_bytes, (bytes, bytearray)):
                continue
            sig_kid = sig.get("kid")
            if required_kids and (
                not isinstance(sig_kid, str) or sig_kid not in required_kids
            ):
                continue

            hash_ctor = _alg_to_hash(sig_alg_enum)
            ok_one = False
            iter_keys = keys
            if isinstance(sig_kid, str):
                iter_keys = [k for k in keys if k[0] == sig_kid] or keys

            for _, secret in iter_keys:
                calc = hmac.new(secret, payload, hash_ctor).digest()
                if hmac.compare_digest(calc, bytes(sig_bytes)):
                    ok_one = True
                    break

            if ok_one:
                accepted += 1
                if accepted >= min_signers:
                    return True

        return False

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

    async def sign_envelope(
        self,
        key: KeyRef,
        env: Envelope,
        *,
        alg: Optional[JWAAlg] = None,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        payload = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self.sign_bytes(key, payload, alg=alg, opts=opts)

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
