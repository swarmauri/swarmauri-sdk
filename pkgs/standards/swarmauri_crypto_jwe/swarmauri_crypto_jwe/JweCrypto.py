from __future__ import annotations

import base64
import json
import os
import zlib
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple, Union

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec, x25519
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    load_pem_private_key,
)

from swarmauri_core.crypto.types import JWAAlg


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def _b64u_dec(s: str) -> bytes:
    pad = "=" * ((4 - (len(s) % 4)) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _json_dumps(obj: Any) -> bytes:
    return json.dumps(
        obj, separators=(",", ":"), ensure_ascii=False, sort_keys=False
    ).encode("utf-8")


def _cek_len_for_enc(enc: JWAAlg) -> int:
    if enc == JWAAlg.A128GCM:
        return 16
    if enc == JWAAlg.A192GCM:
        return 24
    if enc == JWAAlg.A256GCM:
        return 32
    raise ValueError(f"Unsupported enc '{enc.value}'. Use A128GCM/A192GCM/A256GCM.")


def _hash_for_oaep(alg: JWAAlg):
    if alg == JWAAlg.RSA_OAEP:
        return hashes.SHA1()
    if alg == JWAAlg.RSA_OAEP_256:
        return hashes.SHA256()
    raise ValueError(f"Unsupported RSA OAEP alg '{alg.value}'.")


def _rand(n: int) -> bytes:
    return os.urandom(n)


def _compute_aad(protected_b64: str, aad_bytes: Optional[bytes]) -> bytes:
    if not aad_bytes:
        return protected_b64.encode("ascii")
    return (protected_b64 + "." + _b64u(aad_bytes)).encode("ascii")


def _jwk_ec_public_numbers(jwk: Mapping[str, Any]) -> ec.EllipticCurvePublicNumbers:
    crv = jwk.get("crv")
    curve_map = {
        "P-256": ec.SECP256R1(),
        "P-384": ec.SECP384R1(),
        "P-521": ec.SECP521R1(),
    }
    if crv not in curve_map:
        raise ValueError(f"Unsupported EC curve in JWK: {crv}")
    x = int.from_bytes(_b64u_dec(jwk["x"]), "big")
    y = int.from_bytes(_b64u_dec(jwk["y"]), "big")
    return ec.EllipticCurvePublicNumbers(x, y, curve_map[crv])


def _ec_jwk_from_public_key(pk: ec.EllipticCurvePublicKey) -> Dict[str, Any]:
    numbers = pk.public_numbers()
    crv = pk.curve.name
    crv_map = {"secp256r1": "P-256", "secp384r1": "P-384", "secp521r1": "P-521"}
    if crv not in crv_map:
        raise ValueError(f"Unsupported EC curve: {crv}")
    size = (pk.curve.key_size + 7) // 8
    x = numbers.x.to_bytes(size, "big")
    y = numbers.y.to_bytes(size, "big")
    return {"kty": "EC", "crv": crv_map[crv], "x": _b64u(x), "y": _b64u(y)}


def _x25519_jwk_from_public_key(pk: x25519.X25519PublicKey) -> Dict[str, Any]:
    raw = pk.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )
    return {"kty": "OKP", "crv": "X25519", "x": _b64u(raw)}


def _load_rsa_public(key: Any) -> rsa.RSAPublicKey:
    if isinstance(key, rsa.RSAPublicKey):
        return key
    if isinstance(key, (bytes, bytearray, str)):
        data = key if isinstance(key, (bytes, bytearray)) else key.encode("utf-8")
        pk = load_pem_public_key(data)
        if not isinstance(pk, rsa.RSAPublicKey):
            raise TypeError("PEM provided is not an RSA public key")
        return pk
    if isinstance(key, Mapping) and key.get("kty") == "RSA":
        n = int.from_bytes(_b64u_dec(key["n"]), "big")
        e = int.from_bytes(_b64u_dec(key["e"]), "big")
        return rsa.RSAPublicNumbers(e, n).public_key()
    raise TypeError("Unsupported RSA public key format.")


