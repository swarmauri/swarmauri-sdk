from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Sequence, Dict

import json
import hashlib
import base64

from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.signing.ISigning import Canon, Envelope
from swarmauri_core.signing.types import Signature
from swarmauri_core.crypto.types import KeyRef, Alg

try:  # pragma: no cover - optional dependency
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import (
        encode_dss_signature,
    )
    from cryptography.hazmat.primitives.serialization import (
        load_pem_private_key,
        load_pem_public_key,
    )
    from cryptography.exceptions import InvalidSignature

    _CRYPTO_OK = True
except Exception:  # pragma: no cover - runtime check
    _CRYPTO_OK = False

try:  # pragma: no cover - optional dependency
    import cbor2

    _CBOR_OK = True
except Exception:  # pragma: no cover - runtime check
    _CBOR_OK = False


def _require_crypto() -> None:
    if not _CRYPTO_OK:
        raise RuntimeError(
            "EcdsaEnvelopeSigner requires 'cryptography'. Install with: pip install cryptography"
        )


def _canon_json(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _canon_cbor(obj: Any) -> bytes:
    if not _CBOR_OK:
        raise RuntimeError("CBOR canonicalization requires 'cbor2'.")
    return cbor2.dumps(obj)


_EC_ALGS = {
    "ECDSA-P256-SHA256": ("ES256", ec.SECP256R1(), hashes.SHA256),
    "ECDSA-P384-SHA384": ("ES384", ec.SECP384R1(), hashes.SHA384),
    "ECDSA-P521-SHA512": ("ES512", ec.SECP521R1(), hashes.SHA512),
}
_ALIAS = {v[0]: k for k, v in _EC_ALGS.items()}


def _select_ec_alg(alg: Optional[str]) -> tuple[str, ec.EllipticCurve, Any]:
    token = alg or "ES256"
    if token in _ALIAS:
        token = _ALIAS[token]
    if token in _EC_ALGS:
        _, curve, hmod = _EC_ALGS[token]
        return token, curve, hmod()
    raise ValueError(
        "Unsupported ECDSA alg '{alg}'. Use one of: "
        f"{', '.join(list(_EC_ALGS.keys()) + list(_ALIAS.keys()))}"
    )


def _keyref_to_ec_private(key: KeyRef) -> ec.EllipticCurvePrivateKey:
    _require_crypto()
    if isinstance(key, dict):
        kind = key.get("kind")
        if kind == "cryptography_obj" and isinstance(
            key.get("obj"), ec.EllipticCurvePrivateKey
        ):
            return key["obj"]  # type: ignore[return-value]
        if kind == "pem":
            data = key.get("priv") or key.get("data")
            if isinstance(data, str):
                data = data.encode("utf-8")
            if not isinstance(data, (bytes, bytearray)):
                raise TypeError("KeyRef 'pem' expects 'priv' or 'data' bytes/str.")
            password = key.get("password")
            if isinstance(password, str):
                password = password.encode("utf-8")
            return load_pem_private_key(data, password=password)
    raise TypeError("Unsupported KeyRef for ECDSA private key.")


def _public_key_id_ec(pk: ec.EllipticCurvePublicKey) -> str:
    spki = pk.public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return hashlib.sha256(spki).hexdigest()


def _b64u_dec(s: str) -> bytes:
    pad = "=" * ((4 - (len(s) % 4)) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _gather_ec_pubkeys(
    opts: Optional[Mapping[str, object]], expected_curve: ec.EllipticCurve
) -> list[ec.EllipticCurvePublicKey]:
    pubs: list[ec.EllipticCurvePublicKey] = []
    if not opts:
        return pubs

    for item in opts.get("pubkeys") or []:  # type: ignore[index]
        if isinstance(item, ec.EllipticCurvePublicKey):
            if item.curve.name != expected_curve.name:
                raise ValueError(
                    f"Curve mismatch: want {expected_curve.name}, got {item.curve.name}"
                )
            pubs.append(item)
        elif isinstance(item, (bytes, bytearray)):
            pk = load_pem_public_key(item)  # type: ignore[arg-type]
            if not isinstance(pk, ec.EllipticCurvePublicKey):
                raise TypeError("PEM is not an EC public key.")
            if pk.curve.name != expected_curve.name:
                raise ValueError(
                    f"Curve mismatch: want {expected_curve.name}, got {pk.curve.name}"
                )
            pubs.append(pk)
        elif isinstance(item, str):
            pk = load_pem_public_key(item.encode("utf-8"))
            if not isinstance(pk, ec.EllipticCurvePublicKey):
                raise TypeError("PEM is not an EC public key.")
            if pk.curve.name != expected_curve.name:
                raise ValueError(
                    f"Curve mismatch: want {expected_curve.name}, got {pk.curve.name}"
                )
            pubs.append(pk)
        elif isinstance(item, dict) and item.get("kty") == "EC":
            crv = item.get("crv")
            jwk_to_curve = {
                "P-256": ec.SECP256R1(),
                "P-384": ec.SECP384R1(),
                "P-521": ec.SECP521R1(),
            }
            if crv not in jwk_to_curve:
                raise ValueError(f"Unsupported JWK 'crv': {crv}")
            if jwk_to_curve[crv].name != expected_curve.name:
                raise ValueError(
                    f"Curve mismatch: want {expected_curve.name}, got {crv}"
                )
            x = int.from_bytes(_b64u_dec(item["x"]), "big")
            y = int.from_bytes(_b64u_dec(item["y"]), "big")
            pn = ec.EllipticCurvePublicNumbers(x, y, expected_curve)
            pubs.append(pn.public_key())
        else:
            raise TypeError("Unsupported entry in opts['pubkeys'] for EC.")
    return pubs


@dataclass(frozen=True)
class _Sig:
    data: Dict[str, Any]

    def __getitem__(self, k: str) -> object:  # pragma: no cover - trivial
        return self.data[k]

    def __iter__(self):  # pragma: no cover - trivial
        return iter(self.data)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.data)

    def get(self, k: str, default: Any = None) -> Any:
        return self.data.get(k, default)


class EcdsaEnvelopeSigner(SigningBase):
    """Detached ECDSA signatures over bytes and envelopes."""

    def supports(self) -> Mapping[str, Iterable[str]]:
        algs = tuple(_EC_ALGS.keys()) + tuple(_ALIAS.keys())
        canons = ("json", "cbor") if _CBOR_OK else ("json",)
        return {
            "algs": algs,
            "canons": canons,
            "signs": ("bytes", "digest", "envelope", "stream"),
            "verifies": ("bytes", "digest", "envelope", "stream"),
            "envelopes": ("mapping",),
            "features": ("multi", "detached_only"),
        }

    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        _require_crypto()
        token, curve, h = _select_ec_alg(alg)
        sk = _keyref_to_ec_private(key)
        if sk.curve.name != curve.name:
            raise ValueError(
                f"Signer curve mismatch: key={sk.curve.name} alg={curve.name}"
            )
        sig_der = sk.sign(payload, ec.ECDSA(h))
        kid = _public_key_id_ec(sk.public_key())
        return [_Sig({"alg": token, "kid": kid, "sig": sig_der, "sigfmt": "DER"})]

    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        _require_crypto()
        min_signers = int((require or {}).get("min_signers", 1))
        allowed_algs = set((require or {}).get("algs", [])) or set(
            self.supports()["algs"]
        )
        accepted = 0

        for sig in signatures:
            alg_token = sig.get("alg")
            if not isinstance(alg_token, str) or alg_token not in allowed_algs:
                continue
            token, curve, h = _select_ec_alg(alg_token)
            pubs = _gather_ec_pubkeys(opts, curve)
            raw = sig.get("sig")
            if not isinstance(raw, (bytes, bytearray)):
                continue

            sig_der = bytes(raw)
            sigfmt = sig.get("sigfmt")
            if sigfmt == "raw" or len(raw) in _raw_lengths_for_curve(curve):
                try:
                    n = (curve.key_size + 7) // 8
                    if len(raw) != 2 * n:
                        raise ValueError
                    r = int.from_bytes(raw[:n], "big")
                    s = int.from_bytes(raw[n:], "big")
                    sig_der = encode_dss_signature(r, s)
                except Exception:
                    sig_der = bytes(raw)

            ok_one = False
            for pk in pubs:
                try:
                    pk.verify(sig_der, payload, ec.ECDSA(h))
                    ok_one = True
                    break
                except InvalidSignature:
                    continue
            if ok_one:
                accepted += 1
            if accepted >= min_signers:
                return True
        return False

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
        alg: Optional[Alg] = None,
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


def _raw_lengths_for_curve(curve: ec.EllipticCurve) -> set[int]:
    n = (curve.key_size + 7) // 8
    return {2 * n}
