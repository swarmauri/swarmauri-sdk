from __future__ import annotations

import base64
import json
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Tuple

import google.auth
from google.auth.transport.requests import Request as GARequest
import requests

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import secrets

from pydantic import PrivateAttr

from swarmauri_base.keys.KeyProviderBase import KeyProviderBase
from swarmauri_core.keys.types import ExportPolicy, KeySpec, KeyUse
from swarmauri_core.crypto.types import KeyRef


API_ROOT = "https://cloudkms.googleapis.com/v1"
SCOPE = "https://www.googleapis.com/auth/cloud-platform"


# ---------- Helpers ----------


def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def _b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def _now() -> float:
    return time.time()


def _is_rsa_decrypt_purpose(algorithm: str) -> bool:
    return algorithm.startswith("RSA_DECRYPT_")


def _is_rsa_sign_purpose(algorithm: str) -> bool:
    return algorithm.startswith("RSA_SIGN_")


def _is_ec_sign_purpose(algorithm: str) -> bool:
    return algorithm.startswith("EC_SIGN_")


def _hash_from_algo(algorithm: str):
    if algorithm.endswith("SHA256"):
        return hashes.SHA256()
    if algorithm.endswith("SHA384"):
        return hashes.SHA384()
    if algorithm.endswith("SHA512"):
        return hashes.SHA512()
    return hashes.SHA256()


def _ec_curve_from_algo(algorithm: str):
    if "P256" in algorithm:
        return ec.SECP256R1()
    if "P384" in algorithm:
        return ec.SECP384R1()
    if "SECP256K1" in algorithm:
        return ec.SECP256K1()
    return ec.SECP256R1()