def _load_rsa_private(
    key: Any, password: Optional[Union[str, bytes]] = None
) -> rsa.RSAPrivateKey:
    if isinstance(key, rsa.RSAPrivateKey):
        return key
    pwd = None
    if isinstance(password, str):
        pwd = password.encode("utf-8")
    elif isinstance(password, (bytes, bytearray)):
        pwd = bytes(password)
    if isinstance(key, (bytes, bytearray, str)):
        data = key if isinstance(key, (bytes, bytearray)) else key.encode("utf-8")
        sk = load_pem_private_key(data, password=pwd)
        if not isinstance(sk, rsa.RSAPrivateKey):
            raise TypeError("PEM provided is not an RSA private key")
        return sk
    raise TypeError("Unsupported RSA private key format.")


def _load_ecdh_recipient_public(jwk_or_pem: Any) -> Tuple[str, Any]:
    if isinstance(jwk_or_pem, Mapping):
        kty = jwk_or_pem.get("kty")
        if kty == "EC":
            pn = _jwk_ec_public_numbers(jwk_or_pem)
            return jwk_or_pem["crv"], pn.public_key()
        if kty == "OKP" and jwk_or_pem.get("crv") == "X25519":
            x = _b64u_dec(jwk_or_pem["x"])
            return "X25519", x25519.X25519PublicKey.from_public_bytes(x)
        raise ValueError(
            f"Unsupported JWK kty/crv for ECDH-ES: {kty}/{jwk_or_pem.get('crv')}"
        )
    if isinstance(jwk_or_pem, (bytes, bytearray, str)):
        data = (
            jwk_or_pem
            if isinstance(jwk_or_pem, (bytes, bytearray))
            else jwk_or_pem.encode("utf-8")
        )
        pk = load_pem_public_key(data)
        if isinstance(pk, ec.EllipticCurvePublicKey):
            crv = pk.curve.name
            if crv == "secp256r1":
                return "P-256", pk
            if crv == "secp384r1":
                return "P-384", pk
            if crv == "secp521r1":
                return "P-521", pk
            raise ValueError(f"Unsupported EC curve: {crv}")
        raise TypeError("PEM must be an EC public key for ECDH-ES.")
    raise TypeError("Unsupported recipient public key format for ECDH-ES.")


def _concat_kdf(
    z: bytes,
    enc: JWAAlg,
    hash_alg=hashes.SHA256(),
    apu: Optional[bytes] = None,
    apv: Optional[bytes] = None,
) -> bytes:
    keydatalen_bits = _cek_len_for_enc(enc) * 8
    alg_id = _jwe_alg_id(enc)
    ckdf = ConcatKDFHash(
        algorithm=hash_alg,
        length=keydatalen_bits // 8,
        otherinfo=alg_id + (apu or b"") + (apv or b""),
    )
    return ckdf.derive(z)


def _jwe_alg_id(enc: JWAAlg) -> bytes:
    enc_b = enc.value.encode("ascii")
    return len(enc_b).to_bytes(4, "big") + enc_b


JWECompact = str


@dataclass
class JweDecryptResult:
    header: Dict[str, Any]
    plaintext: bytes


