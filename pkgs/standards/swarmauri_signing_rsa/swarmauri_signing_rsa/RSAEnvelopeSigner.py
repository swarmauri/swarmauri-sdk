from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Union

from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.signing.ISigning import Canon, Envelope
from swarmauri_core.signing.types import Signature
from swarmauri_core.crypto.types import KeyRef, Alg

try:  # pragma: no cover - optional dependency
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes, serialization
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


# ---------------------------------------------------------------------------
# helpers: canonicalization
# ---------------------------------------------------------------------------


def _canon_json(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _canon_cbor(obj: Any) -> bytes:
    if not _CBOR_OK:
        raise RuntimeError("CBOR canonicalization requires 'cbor2' to be installed.")
    return cbor2.dumps(obj)


# ---------------------------------------------------------------------------
# helpers: JWK <-> ints/bytes
# ---------------------------------------------------------------------------


def _b64u_to_int(s: str) -> int:
    import base64

    pad = "=" * ((4 - len(s) % 4) % 4)
    return int.from_bytes(base64.urlsafe_b64decode((s + pad).encode("ascii")), "big")


def _int_to_b64u(i: int) -> str:  # pragma: no cover - convenience
    import base64

    if i == 0:
        raw = b"\x00"
    else:
        length = (i.bit_length() + 7) // 8
        raw = i.to_bytes(length, "big")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _jwk_thumbprint_sha256(jwk: Mapping[str, Any]) -> str:
    if jwk.get("kty") != "RSA":
        raise ValueError("JWK kty must be 'RSA' for thumbprint.")
    obj = {"e": jwk["e"], "kty": "RSA", "n": jwk["n"]}
    data = json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# helpers: key loading (PEM/JWK)
# ---------------------------------------------------------------------------


def _ensure_crypto() -> None:
    if not _CRYPTO_OK:
        raise RuntimeError(
            "RSAEnvelopeSigner requires 'cryptography'. Install with: pip install cryptography"
        )


def _load_private_from_pem(
    pem_bytes: bytes, passphrase: Optional[Union[str, bytes]]
) -> rsa.RSAPrivateKey:
    _ensure_crypto()
    pw = None
    if isinstance(passphrase, str):
        pw = passphrase.encode("utf-8")
    elif isinstance(passphrase, (bytes, bytearray)):
        pw = bytes(passphrase)
    return load_pem_private_key(pem_bytes, password=pw)


def _load_public_from_pem(pem_bytes: bytes) -> rsa.RSAPublicKey:
    _ensure_crypto()
    pub = load_pem_public_key(pem_bytes)
    if not isinstance(pub, rsa.RSAPublicKey):
        raise TypeError("PEM public key is not RSA.")
    return pub


def _private_from_jwk(jwk: Mapping[str, Any]) -> rsa.RSAPrivateKey:
    _ensure_crypto()
    if jwk.get("kty") != "RSA":
        raise ValueError("JWK kty must be 'RSA' for RSA signing.")
    n = _b64u_to_int(jwk["n"])
    e = _b64u_to_int(jwk["e"])
    d = _b64u_to_int(jwk["d"])
    p = _b64u_to_int(jwk["p"]) if "p" in jwk else None
    q = _b64u_to_int(jwk["q"]) if "q" in jwk else None
    dp = _b64u_to_int(jwk["dp"]) if "dp" in jwk else None
    dq = _b64u_to_int(jwk["dq"]) if "dq" in jwk else None
    qi = _b64u_to_int(jwk["qi"]) if "qi" in jwk else None

    pub_numbers = rsa.RSAPublicNumbers(e=e, n=n)
    if all(v is not None for v in (p, q, dp, dq, qi)):
        priv_numbers = rsa.RSAPrivateNumbers(
            p=p, q=q, d=d, dmp1=dp, dmq1=dq, iqmp=qi, public_numbers=pub_numbers
        )
    else:
        raise ValueError("RSA private JWK must include CRT params: p,q,dp,dq,qi")
    return priv_numbers.private_key()


def _public_from_jwk(jwk: Mapping[str, Any]) -> rsa.RSAPublicKey:
    _ensure_crypto()
    if jwk.get("kty") != "RSA":
        raise ValueError("JWK kty must be 'RSA'.")
    n = _b64u_to_int(jwk["n"])
    e = _b64u_to_int(jwk["e"])
    return rsa.RSAPublicNumbers(e=e, n=n).public_key()


def _keyref_to_private(
    key: KeyRef, passphrase: Optional[Union[str, bytes]]
) -> rsa.RSAPrivateKey:
    _ensure_crypto()
    if isinstance(key, dict):
        k = key.get("kind")
        if k == "cryptography_obj" and isinstance(key.get("obj"), rsa.RSAPrivateKey):
            return key["obj"]  # type: ignore[return-value]
        if k == "pem_priv":
            data = key.get("data")
            if isinstance(data, str):
                data = data.encode("utf-8")
            if not isinstance(data, (bytes, bytearray)):
                raise TypeError("pem_priv KeyRef requires 'data' as bytes/str.")
            return _load_private_from_pem(bytes(data), passphrase)
        if k == "pem_priv_path":
            path = key.get("path")
            if not isinstance(path, str):
                raise TypeError("pem_priv_path KeyRef requires 'path' string.")
            with open(path, "rb") as f:
                return _load_private_from_pem(f.read(), passphrase)
        if k == "jwk_priv":
            jwk = key.get("jwk")
            if not isinstance(jwk, Mapping):
                raise TypeError("jwk_priv KeyRef requires 'jwk' mapping.")
            return _private_from_jwk(jwk)
    raise TypeError("Unsupported KeyRef for RSA private key.")


def _keyref_to_public(key: Any) -> rsa.RSAPublicKey:
    _ensure_crypto()
    if isinstance(key, dict):
        k = key.get("kind")
        if k == "cryptography_obj" and isinstance(key.get("obj"), rsa.RSAPublicKey):
            return key["obj"]  # type: ignore[return-value]
        if k == "pem_pub":
            data = key.get("data")
            if isinstance(data, str):
                data = data.encode("utf-8")
            return _load_public_from_pem(bytes(data))
        if k == "pem_pub_path":
            path = key.get("path")
            with open(path, "rb") as f:
                return _load_public_from_pem(f.read())
        if k == "jwk_pub":
            jwk = key.get("jwk")
            if not isinstance(jwk, Mapping):
                raise TypeError("jwk_pub requires 'jwk' mapping.")
            return _public_from_jwk(jwk)
        if key.get("kty") == "RSA" and "n" in key and "e" in key:
            return _public_from_jwk(key)
    elif isinstance(key, (bytes, bytearray, str)):
        data = key.encode("utf-8") if isinstance(key, str) else bytes(key)
        try:
            return _load_public_from_pem(data)
        except Exception as e:  # pragma: no cover - invalid format
            raise TypeError(
                "bytes/str given to _keyref_to_public is not a valid PEM public key."
            ) from e
    raise TypeError("Unsupported verification key format for RSA.")


def _kid_from_public(
    pk: rsa.RSAPublicKey, jwk_hint: Optional[Mapping[str, Any]] = None
) -> str:
    try:
        if jwk_hint and jwk_hint.get("kty") == "RSA":
            return _jwk_thumbprint_sha256(jwk_hint)
    except Exception:  # pragma: no cover - thumbprint failure
        pass
    spki = pk.public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return hashlib.sha256(spki).hexdigest()


@dataclass(frozen=True)
class _Sig:  # pragma: no cover - mapping proxy
    data: Dict[str, Any]

    def __getitem__(self, k: str) -> object:
        return self.data[k]

    def __iter__(self):  # pragma: no cover - trivial
        return iter(self.data)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.data)

    def get(self, k: str, default: Any = None) -> Any:
        return self.data.get(k, default)


