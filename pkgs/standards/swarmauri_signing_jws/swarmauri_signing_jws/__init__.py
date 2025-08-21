from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple, Union

from swarmauri_signing_hmac import HmacEnvelopeSigner
from swarmauri_signing_rsa import RSAEnvelopeSigner
from swarmauri_signing_ecdsa import EcdsaEnvelopeSigner
from swarmauri_signing_ed25519 import Ed25519EnvelopeSigner

try:  # optional secp256k1
    from swarmauri_signing_secp256k1 import Secp256k1EnvelopeSigner

    _HAS_K1 = True
except Exception:  # pragma: no cover - optional dependency
    _HAS_K1 = False

try:  # ECDSA DER<->raw conversion
    from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

    _CRYPTO_OK = True
except Exception:  # pragma: no cover - cryptography missing
    _CRYPTO_OK = False


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64u_dec(s: str) -> bytes:
    pad = "=" * ((4 - (len(s) % 4)) % 4)
    return base64.urlsafe_b64decode(s + pad)


_ECDSA_RAW_LEN = {"ES256": 32 * 2, "ES384": 48 * 2, "ES512": 66 * 2}


def _ecdsa_der_to_raw(sig_der: bytes, alg: str) -> bytes:
    if not _CRYPTO_OK:  # pragma: no cover - defensive
        raise RuntimeError("cryptography is required for ECDSA DER→raw conversion")
    r, s = decode_dss_signature(sig_der)
    n = _ECDSA_RAW_LEN[alg] // 2
    return r.to_bytes(n, "big") + s.to_bytes(n, "big")


def _jwk_to_pub_for_signer(jwk: Mapping[str, Any]) -> Any:
    kty = jwk.get("kty")
    if kty == "RSA":
        return jwk
    if kty == "EC":
        return jwk
    if kty == "OKP" and jwk.get("crv") == "Ed25519":
        x = jwk.get("x")
        if not isinstance(x, str):
            raise ValueError("Invalid Ed25519 JWK")
        return _b64u_dec(x)
    if kty == "oct":
        k = jwk.get("k")
        if not isinstance(k, str):
            raise ValueError("Invalid oct JWK")
        return _b64u_dec(k)
    raise ValueError(f"Unsupported JWK kty: {kty}")


_RSA_RS = {
    "RS256": "RSA-PKCS1v15-SHA256",
    "RS384": "RSA-PKCS1v15-SHA384",
    "RS512": "RSA-PKCS1v15-SHA512",
}
_RSA_PS = {
    "PS256": "RSA-PSS-SHA256",
    "PS384": "RSA-PSS-SHA384",
    "PS512": "RSA-PSS-SHA512",
}
_EC_SET = {"ES256", "ES384", "ES512"}
_K1_SET = {"ES256K"}
_HS_SET = {"HS256", "HS384", "HS512"}
_EDDSA = "EdDSA"


def _is_rsa(alg: str) -> bool:
    return alg in _RSA_RS or alg in _RSA_PS


def _is_ec(alg: str) -> bool:
    return alg in _EC_SET


def _is_k1(alg: str) -> bool:
    return alg in _K1_SET


def _is_hmac(alg: str) -> bool:
    return alg in _HS_SET


def _is_eddsa(alg: str) -> bool:
    return alg == _EDDSA


JWSCompact = str


@dataclass
class JwsResult:
    header: Dict[str, Any]
    payload: bytes