class JweCrypto:
    """Utility class for JSON Web Encryption (RFC 7516, RFC 7518)."""

    async def encrypt_compact(
        self,
        *,
        payload: Union[bytes, str, Mapping[str, Any]],
        alg: JWAAlg,
        enc: JWAAlg,
        key: Mapping[str, Any],
        kid: Optional[str] = None,
        header_extra: Optional[Mapping[str, Any]] = None,
        aad: Optional[Union[bytes, str]] = None,
    ) -> JWECompact:
        if isinstance(payload, str):
            pt = payload.encode("utf-8")
        elif isinstance(payload, (bytes, bytearray)):
            pt = bytes(payload)
        else:
            pt = _json_dumps(payload)

        protected: Dict[str, Any] = {"alg": alg.value, "enc": enc.value}
        if kid:
            protected["kid"] = kid
        if header_extra:
            protected.update(dict(header_extra))

        if protected.get("zip") == "DEF":
            pt = zlib.compress(pt)

        cek: bytes
        encrypted_key_b64 = ""
        epk_header: Optional[Dict[str, Any]] = None

        if alg == JWAAlg.DIR:
            secret = key.get("k")
            secret_b = (
                secret.encode("utf-8") if isinstance(secret, str) else bytes(secret)
            )
            if len(secret_b) != _cek_len_for_enc(enc):
                raise ValueError(
                    f"'dir' key size must equal enc key size ({_cek_len_for_enc(enc)} bytes)"
                )
            cek = secret_b
        elif alg in (JWAAlg.RSA_OAEP, JWAAlg.RSA_OAEP_256):
            cek = _rand(_cek_len_for_enc(enc))
            pk = _load_rsa_public(key.get("pub") or key)
            hash_alg = _hash_for_oaep(alg)
            ekey = pk.encrypt(
                cek,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hash_alg),
                    algorithm=hash_alg,
                    label=None,
                ),
            )
            encrypted_key_b64 = _b64u(ekey)
        elif alg == JWAAlg.ECDH_ES:
            crv, rpk = _load_ecdh_recipient_public(key.get("pub") or key)
            if crv == "X25519":
                esk = x25519.X25519PrivateKey.generate()
                epk = esk.public_key()
                z = esk.exchange(rpk)  # type: ignore[arg-type]
                epk_header = _x25519_jwk_from_public_key(epk)
            else:
                curve = {
                    "P-256": ec.SECP256R1(),
                    "P-384": ec.SECP384R1(),
                    "P-521": ec.SECP521R1(),
                }[crv]
                esk = ec.generate_private_key(curve)
                epk = esk.public_key()
                z = esk.exchange(ec.ECDH(), rpk)  # type: ignore[arg-type]
                epk_header = _ec_jwk_from_public_key(epk)
            apu_b = None
            apv_b = None
            if "apu" in (header_extra or {}):
                apu_b = (
                    _b64u_dec(header_extra["apu"])
                    if isinstance(header_extra["apu"], str)
                    else header_extra["apu"]
                )
            if "apv" in (header_extra or {}):
                apv_b = (
                    _b64u_dec(header_extra["apv"])
                    if isinstance(header_extra["apv"], str)
                    else header_extra["apv"]
                )
            cek = _concat_kdf(z, enc, hashes.SHA256(), apu_b, apv_b)
            protected["epk"] = epk_header
        else:
            raise ValueError(f"Unsupported alg '{alg.value}'")

        iv = _rand(12)
        aadd = _ensure_bytes(aad) if aad is not None else None

        protected_b64 = _b64u(_json_dumps(protected))
        aead_aad = _compute_aad(protected_b64, aadd)

        aesgcm = AESGCM(cek)
        ct = aesgcm.encrypt(iv, pt, aead_aad)
        ciphertext, tag = ct[:-16], ct[-16:]

        return ".".join(
            [
                protected_b64,
                encrypted_key_b64,
                _b64u(iv),
                _b64u(ciphertext),
                _b64u(tag),
            ]
        )

    async def decrypt_compact(
        self,
        jwe: JWECompact,
        *,
        dir_key: Optional[Union[bytes, str]] = None,
        rsa_private_pem: Optional[Union[str, bytes]] = None,
        rsa_private_password: Optional[Union[str, bytes]] = None,
        ecdh_private_key: Optional[Any] = None,
        expected_algs: Optional[Iterable[JWAAlg]] = None,
        expected_encs: Optional[Iterable[JWAAlg]] = None,
        aad: Optional[Union[bytes, str]] = None,
    ) -> JweDecryptResult:
        parts = jwe.split(".")
        if len(parts) != 5:
            raise ValueError("Invalid JWE compact: expected 5 dot-separated parts.")
        b64_prot, b64_ekey, b64_iv, b64_ct, b64_tag = parts

        header = json.loads(_b64u_dec(b64_prot))
        try:
            alg = JWAAlg(header.get("alg"))
            enc = JWAAlg(header.get("enc"))
        except Exception as exc:
            raise ValueError("JWE header missing 'alg' or 'enc'.") from exc
        if expected_algs and alg not in set(expected_algs):
            raise ValueError(f"Unexpected alg '{alg.value}'.")
        if expected_encs and enc not in set(expected_encs):
            raise ValueError(f"Unexpected enc '{enc.value}'.")

        iv = _b64u_dec(b64_iv)
        if len(iv) != 12:
            raise ValueError("Invalid IV length for AES-GCM (must be 96-bit).")
        ciphertext = _b64u_dec(b64_ct)
        tag = _b64u_dec(b64_tag)
        aadd = _ensure_bytes(aad) if aad is not None else None
        aead_aad = _compute_aad(b64_prot, aadd)

        if alg == JWAAlg.DIR:
            if dir_key is None:
                raise ValueError("dir_key is required for alg='dir'.")
            cek = (
                dir_key.encode("utf-8") if isinstance(dir_key, str) else bytes(dir_key)
            )
            if len(cek) != _cek_len_for_enc(enc):
                raise ValueError("dir_key length mismatch for enc.")
        elif alg in (JWAAlg.RSA_OAEP, JWAAlg.RSA_OAEP_256):
            if rsa_private_pem is None:
                raise ValueError("rsa_private_pem is required for RSA-OAEP decryption.")
            sk = _load_rsa_private(rsa_private_pem, password=rsa_private_password)
            ekey = _b64u_dec(b64_ekey)
            hash_alg = _hash_for_oaep(alg)
            cek = sk.decrypt(
                ekey,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hash_alg), algorithm=hash_alg, label=None
                ),
            )
        elif alg == JWAAlg.ECDH_ES:
            if ecdh_private_key is None:
                raise ValueError("ecdh_private_key is required for ECDH-ES decryption.")
            epk = header.get("epk")
            if not isinstance(epk, Mapping):
                raise ValueError("Missing/invalid 'epk' in JWE header for ECDH-ES.")
            if epk.get("kty") == "OKP" and epk.get("crv") == "X25519":
                if not isinstance(ecdh_private_key, x25519.X25519PrivateKey):
                    raise TypeError("ECDH-ES with X25519 requires an X25519PrivateKey.")
                z = ecdh_private_key.exchange(
                    x25519.X25519PublicKey.from_public_bytes(_b64u_dec(epk["x"]))
                )
            elif epk.get("kty") == "EC":
                crv = epk.get("crv")
                curve = {
                    "P-256": ec.SECP256R1(),
                    "P-384": ec.SECP384R1(),
                    "P-521": ec.SECP521R1(),
                }.get(crv)
                if curve is None:
                    raise ValueError(f"Unsupported EC curve in epk: {crv}")
                if not isinstance(ecdh_private_key, ec.EllipticCurvePrivateKey):
                    raise TypeError(
                        "ECDH-ES with EC requires an EllipticCurvePrivateKey."
                    )
                x = int.from_bytes(_b64u_dec(epk["x"]), "big")
                y = int.from_bytes(_b64u_dec(epk["y"]), "big")
                rpk = ec.EllipticCurvePublicNumbers(x, y, curve).public_key()
                z = ecdh_private_key.exchange(ec.ECDH(), rpk)
            else:
                raise ValueError("Unsupported 'epk' kty/crv.")
            apu_b = _b64u_dec(header["apu"]) if "apu" in header else None
            apv_b = _b64u_dec(header["apv"]) if "apv" in header else None
            cek = _concat_kdf(z, enc, hashes.SHA256(), apu_b, apv_b)
        else:
            raise ValueError(f"Unsupported alg '{alg.value}'")

        aesgcm = AESGCM(cek)
        try:
            pt = aesgcm.decrypt(iv, ciphertext + tag, aead_aad)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(
                "JWE decryption failed (invalid tag or wrong key)."
            ) from exc

        if header.get("zip") == "DEF":
            try:
                pt = zlib.decompress(pt)
            except Exception as exc:  # noqa: BLE001
                raise ValueError(f"Failed to decompress (zip=DEF): {exc}") from exc

        return JweDecryptResult(header=header, plaintext=pt)


def _ensure_bytes(v: Union[str, bytes, bytearray]) -> bytes:
    if isinstance(v, (bytes, bytearray)):
        return bytes(v)
    if isinstance(v, str):
        return v.encode("utf-8")
    raise TypeError("Expected bytes or str")