class RSAEnvelopeSigner(SigningBase):
    """RSA detached signer for bytes and canonicalized envelopes."""

    def supports(self) -> Mapping[str, Iterable[str]]:
        algs = ("RSA-PSS-SHA256", "RS256")
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
        _ensure_crypto()
        alg = alg or "RSA-PSS-SHA256"
        sk = _keyref_to_private(key, passphrase=(opts or {}).get("passphrase"))
        pk = sk.public_key()
        if alg == "RSA-PSS-SHA256":
            sig = sk.sign(
                payload,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
        elif alg == "RS256":
            sig = sk.sign(payload, padding.PKCS1v15(), hashes.SHA256())
        else:
            raise ValueError(
                "Unsupported alg for RSAEnvelopeSigner. Use 'RSA-PSS-SHA256' or 'RS256'."
            )

        jwk_hint = (
            (opts or {}).get("kid_jwk_hint") if isinstance(opts, Mapping) else None
        )
        kid = _kid_from_public(pk, jwk_hint if isinstance(jwk_hint, Mapping) else None)
        return [_Sig({"alg": str(alg), "kid": kid, "sig": sig})]

    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        _ensure_crypto()
        min_signers = int((require or {}).get("min_signers", 1))
        allowed_algs = set((require or {}).get("algs", ("RSA-PSS-SHA256", "RS256")))

        pubs: list[rsa.RSAPublicKey] = []
        if opts and "pubkeys" in opts:
            for entry in opts["pubkeys"]:  # type: ignore[index]
                pubs.append(_keyref_to_public(entry))
        else:
            raise ValueError(
                "RSAEnvelopeSigner.verify_bytes requires opts['pubkeys'] with one or more RSA public keys."
            )

        accepted = 0
        for sig in signatures:
            alg = sig.get("alg")
            if not isinstance(alg, str) or alg not in allowed_algs:
                continue
            sig_bytes = sig.get("sig")
            if not isinstance(sig_bytes, (bytes, bytearray)):
                continue

            verified = False
            for pk in pubs:
                try:
                    if alg == "RSA-PSS-SHA256":
                        pk.verify(
                            sig_bytes,
                            payload,
                            padding.PSS(
                                mgf=padding.MGF1(hashes.SHA256()),
                                salt_length=padding.PSS.MAX_LENGTH,
                            ),
                            hashes.SHA256(),
                        )
                    else:  # RS256
                        pk.verify(
                            sig_bytes, payload, padding.PKCS1v15(), hashes.SHA256()
                        )
                    verified = True
                    break
                except InvalidSignature:
                    continue

            if verified:
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
        alg: Optional[Alg] = None,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        payload = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self.sign_bytes(
            key, payload, alg=alg or "RSA-PSS-SHA256", opts=opts
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
        payload = await self.canonicalize_envelope(env, canon=canon, opts=opts)
        return await self.verify_bytes(payload, signatures, require=require, opts=opts)
