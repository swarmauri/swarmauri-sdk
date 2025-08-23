from __future__ import annotations

import base64
import hashlib
import os
import secrets
from typing import Dict, Iterable, Mapping, Optional, Tuple, Literal

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    NoEncryption,
    PublicFormat,
)

from swarmauri_base.keys.KeyProviderBase import KeyProviderBase
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy
from swarmauri_core.crypto.types import KeyRef


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def _ssh_pub_bytes(pub) -> bytes:
    return pub.public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)


def _pem_priv(priv) -> bytes:
    return priv.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())


def _fingerprint(ssh_pub: bytes) -> str:
    try:
        b64 = ssh_pub.split(None, 2)[1]
        blob = base64.b64decode(b64)
        h = hashlib.md5(blob).hexdigest()
        return ":".join(a + b for a, b in zip(h[::2], h[1::2]))
    except Exception:  # pragma: no cover - defensive
        return "unknown"


class SshKeyProvider(KeyProviderBase):
    """SSH-focused key provider with JWK/JWKS export."""

    type: Literal["SshKeyProvider"] = "SshKeyProvider"

    def __init__(self) -> None:
        super().__init__()
        self._store: Dict[str, Dict[int, KeyRef]] = {}

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "class": ("asym",),
            "algs": (KeyAlg.ED25519, KeyAlg.RSA_PSS_SHA256, KeyAlg.ECDSA_P256_SHA256),
            "features": ("rotate", "import", "jwks", "hkdf", "random"),
        }

    async def create_key(self, spec: KeySpec) -> KeyRef:
        if spec.klass != KeyClass.asymmetric:
            raise ValueError("SshKeyProvider only creates asymmetric keys")
        kid = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
        version = 1

        if spec.alg == KeyAlg.ED25519:
            sk = ed25519.Ed25519PrivateKey.generate()
        elif spec.alg == KeyAlg.RSA_PSS_SHA256:
            bits = spec.size_bits or 3072
            sk = rsa.generate_private_key(public_exponent=65537, key_size=bits)
        elif spec.alg == KeyAlg.ECDSA_P256_SHA256:
            sk = ec.generate_private_key(ec.SECP256R1())
        else:
            raise ValueError(f"Unsupported alg: {spec.alg}")

        pem = _pem_priv(sk)
        ssh_pub = _ssh_pub_bytes(sk.public_key())

        ref = KeyRef(
            kid=kid,
            version=version,
            type="OPAQUE",
            uses=spec.uses,
            export_policy=spec.export_policy,
            public=ssh_pub,
            material=(pem if spec.export_policy != ExportPolicy.NONE else None),
            tags={
                "label": spec.label,
                "alg": spec.alg.value,
                "ssh_fingerprint": _fingerprint(ssh_pub),
            },
            fingerprint=self._fingerprint(public=ssh_pub, kid=kid),
        )
        self._store.setdefault(kid, {})[version] = ref
        return ref

    async def import_key(
        self, spec: KeySpec, material: bytes, *, public: Optional[bytes] = None
    ) -> KeyRef:
        kid = hashlib.sha256(material if material else (public or b"")).hexdigest()[:16]
        if material:
            sk = serialization.load_pem_private_key(material, password=None)
            ssh_pub = _ssh_pub_bytes(sk.public_key())
        elif public:
            ssh_pub = public
        else:
            raise ValueError(
                "Provide either PEM private in 'material' or OpenSSH public in 'public'"
            )

        ref = KeyRef(
            kid=kid,
            version=1,
            type="OPAQUE",
            uses=spec.uses,
            export_policy=spec.export_policy,
            public=ssh_pub,
            material=(material if spec.export_policy != ExportPolicy.NONE else None),
            tags={
                "label": spec.label,
                "alg": spec.alg.value,
                "imported": True,
                "ssh_fingerprint": _fingerprint(ssh_pub),
            },
            fingerprint=self._fingerprint(public=ssh_pub, kid=kid),
        )
        self._store.setdefault(kid, {})[1] = ref
        return ref

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ) -> KeyRef:
        if kid not in self._store:
            raise KeyError("unknown kid")
        latest = max(self._store[kid])
        base = self._store[kid][latest]
        alg = KeyAlg(base.tags["alg"])
        spec = KeySpec(
            klass=KeyClass.asymmetric,
            alg=alg,
            size_bits=(spec_overrides or {}).get("size_bits"),
            label=base.tags.get("label"),
            export_policy=base.export_policy,
            uses=tuple(base.uses),
            tags=base.tags,
        )
        new = await self.create_key(spec)
        new = new.__class__(**{**new.__dict__, "kid": kid, "version": latest + 1})
        self._store[kid][latest + 1] = new
        return new

    async def destroy_key(self, kid: str, version: Optional[int] = None) -> bool:
        if kid not in self._store:
            return False
        if version is None:
            del self._store[kid]
            return True
        self._store[kid].pop(version, None)
        if not self._store[kid]:
            del self._store[kid]
        return True

    async def get_key(
        self, kid: str, version: Optional[int] = None, *, include_secret: bool = False
    ) -> KeyRef:
        bucket = self._store[kid]
        v = version or max(bucket)
        return bucket[v]

    async def list_versions(self, kid: str) -> Tuple[int, ...]:
        return tuple(sorted(self._store[kid].keys()))

    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        ref = await self.get_key(kid, version)
        alg = KeyAlg(ref.tags["alg"])
        pk = serialization.load_ssh_public_key(ref.public)
        if alg == KeyAlg.ED25519:
            raw = pk.public_bytes(Encoding.Raw, PublicFormat.Raw)
            return {
                "kty": "OKP",
                "crv": "Ed25519",
                "x": _b64u(raw),
                "kid": f"{ref.kid}.{ref.version}",
            }
        if alg == KeyAlg.ECDSA_P256_SHA256:
            nums = pk.public_numbers()
            x = nums.x.to_bytes(32, "big")
            y = nums.y.to_bytes(32, "big")
            return {
                "kty": "EC",
                "crv": "P-256",
                "x": _b64u(x),
                "y": _b64u(y),
                "kid": f"{ref.kid}.{ref.version}",
            }
        if alg == KeyAlg.RSA_PSS_SHA256:
            nums = pk.public_numbers()
            n = nums.n.to_bytes((nums.n.bit_length() + 7) // 8, "big")
            e = nums.e.to_bytes((nums.e.bit_length() + 7) // 8, "big")
            return {
                "kty": "RSA",
                "n": _b64u(n),
                "e": _b64u(e),
                "kid": f"{ref.kid}.{ref.version}",
            }
        raise ValueError("Unsupported alg for JWK export")

    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        out = []
        for kid, versions in self._store.items():
            if prefix_kids and not kid.startswith(prefix_kids):
                continue
            v = max(versions)
            out.append(await self.get_public_jwk(kid, v))
        return {"keys": out}

    async def random_bytes(self, n: int) -> bytes:
        return secrets.token_bytes(n)

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        return HKDF(
            algorithm=hashes.SHA256(), length=length, salt=salt, info=info
        ).derive(ikm)
