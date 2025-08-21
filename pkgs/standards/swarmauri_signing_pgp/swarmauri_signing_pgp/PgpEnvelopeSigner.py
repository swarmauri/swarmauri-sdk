from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.signing.ISigning import Canon, Envelope, Signature

try:  # pragma: no cover - optional dependency
    import pgpy

    _PGP_OK = True
except Exception:  # pragma: no cover - import guard
    _PGP_OK = False

try:  # pragma: no cover - optional dependency
    import cbor2

    _CBOR_OK = True
except Exception:  # pragma: no cover - import guard
    _CBOR_OK = False


def _ensure_pgpy() -> None:
    if not _PGP_OK:  # pragma: no cover - runtime guard
        raise RuntimeError(
            "PgpEnvelopeSigner requires 'PGPy'. Install with: pip install pgpy"
        )


def _canon_json(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _canon_cbor(obj: Any) -> bytes:
    if not _CBOR_OK:  # pragma: no cover - runtime guard
        raise RuntimeError("CBOR canonicalization requires 'cbor2' to be installed.")
    return cbor2.dumps(obj)


@dataclass(frozen=True)
class _Sig:
    data: Dict[str, Any]

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)


class PgpEnvelopeSigner(SigningBase):
    """Detached OpenPGP signatures over bytes or canonicalized envelopes."""

    type: str = "PgpEnvelopeSigner"

    def supports(self) -> Mapping[str, Iterable[str]]:
        canons = ("json", "cbor") if _CBOR_OK else ("json",)
        return {
            "algs": ("OpenPGP",),
            "canons": canons,
            "features": ("multi", "detached_only"),
        }

    # ------------------------------------------------------------------
    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        _ensure_pgpy()
        if alg not in (None, "OpenPGP"):
            raise ValueError("Unsupported alg for PgpEnvelopeSigner.")

        k = self._load_private_key(key, opts)
        must_unlock = getattr(k, "is_unlocked", True) is False
        if must_unlock:
            pw = (opts or {}).get("passphrase")
            if not isinstance(pw, (str, bytes)):
                raise RuntimeError(
                    "PGP private key is locked; supply opts['passphrase']."
                )
            k.unlock(pw)  # pragma: no cover - password path

        sig = k.sign(payload, detached=True)
        kid = str(k.fingerprint)
        sig_bytes = bytes(sig.__bytes__())
        sig_asc = str(sig)
        return [
            _Sig({"alg": "OpenPGP", "kid": kid, "sig": sig_bytes, "armored": sig_asc})
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
        _ensure_pgpy()
        min_signers = int(require.get("min_signers", 1)) if require else 1

        pubkeys = []
        if opts and "pubkeys" in opts:
            for entry in opts["pubkeys"]:  # type: ignore[index]
                if isinstance(entry, pgpy.PGPKey):
                    pubkeys.append(entry)
                elif isinstance(entry, str):
                    pubkeys.append(pgpy.PGPKey.from_blob(entry)[0])
                else:
                    raise TypeError("Unsupported public key in opts['pubkeys'].")

        accepted = 0
        for sig in signatures:
            if sig.get("alg") != "OpenPGP":
                continue
            sig_bytes = sig.get("sig")
            sig_arm = sig.get("armored")
            if isinstance(sig_bytes, (bytes, bytearray)):
                s = pgpy.PGPSignature.from_blob(bytes(sig_bytes))
            elif isinstance(sig_arm, str):
                s = pgpy.PGPSignature.from_blob(sig_arm)
            else:
                continue

            ok_one = False
            for pk in pubkeys:
                if pk.verify(payload, s):
                    ok_one = True
                    break
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
        return await self.sign_bytes(key, payload, alg="OpenPGP", opts=opts)

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
    def _load_private_key(self, key: KeyRef, opts: Optional[Mapping[str, object]]):
        if isinstance(key, dict):
            kind = key.get("kind")
            if kind == "pgpy_key" and isinstance(key.get("priv"), pgpy.PGPKey):
                return key["priv"]
            if kind == "pgpy_key_armored" and isinstance(key.get("priv"), str):
                k, _ = pgpy.PGPKey.from_blob(key["priv"])
                return k
        raise TypeError("Unsupported KeyRef for PgpEnvelopeSigner private key.")