class JwsSignerVerifier:
    """Composite JWS signer/verifier supporting multiple algorithms."""

    def __init__(
        self,
        *,
        hmac_signer: Optional[HmacEnvelopeSigner] = None,
        rsa_signer: Optional[RSAEnvelopeSigner] = None,
        ecdsa_signer: Optional[EcdsaEnvelopeSigner] = None,
        eddsa_signer: Optional[Ed25519EnvelopeSigner] = None,
        k1_signer: Optional[Any] = None,
    ) -> None:
        self.hmac = hmac_signer or HmacEnvelopeSigner()
        self.rsa = rsa_signer or RSAEnvelopeSigner()
        self.ecdsa = ecdsa_signer or EcdsaEnvelopeSigner()
        self.eddsa = eddsa_signer or Ed25519EnvelopeSigner()
        self.k1 = k1_signer or (Secp256k1EnvelopeSigner() if _HAS_K1 else None)

    async def sign_compact(
        self,
        *,
        payload: Union[bytes, str, Mapping[str, Any]],
        alg: str,
        key: Mapping[str, Any],
        kid: Optional[str] = None,
        header_extra: Optional[Mapping[str, Any]] = None,
        typ: Optional[str] = None,
    ) -> JWSCompact:
        if isinstance(payload, str):
            payload_b = payload.encode("utf-8")
        elif isinstance(payload, (bytes, bytearray)):
            payload_b = bytes(payload)
        else:
            payload_b = json.dumps(
                payload, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")

        header: Dict[str, Any] = {"alg": alg}
        if kid:
            header["kid"] = kid
        if typ:
            header["typ"] = typ
        if header_extra:
            header.update(dict(header_extra))

        b64 = header.get("b64", True)
        if not b64 and "b64" not in header.get("crit", []):
            raise ValueError("'b64': false requires 'b64' in 'crit'")

        b64_header = _b64u(
            json.dumps(header, separators=(",", ":"), ensure_ascii=False).encode(
                "utf-8"
            )
        )
        if b64:
            b64_payload = _b64u(payload_b)
            signing_input = f"{b64_header}.{b64_payload}".encode("ascii")
        else:
            if isinstance(payload_b, bytes):
                payload_part = payload_b.decode("utf-8")
            else:  # pragma: no cover - impossible
                payload_part = payload_b
            b64_payload = payload_part
            signing_input = f"{b64_header}.{b64_payload}".encode("utf-8")

        sig_bytes = await self._sign_for_alg(signing_input, alg, key)
        b64sig = _b64u(sig_bytes)
        return f"{b64_header}.{b64_payload}.{b64sig}"

    async def verify_compact(
        self,
        jws: JWSCompact,
        *,
        hmac_keys: Optional[Sequence[Mapping[str, Any]]] = None,
        rsa_pubkeys: Optional[Sequence[Any]] = None,
        ec_pubkeys: Optional[Sequence[Any]] = None,
        ed_pubkeys: Optional[Sequence[Any]] = None,
        k1_pubkeys: Optional[Sequence[Any]] = None,
        jwks_resolver: Optional[callable] = None,
        alg_allowlist: Optional[Iterable[str]] = None,
    ) -> JwsResult:
        parts = jws.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWS compact serialization.")
        b64_header, payload_part, b64_sig = parts
        try:
            header = json.loads(_b64u_dec(b64_header))
        except Exception as exc:
            raise ValueError(f"Invalid JWS header: {exc}")
        alg = header.get("alg")
        kid = header.get("kid")
        if not isinstance(alg, str):
            raise ValueError("Missing/invalid 'alg' in JWS header.")
        if alg_allowlist and alg not in set(alg_allowlist):
            raise ValueError(f"Rejected alg '{alg}' (not in allowlist).")

        b64 = header.get("b64", True)
        if not b64 and "b64" not in header.get("crit", []):
            raise ValueError("'b64': false requires 'b64' in 'crit'")

        if b64:
            payload_b = _b64u_dec(payload_part)
            signing_input = f"{b64_header}.{payload_part}".encode("ascii")
        else:
            payload_b = payload_part.encode("utf-8")
            signing_input = f"{b64_header}.{payload_part}".encode("utf-8")

        sig = _b64u_dec(b64_sig)

        if jwks_resolver:
            jwk = jwks_resolver(kid, alg)
            if _is_hmac(alg):
                ok = await self.hmac.verify_bytes(
                    signing_input,
                    [{"alg": alg, "sig": sig}],
                    require={"min_signers": 1, "algs": [alg], "kids": set()},
                    opts={
                        "keys": [{"kind": "raw", "key": _jwk_to_pub_for_signer(jwk)}]
                    },
                )
            elif _is_rsa(alg):
                ok = await self.rsa.verify_bytes(
                    signing_input,
                    [{"alg": _map_rsa_alg(alg), "sig": sig}],
                    require={"min_signers": 1, "algs": [_map_rsa_alg(alg)]},
                    opts={"pubkeys": [_jwk_to_pub_for_signer(jwk)]},
                )
            elif _is_ec(alg):
                ok = await self.ecdsa.verify_bytes(
                    signing_input,
                    [{"alg": alg, "sig": sig, "sigfmt": "raw"}],
                    require={"min_signers": 1, "algs": [alg]},
                    opts={"pubkeys": [_jwk_to_pub_for_signer(jwk)]},
                )
            elif _is_k1(alg):
                if not self.k1:
                    raise ValueError(
                        "ES256K requested but secp256k1 signer is not available"
                    )
                ok = await self.k1.verify_bytes(
                    signing_input,
                    [{"alg": alg, "sig": sig, "sigfmt": "raw"}],
                    require={"min_signers": 1, "algs": [alg]},
                    opts={"pubkeys": [_jwk_to_pub_for_signer(jwk)]},
                )
            elif _is_eddsa(alg):
                ok = await self.eddsa.verify_bytes(
                    signing_input,
                    [{"alg": "Ed25519", "sig": sig}],
                    require={"min_signers": 1, "algs": ["Ed25519"]},
                    opts={"pubkeys": [_jwk_to_pub_for_signer(jwk)]},
                )
            else:
                raise ValueError(f"Unsupported alg: {alg}")
            if not ok:
                raise ValueError("Invalid JWS signature.")
            return JwsResult(header=header, payload=payload_b)

        if _is_hmac(alg):
            keys = hmac_keys or []
            if not keys:
                raise ValueError("No HMAC keys provided.")
            ok = await self.hmac.verify_bytes(
                signing_input,
                [{"alg": alg, "sig": sig}],
                require={"min_signers": 1, "algs": [alg]},
                opts={"keys": list(keys)},
            )
            if not ok:
                raise ValueError("Invalid JWS (HMAC) signature.")
            return JwsResult(header=header, payload=payload_b)

        if _is_rsa(alg):
            if not rsa_pubkeys:
                raise ValueError("No RSA public keys provided.")
            ok = await self.rsa.verify_bytes(
                signing_input,
                [{"alg": _map_rsa_alg(alg), "sig": sig}],
                require={"min_signers": 1, "algs": [_map_rsa_alg(alg)]},
                opts={"pubkeys": list(rsa_pubkeys)},
            )
            if not ok:
                raise ValueError("Invalid JWS (RSA) signature.")
            return JwsResult(header=header, payload=payload_b)

        if _is_ec(alg):
            if not ec_pubkeys:
                raise ValueError("No EC public keys provided.")
            ok = await self.ecdsa.verify_bytes(
                signing_input,
                [{"alg": alg, "sig": sig, "sigfmt": "raw"}],
                require={"min_signers": 1, "algs": [alg]},
                opts={"pubkeys": list(ec_pubkeys)},
            )
            if not ok:
                raise ValueError("Invalid JWS (ECDSA) signature.")
            return JwsResult(header=header, payload=payload_b)

        if _is_k1(alg):
            if not self.k1:
                raise ValueError(
                    "ES256K requested but secp256k1 signer is not available"
                )
            if not k1_pubkeys:
                raise ValueError("No secp256k1 public keys provided.")
            ok = await self.k1.verify_bytes(
                signing_input,
                [{"alg": "ES256K", "sig": sig, "sigfmt": "raw"}],
                require={"min_signers": 1, "algs": ["ES256K"]},
                opts={"pubkeys": list(k1_pubkeys)},
            )
            if not ok:
                raise ValueError("Invalid JWS (ES256K) signature.")
            return JwsResult(header=header, payload=payload_b)

        if _is_eddsa(alg):
            pubs = []
            for x in ed_pubkeys or []:
                if isinstance(x, dict) and x.get("kty") == "OKP":
                    pubs.append(_jwk_to_pub_for_signer(x))
                else:
                    pubs.append(x)
            if not pubs:
                raise ValueError("No Ed25519 public keys provided.")
            ok = await self.eddsa.verify_bytes(
                signing_input,
                [{"alg": "Ed25519", "sig": sig}],
                require={"min_signers": 1, "algs": ["Ed25519"]},
                opts={"pubkeys": pubs},
            )
            if not ok:
                raise ValueError("Invalid JWS (EdDSA) signature.")
            return JwsResult(header=header, payload=payload_b)

        raise ValueError(f"Unsupported alg: {alg}")

    async def sign_general_json(
        self,
        *,
        payload: Union[bytes, str, Mapping[str, Any]],
        signatures: Sequence[
            Tuple[str, Mapping[str, Any], Optional[str], Optional[Mapping[str, Any]]]
        ],
    ) -> Dict[str, Any]:
        if isinstance(payload, str):
            payload_b = payload.encode("utf-8")
        elif isinstance(payload, (bytes, bytearray)):
            payload_b = bytes(payload)
        else:
            payload_b = json.dumps(
                payload, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")

        b64 = True
        if signatures:
            hdr = {"alg": signatures[0][0]}
            if signatures[0][2]:
                hdr["kid"] = signatures[0][2]
            if signatures[0][3]:
                hdr.update(dict(signatures[0][3]))
            b64 = hdr.get("b64", True)
            if not b64 and "b64" not in hdr.get("crit", []):
                raise ValueError("'b64': false requires 'b64' in 'crit'")

        if b64:
            payload_part = _b64u(payload_b)
        else:
            payload_part = payload_b.decode("utf-8")

        out_sigs = []
        for alg, key, kid, header_extra in signatures:
            header = {"alg": alg}
            if kid:
                header["kid"] = kid
            if header_extra:
                header.update(dict(header_extra))
            b64_hdr = _b64u(
                json.dumps(header, separators=(",", ":"), ensure_ascii=False).encode(
                    "utf-8"
                )
            )
            signing_input = (
                f"{b64_hdr}.{payload_part}".encode("utf-8")
                if not b64
                else f"{b64_hdr}.{payload_part}".encode("ascii")
            )
            sig_bytes = await self._sign_for_alg(signing_input, alg, key)
            out_sigs.append({"protected": b64_hdr, "signature": _b64u(sig_bytes)})
        return {"payload": payload_part, "signatures": out_sigs}

    async def verify_general_json(
        self,
        jws_obj: Mapping[str, Any],
        *,
        hmac_keys: Optional[Sequence[Mapping[str, Any]]] = None,
        rsa_pubkeys: Optional[Sequence[Any]] = None,
        ec_pubkeys: Optional[Sequence[Any]] = None,
        ed_pubkeys: Optional[Sequence[Any]] = None,
        k1_pubkeys: Optional[Sequence[Any]] = None,
        jwks_resolver: Optional[callable] = None,
        require_any: Optional[Iterable[str]] = None,
        min_signers: int = 1,
    ) -> Tuple[int, bytes]:
        payload_part = jws_obj.get("payload")
        if not isinstance(payload_part, str):
            raise ValueError("Invalid JWS JSON: missing payload.")
        sigs = jws_obj.get("signatures")
        if not isinstance(sigs, list) or not sigs:
            raise ValueError("Invalid JWS JSON: missing signatures.")

        payload_b = b""
        accepted = 0
        allowed = set(require_any) if require_any else None

        for s in sigs:
            b64_hdr = s.get("protected")
            b64sig = s.get("signature")
            if not (isinstance(b64_hdr, str) and isinstance(b64sig, str)):
                continue
            try:
                header = json.loads(_b64u_dec(b64_hdr))
            except Exception:
                continue
            alg = header.get("alg")
            kid = header.get("kid")
            if not isinstance(alg, str):
                continue
            if allowed and alg not in allowed:
                continue
            b64 = header.get("b64", True)
            if not b64 and "b64" not in header.get("crit", []):
                continue
            if b64:
                if not payload_b:
                    payload_b = _b64u_dec(payload_part)
                signing_input = f"{b64_hdr}.{payload_part}".encode("ascii")
            else:
                if not payload_b:
                    payload_b = payload_part.encode("utf-8")
                signing_input = f"{b64_hdr}.{payload_part}".encode("utf-8")
            sig = _b64u_dec(b64sig)
            if jwks_resolver:
                jwk = jwks_resolver(kid, alg)
                ok = await self._verify_one(signing_input, alg, sig, jwk=jwk)
            else:
                ok = await self._verify_one(
                    signing_input,
                    alg,
                    sig,
                    hmac_keys=hmac_keys,
                    rsa_pubkeys=rsa_pubkeys,
                    ec_pubkeys=ec_pubkeys,
                    ed_pubkeys=ed_pubkeys,
                    k1_pubkeys=k1_pubkeys,
                )
            if ok:
                accepted += 1
                if accepted >= min_signers:
                    break
        return accepted, payload_b

    async def _sign_for_alg(
        self, signing_input: bytes, alg: str, key: Mapping[str, Any]
    ) -> bytes:
        if _is_hmac(alg):
            sig = await self.hmac.sign_bytes(key, signing_input, alg=alg)
            return sig[0]["sig"]
        if _is_rsa(alg):
            mapped = _map_rsa_alg(alg)
            sig = await self.rsa.sign_bytes(key, signing_input, alg=mapped)
            return sig[0]["sig"]
        if _is_ec(alg):
            sig = await self.ecdsa.sign_bytes(key, signing_input, alg=alg)
            der = sig[0]["sig"]
            return _ecdsa_der_to_raw(der, alg)
        if _is_k1(alg):
            if not self.k1:
                raise ValueError(
                    "ES256K requested but secp256k1 signer is not available"
                )
            sig = await self.k1.sign_bytes(key, signing_input, alg="ES256K")
            der = sig[0]["sig"]
            return _ecdsa_der_to_raw(der, "ES256")
        if _is_eddsa(alg):
            sig = await self.eddsa.sign_bytes(key, signing_input, alg="Ed25519")
            return sig[0]["sig"]
        raise ValueError(f"Unsupported alg: {alg}")

    async def _verify_one(
        self,
        signing_input: bytes,
        alg: str,
        sig: bytes,
        *,
        jwk: Optional[Mapping[str, Any]] = None,
        hmac_keys: Optional[Sequence[Mapping[str, Any]]] = None,
        rsa_pubkeys: Optional[Sequence[Any]] = None,
        ec_pubkeys: Optional[Sequence[Any]] = None,
        ed_pubkeys: Optional[Sequence[Any]] = None,
        k1_pubkeys: Optional[Sequence[Any]] = None,
    ) -> bool:
        if jwk is not None:
            if _is_hmac(alg):
                return await self.hmac.verify_bytes(
                    signing_input,
                    [{"alg": alg, "sig": sig}],
                    require={"min_signers": 1, "algs": [alg]},
                    opts={
                        "keys": [{"kind": "raw", "key": _jwk_to_pub_for_signer(jwk)}]
                    },
                )
            if _is_rsa(alg):
                return await self.rsa.verify_bytes(
                    signing_input,
                    [{"alg": _map_rsa_alg(alg), "sig": sig}],
                    require={"min_signers": 1, "algs": [_map_rsa_alg(alg)]},
                    opts={"pubkeys": [_jwk_to_pub_for_signer(jwk)]},
                )
            if _is_ec(alg):
                return await self.ecdsa.verify_bytes(
                    signing_input,
                    [{"alg": alg, "sig": sig, "sigfmt": "raw"}],
                    require={"min_signers": 1, "algs": [alg]},
                    opts={"pubkeys": [_jwk_to_pub_for_signer(jwk)]},
                )
            if _is_k1(alg):
                if not self.k1:
                    return False
                return await self.k1.verify_bytes(
                    signing_input,
                    [{"alg": "ES256K", "sig": sig, "sigfmt": "raw"}],
                    require={"min_signers": 1, "algs": ["ES256K"]},
                    opts={"pubkeys": [_jwk_to_pub_for_signer(jwk)]},
                )
            if _is_eddsa(alg):
                return await self.eddsa.verify_bytes(
                    signing_input,
                    [{"alg": "Ed25519", "sig": sig}],
                    require={"min_signers": 1, "algs": ["Ed25519"]},
                    opts={"pubkeys": [_jwk_to_pub_for_signer(jwk)]},
                )
            return False

        if _is_hmac(alg) and hmac_keys:
            return await self.hmac.verify_bytes(
                signing_input,
                [{"alg": alg, "sig": sig}],
                require={"min_signers": 1, "algs": [alg]},
                opts={"keys": list(hmac_keys)},
            )
        if _is_rsa(alg) and rsa_pubkeys:
            return await self.rsa.verify_bytes(
                signing_input,
                [{"alg": _map_rsa_alg(alg), "sig": sig}],
                require={"min_signers": 1, "algs": [_map_rsa_alg(alg)]},
                opts={"pubkeys": list(rsa_pubkeys)},
            )
        if _is_ec(alg) and ec_pubkeys:
            return await self.ecdsa.verify_bytes(
                signing_input,
                [{"alg": alg, "sig": sig, "sigfmt": "raw"}],
                require={"min_signers": 1, "algs": [alg]},
                opts={"pubkeys": list(ec_pubkeys)},
            )
        if _is_k1(alg) and self.k1 and k1_pubkeys:
            return await self.k1.verify_bytes(
                signing_input,
                [{"alg": "ES256K", "sig": sig, "sigfmt": "raw"}],
                require={"min_signers": 1, "algs": ["ES256K"]},
                opts={"pubkeys": list(k1_pubkeys)},
            )
        if _is_eddsa(alg) and ed_pubkeys:
            pubs = []
            for x in ed_pubkeys:
                if isinstance(x, dict) and x.get("kty") == "OKP":
                    pubs.append(_jwk_to_pub_for_signer(x))
                else:
                    pubs.append(x)
            return await self.eddsa.verify_bytes(
                signing_input,
                [{"alg": "Ed25519", "sig": sig}],
                require={"min_signers": 1, "algs": ["Ed25519"]},
                opts={"pubkeys": pubs},
            )
        return False


def _map_rsa_alg(alg: str) -> str:
    if alg in _RSA_RS:
        return _RSA_RS[alg]
    if alg in _RSA_PS:
        return _RSA_PS[alg]
    raise ValueError(f"Unsupported RSA alg: {alg}")


__all__ = ["JwsSignerVerifier", "JwsResult"]