def _jwk_from_pem_public_key(pem_bytes: bytes) -> Dict[str, Any]:
    pub = load_pem_public_key(pem_bytes)
    if isinstance(pub, rsa.RSAPublicKey):
        numbers = pub.public_numbers()
        n = numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")
        e = numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")
        return {
            "kty": "RSA",
            "n": base64.urlsafe_b64encode(n).rstrip(b"=").decode("ascii"),
            "e": base64.urlsafe_b64encode(e).rstrip(b"=").decode("ascii"),
        }
    if isinstance(pub, ec.EllipticCurvePublicKey):
        numbers = pub.public_numbers()
        x = numbers.x.to_bytes((numbers.curve.key_size + 7) // 8, "big")
        y = numbers.y.to_bytes((numbers.curve.key_size + 7) // 8, "big")
        crv = "P-256"
        if isinstance(numbers.curve, ec.SECP384R1):
            crv = "P-384"
        elif isinstance(numbers.curve, ec.SECP256K1):
            crv = "secp256k1"
        return {
            "kty": "EC",
            "crv": crv,
            "x": base64.urlsafe_b64encode(x).rstrip(b"=").decode("ascii"),
            "y": base64.urlsafe_b64encode(y).rstrip(b"=").decode("ascii"),
        }
    raise ValueError("Unsupported public key type in PEM")


@dataclass(frozen=True)
class _GcpKeyRef(KeyRef):
    """Read-only reference to a KMS key version."""


class GcpKmsKeyProvider(KeyProviderBase):
    type: Literal["GcpKmsKeyProvider"] = "GcpKmsKeyProvider"
    _creds = PrivateAttr()
    _ga_req = PrivateAttr()
    _lock: threading.RLock = PrivateAttr(default_factory=threading.RLock)
    _pub_cache: Dict[str, Tuple[bytes, str]] = PrivateAttr(default_factory=dict)
    _pub_cache_at: Dict[str, float] = PrivateAttr(default_factory=dict)
    _pub_ttl: float = PrivateAttr(default=300.0)

    def __init__(
        self,
        *,
        project_id: str,
        location_id: str,
        key_ring_id: str,
        http_timeout_s: int = 8,
        user_agent: str = "GcpKmsKeyProvider/1.0",
    ) -> None:
        super().__init__()
        self._project = project_id
        self._location = location_id
        self._ring = key_ring_id
        self._timeout = http_timeout_s
        self._ua = user_agent

        creds, _ = google.auth.default(scopes=[SCOPE])
        self._creds = creds
        self._ga_req = GARequest()

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "class": ("kms", "asym", "sym"),
            "algs": ("AES", "RSA", "EC"),
            "features": (
                "encrypt",
                "decrypt",
                "sign",
                "verify",
                "wrap",
                "unwrap",
                "jwks",
            ),
        }

    async def create_key(self, spec: KeySpec) -> KeyRef:
        purpose = "ENCRYPT_DECRYPT"
        token = self._token()
        url = (
            f"{API_ROOT}/projects/{self._project}/locations/{self._location}/"
            f"keyRings/{self._ring}/cryptoKeys?cryptoKeyId={spec.name}"
        )
        body = {"purpose": purpose}
        r = requests.post(
            url, headers=self._hdr(token), json=body, timeout=self._timeout
        )
        if r.status_code not in (200, 201):
            raise RuntimeError(f"create_key failed: {r.status_code} {r.text}")
        return _GcpKeyRef(
            kid=spec.name,
            version=1,
            type="OPAQUE",
            uses=(KeyUse.encrypt, KeyUse.decrypt),
            export_policy=ExportPolicy.public_only,
            public=None,
            material=None,
            tags={"kms": "gcp"},
        )

    async def import_key(
        self, spec: KeySpec, material: bytes, *, public: Optional[bytes] = None
    ) -> KeyRef:
        raise NotImplementedError(
            "Use Cloud KMS ImportJobs to import external keys (not provided here)"
        )

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ) -> KeyRef:
        raise NotImplementedError(
            "Configure rotation via Cloud KMS CryptoKey rotation config or create new versions"
        )

    async def destroy_key(self, kid: str, version: Optional[int] = None) -> bool:
        if version is None:
            raise ValueError("GCP KMS requires a specific version to destroy")
        name = self._version_name(kid, version)
        token = self._token()
        url = f"{API_ROOT}/{name}:destroy"
        r = requests.post(url, headers=self._hdr(token), json={}, timeout=self._timeout)
        if r.status_code != 200:
            raise RuntimeError(f"destroy_key failed: {r.status_code} {r.text}")
        return True

    async def get_key(
        self, kid: str, version: Optional[int] = None, *, include_secret: bool = False
    ) -> KeyRef:
        vname, algo = self._effective_version_and_algo(kid, version)
        public_pem = self._maybe_fetch_public_pem(vname, algo)
        public_bytes = None
        tags: Dict[str, Any] = {"kms": "gcp", "algorithm": algo}
        if public_pem:
            jwk = _jwk_from_pem_public_key(public_pem)
            tags["kty"] = jwk.get("kty")
            public_bytes = json.dumps(
                jwk, separators=(",", ":"), sort_keys=True
            ).encode("utf-8")

        ver_num = int(vname.rsplit("/", 1)[-1])
        if _is_rsa_decrypt_purpose(algo):
            uses = (KeyUse.wrap, KeyUse.unwrap)
        elif _is_rsa_sign_purpose(algo) or _is_ec_sign_purpose(algo):
            uses = (KeyUse.sign, KeyUse.verify)
        else:
            uses = (KeyUse.encrypt, KeyUse.decrypt)

        return _GcpKeyRef(
            kid=kid,
            version=ver_num,
            type="OPAQUE",
            uses=uses,
            export_policy=ExportPolicy.public_only,
            public=public_bytes,
            material=None,
            tags=tags,
        )

    async def list_versions(self, kid: str) -> Tuple[int, ...]:
        token = self._token()
        name = self._key_name(kid)
        url = f"{API_ROOT}/{name}/cryptoKeyVersions?pageSize=1000"
        r = requests.get(url, headers=self._hdr(token), timeout=self._timeout)
        if r.status_code != 200:
            raise RuntimeError(f"list_versions failed: {r.status_code} {r.text}")
        obj = r.json()
        vers = []
        for v in obj.get("cryptoKeyVersions", []):
            if v.get("state") == "ENABLED":
                vers.append(int(v["name"].split("/")[-1]))
        return tuple(sorted(vers))

    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        ref = await self.get_key(kid, version)
        if not ref.public:
            raise RuntimeError("no public key material available")
        return json.loads(ref.public.decode("utf-8"))

    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        token = self._token()
        list_url = f"{API_ROOT}/projects/{self._project}/locations/{self._location}/keyRings/{self._ring}/cryptoKeys?pageSize=1000"
        r = requests.get(list_url, headers=self._hdr(token), timeout=self._timeout)
        if r.status_code != 200:
            raise RuntimeError(f"jwks list keys failed: {r.status_code} {r.text}")
        keys_out = []
        for ck in r.json().get("cryptoKeys", []):
            kid = ck["name"].split("/")[-1]
            if prefix_kids and not kid.startswith(prefix_kids):
                continue
            v_url = f"{API_ROOT}/{ck['name']}/cryptoKeyVersions?pageSize=1000"
            rv = requests.get(v_url, headers=self._hdr(token), timeout=self._timeout)
            if rv.status_code != 200:
                continue
            for v in rv.json().get("cryptoKeyVersions", []):
                if v.get("state") != "ENABLED":
                    continue
                algo = v.get("algorithm", "")
                if (
                    _is_rsa_sign_purpose(algo)
                    or _is_ec_sign_purpose(algo)
                    or _is_rsa_decrypt_purpose(algo)
                ):
                    vname = v["name"]
                    pem = self._maybe_fetch_public_pem(vname, algo)
                    if not pem:
                        continue
                    jwk = _jwk_from_pem_public_key(pem)
                    jwk["kid"] = f"{kid}.{int(vname.split('/')[-1])}"
                    if _is_rsa_sign_purpose(algo):
                        jwk["alg"] = (
                            "PS256" if "PKCS1_PSS" in algo or "PSS" in algo else "RS256"
                        )
                    elif _is_ec_sign_purpose(algo):
                        jwk["alg"] = "ES256" if "P256" in algo else "ES384"
                    elif _is_rsa_decrypt_purpose(algo):
                        jwk["alg"] = "RSA-OAEP-256"
                    keys_out.append(jwk)
        return {"keys": keys_out}

    async def encrypt(
        self,
        kid: str,
        plaintext: bytes,
        *,
        aad: Optional[bytes] = None,
        version: Optional[int] = None,
    ) -> bytes:
        name = self._key_name(kid)
        token = self._token()
        url = f"{API_ROOT}/{name}:encrypt"
        body: Dict[str, Any] = {"plaintext": _b64e(plaintext)}
        if aad:
            body["additionalAuthenticatedData"] = _b64e(aad)
        r = requests.post(
            url, headers=self._hdr(token), json=body, timeout=self._timeout
        )
        if r.status_code != 200:
            raise RuntimeError(f"encrypt failed: {r.status_code} {r.text}")
        return _b64d(r.json()["ciphertext"])

    async def decrypt(
        self,
        kid: str,
        ciphertext: bytes,
        *,
        aad: Optional[bytes] = None,
        version: Optional[int] = None,
    ) -> bytes:
        name = self._key_name(kid)
        token = self._token()
        url = f"{API_ROOT}/{name}:decrypt"
        body: Dict[str, Any] = {"ciphertext": _b64e(ciphertext)}
        if aad:
            body["additionalAuthenticatedData"] = _b64e(aad)
        r = requests.post(
            url, headers=self._hdr(token), json=body, timeout=self._timeout
        )
        if r.status_code != 200:
            raise RuntimeError(f"decrypt failed: {r.status_code} {r.text}")
        return _b64d(r.json()["plaintext"])

    async def wrap_key(
        self, kid: str, dek: bytes, *, version: Optional[int] = None
    ) -> bytes:
        vname, algo = self._effective_version_and_algo(kid, version)
        if not _is_rsa_decrypt_purpose(algo):
            raise ValueError(f"wrap_key requires RSA_DECRYPT_* algorithm, got {algo}")
        pem = self._maybe_fetch_public_pem(vname, algo)
        if not pem:
            raise RuntimeError("No public key available for wrap_key")
        pub = load_pem_public_key(pem)
        if not isinstance(pub, rsa.RSAPublicKey):
            raise ValueError("wrap_key requires RSA public key")
        oaep_hash = _hash_from_algo(algo)
        ct = pub.encrypt(
            dek,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=oaep_hash),
                algorithm=oaep_hash,
                label=None,
            ),
        )
        return ct

    async def unwrap_key(
        self, kid: str, wrapped: bytes, *, version: Optional[int] = None
    ) -> bytes:
        vname, algo = self._effective_version_and_algo(kid, version)
        if not _is_rsa_decrypt_purpose(algo):
            raise ValueError(f"unwrap_key requires RSA_DECRYPT_* algorithm, got {algo}")
        token = self._token()
        url = f"{API_ROOT}/{vname}:asymmetricDecrypt"
        body = {"ciphertext": _b64e(wrapped)}
        r = requests.post(
            url, headers=self._hdr(token), json=body, timeout=self._timeout
        )
        if r.status_code != 200:
            raise RuntimeError(f"unwrap_key failed: {r.status_code} {r.text}")
        return _b64d(r.json()["plaintext"])

    async def sign(
        self,
        kid: str,
        message: bytes,
        *,
        version: Optional[int] = None,
        prehashed: bool = False,
    ) -> bytes:
        vname, algo = self._effective_version_and_algo(kid, version)
        if not (_is_rsa_sign_purpose(algo) or _is_ec_sign_purpose(algo)):
            raise ValueError(
                f"sign requires RSA_SIGN_* or EC_SIGN_* algorithm, got {algo}"
            )

        h = _hash_from_algo(algo)
        if prehashed:
            digest_bytes = message
        else:
            digest = hashes.Hash(h)
            digest.update(message)
            digest_bytes = digest.finalize()

        token = self._token()
        url = f"{API_ROOT}/{vname}:asymmetricSign"
        body = {"digest": {f"sha{h.digest_size * 8}": _b64e(digest_bytes)}}
        r = requests.post(
            url, headers=self._hdr(token), json=body, timeout=self._timeout
        )
        if r.status_code != 200:
            raise RuntimeError(f"sign failed: {r.status_code} {r.text}")
        return _b64d(r.json()["signature"])

    async def verify(
        self,
        kid: str,
        message: bytes,
        signature: bytes,
        *,
        version: Optional[int] = None,
        prehashed: bool = False,
    ) -> bool:
        vname, algo = self._effective_version_and_algo(kid, version)
        pem = self._maybe_fetch_public_pem(vname, algo)
        if not pem:
            raise RuntimeError("No public key available for verify")
        pub = load_pem_public_key(pem)

        h = _hash_from_algo(algo)
        if prehashed:
            digest_bytes = message
        else:
            digest_calc = hashes.Hash(h)
            digest_calc.update(message)
            digest_bytes = digest_calc.finalize()

        try:
            if isinstance(pub, rsa.RSAPublicKey):
                if "PKCS1" in algo and "PSS" not in algo:
                    pub.verify(
                        signature,
                        digest_bytes,
                        padding.PKCS1v15(),
                        Prehashed(h),
                    )
                else:
                    pub.verify(
                        signature,
                        digest_bytes,
                        padding.PSS(
                            mgf=padding.MGF1(h),
                            salt_length=padding.PSS.MAX_LENGTH,
                        ),
                        Prehashed(h),
                    )
                return True
            if isinstance(pub, ec.EllipticCurvePublicKey):
                pub.verify(signature, digest_bytes, ec.ECDSA(Prehashed(h)))
                return True
        except Exception:
            return False
        return False

    async def random_bytes(self, n: int) -> bytes:
        return secrets.token_bytes(n)

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        return HKDF(
            algorithm=hashes.SHA256(), length=length, salt=salt, info=info
        ).derive(ikm)

    def _token(self) -> str:
        with self._lock:
            if not self._creds.valid:
                self._creds.refresh(self._ga_req)
            return self._creds.token  # type: ignore[return-value]

    def _hdr(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self._ua,
        }

    def _key_name(self, kid: str) -> str:
        return f"projects/{self._project}/locations/{self._location}/keyRings/{self._ring}/cryptoKeys/{kid}"

    def _version_name(self, kid: str, version: int) -> str:
        return f"{self._key_name(kid)}/cryptoKeyVersions/{int(version)}"

    def _effective_version_and_algo(
        self, kid: str, version: Optional[int]
    ) -> Tuple[str, str]:
        token = self._token()
        if version is None:
            ck_url = f"{API_ROOT}/{self._key_name(kid)}"
            r = requests.get(ck_url, headers=self._hdr(token), timeout=self._timeout)
            if r.status_code != 200:
                raise RuntimeError(f"get CryptoKey failed: {r.status_code} {r.text}")
            obj = r.json()
            primary = obj.get("primary", {}).get("name")
            if primary:
                vname = primary
            else:
                lv_url = (
                    f"{API_ROOT}/{self._key_name(kid)}/cryptoKeyVersions?pageSize=1000"
                )
                rv = requests.get(
                    lv_url, headers=self._hdr(token), timeout=self._timeout
                )
                if rv.status_code != 200:
                    raise RuntimeError(
                        f"list versions failed: {rv.status_code} {rv.text}"
                    )
                enabled = [
                    (
                        int(v["name"].split("/")[-1]),
                        v["name"],
                        v.get("algorithm", ""),
                    )
                    for v in rv.json().get("cryptoKeyVersions", [])
                    if v.get("state") == "ENABLED"
                ]
                if not enabled:
                    raise RuntimeError("no ENABLED versions available")
                enabled.sort(key=lambda t: t[0], reverse=True)
                vname = enabled[0][1]
        else:
            vname = self._version_name(kid, version)

        v_url = f"{API_ROOT}/{vname}"
        rv = requests.get(v_url, headers=self._hdr(token), timeout=self._timeout)
        if rv.status_code != 200:
            raise RuntimeError(f"get version failed: {rv.status_code} {rv.text}")
        algo = rv.json().get("algorithm", "")
        return vname, algo

    def _maybe_fetch_public_pem(
        self, version_name: str, algorithm: str
    ) -> Optional[bytes]:
        if not (
            _is_rsa_sign_purpose(algorithm)
            or _is_ec_sign_purpose(algorithm)
            or _is_rsa_decrypt_purpose(algorithm)
        ):
            return None
        with self._lock:
            ts = self._pub_cache_at.get(version_name, 0.0)
            if version_name in self._pub_cache and (_now() - ts) < self._pub_ttl:
                return self._pub_cache[version_name][0]
        token = self._token()
        url = f"{API_ROOT}/{version_name}/publicKey"
        r = requests.get(url, headers=self._hdr(token), timeout=self._timeout)
        if r.status_code != 200:
            raise RuntimeError(f"getPublicKey failed: {r.status_code} {r.text}")
        pem = r.json().get("pem", "").encode("utf-8")
        with self._lock:
            self._pub_cache[version_name] = (pem, algorithm)
            self._pub_cache_at[version_name] = _now()
        return pem
