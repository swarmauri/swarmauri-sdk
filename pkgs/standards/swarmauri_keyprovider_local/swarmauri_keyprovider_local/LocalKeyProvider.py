from __future__ import annotations

import base64
import hashlib
import os
import secrets
from typing import Iterable, Mapping, Optional, Tuple, Dict, Literal

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, ec, x25519

from swarmauri_base.keys.KeyProviderBase import KeyProviderBase
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy
from swarmauri_core.crypto.types import KeyRef


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def _pem_pub(priv) -> bytes:
    return priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def _pem_priv(priv) -> bytes:
    return priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


class LocalKeyProvider(KeyProviderBase):
    """In-memory key provider for development and testing."""

    type: Literal["LocalKeyProvider"] = "LocalKeyProvider"

    def __init__(self) -> None:
        super().__init__()
        self._store: Dict[str, Dict[int, KeyRef]] = {}

    def supports(self) -> Mapping[str, Iterable[str]]:
        algs: tuple[str, ...] = (
            KeyAlg.AES256_GCM.value,
            KeyAlg.ED25519.value,
            KeyAlg.X25519.value,
            KeyAlg.RSA_OAEP_SHA256.value,
            KeyAlg.RSA_PSS_SHA256.value,
            KeyAlg.ECDSA_P256_SHA256.value,
        )
        return {
            "class": ("sym", "asym"),
            "algs": algs,
            "features": ("rotate", "import", "jwks", "hkdf", "random"),
        }

    async def create_key(self, spec: KeySpec) -> KeyRef:
        kid = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
        version = 1

        if spec.klass == KeyClass.symmetric:
            if spec.alg != KeyAlg.AES256_GCM:
                raise ValueError(f"Unsupported symmetric alg: {spec.alg}")
            material = secrets.token_bytes(32)
            public = None
        else:
            if spec.alg == KeyAlg.ED25519:
                sk = ed25519.Ed25519PrivateKey.generate()
            elif spec.alg == KeyAlg.X25519:
                sk = x25519.X25519PrivateKey.generate()
            elif spec.alg in (KeyAlg.RSA_OAEP_SHA256, KeyAlg.RSA_PSS_SHA256):
                bits = spec.size_bits or 3072
                sk = rsa.generate_private_key(public_exponent=65537, key_size=bits)
            elif spec.alg == KeyAlg.ECDSA_P256_SHA256:
                sk = ec.generate_private_key(ec.SECP256R1())
            else:
                raise ValueError(f"Unsupported asymmetric alg: {spec.alg}")
            material = _pem_priv(sk)
            public = _pem_pub(sk)

        ref = KeyRef(
            kid=kid,
            version=version,
            type="OPAQUE",
            uses=tuple(spec.uses),
            export_policy=spec.export_policy,
            public=public,
            material=(material if spec.export_policy != ExportPolicy.NONE else None),
            tags={"label": spec.label, "alg": spec.alg.value, **(spec.tags or {})},
            fingerprint=self._fingerprint(public=public, material=material, kid=kid),
        )
        self._store.setdefault(kid, {})[version] = ref
        return ref

    async def import_key(
        self,
        spec: KeySpec,
        material: bytes,
        *,
        public: Optional[bytes] = None,
    ) -> KeyRef:
        kid = hashlib.sha256(material).hexdigest()[:16]
        ref = KeyRef(
            kid=kid,
            version=1,
            type="OPAQUE",
            uses=tuple(spec.uses),
            export_policy=spec.export_policy,
            public=public,
            material=(material if spec.export_policy != ExportPolicy.NONE else None),
            tags={
                "label": spec.label,
                "alg": spec.alg.value,
                "imported": True,
                **(spec.tags or {}),
            },
            fingerprint=self._fingerprint(public=public, material=material, kid=kid),
        )
        self._store.setdefault(kid, {})[1] = ref
        return ref

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ) -> KeyRef:
        if kid not in self._store:
            raise KeyError(f"Unknown kid: {kid}")
        latest = max(self._store[kid])
        base = self._store[kid][latest]
        alg = KeyAlg(base.tags["alg"])
        spec = KeySpec(
            klass=(
                KeyClass.symmetric if alg == KeyAlg.AES256_GCM else KeyClass.asymmetric
            ),
            alg=alg,
            size_bits=(spec_overrides or {}).get("size_bits"),
            label=base.tags.get("label"),
            export_policy=base.export_policy,
            uses=tuple(base.uses),
            tags=base.tags,
        )
        new_ref = await self.create_key(spec)
        rotated = new_ref.__class__(
            **{**new_ref.__dict__, "kid": kid, "version": latest + 1}
        )
        self._store[kid][latest + 1] = rotated
        return rotated

    async def destroy_key(self, kid: str, version: Optional[int] = None) -> bool:
        bucket = self._store.get(kid)
        if not bucket:
            return False
        if version is None:
            del self._store[kid]
            return True
        bucket.pop(version, None)
        if not bucket:
            del self._store[kid]
        return True

    async def get_key(
        self,
        kid: str,
        version: Optional[int] = None,
        *,
        include_secret: bool = False,
    ) -> KeyRef:
        bucket = self._store[kid]
        v = version or max(bucket)
        ref = bucket[v]
        if include_secret or ref.material is None:
            return ref
        return ref

    async def list_versions(self, kid: str) -> Tuple[int, ...]:
        return tuple(sorted(self._store[kid].keys()))

    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        ref = await self.get_key(kid, version)
        alg = KeyAlg(ref.tags["alg"])
        if alg == KeyAlg.ED25519:
            pk = serialization.load_pem_public_key(ref.public)
            raw = pk.public_bytes(
                serialization.Encoding.Raw, serialization.PublicFormat.Raw
            )
            return {
                "kty": "OKP",
                "crv": "Ed25519",
                "x": _b64u(raw),
                "kid": f"{ref.kid}.{ref.version}",
            }
        if alg in (KeyAlg.RSA_OAEP_SHA256, KeyAlg.RSA_PSS_SHA256):
            pk = serialization.load_pem_public_key(ref.public)
            pn = pk.public_numbers()
            n = pn.n.to_bytes((pn.n.bit_length() + 7) // 8, "big")
            e = pn.e.to_bytes((pn.e.bit_length() + 7) // 8, "big")
            return {
                "kty": "RSA",
                "n": _b64u(n),
                "e": _b64u(e),
                "kid": f"{ref.kid}.{ref.version}",
            }
        if alg == KeyAlg.ECDSA_P256_SHA256:
            pk = serialization.load_pem_public_key(ref.public)
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
        if alg == KeyAlg.X25519:
            pk = serialization.load_pem_public_key(ref.public)
            raw = pk.public_bytes(
                serialization.Encoding.Raw, serialization.PublicFormat.Raw
            )
            return {
                "kty": "OKP",
                "crv": "X25519",
                "x": _b64u(raw),
                "kid": f"{ref.kid}.{ref.version}",
            }
        if alg == KeyAlg.AES256_GCM:
            return {"kty": "oct", "alg": "A256GCM", "kid": f"{ref.kid}.{ref.version}"}
        raise ValueError(f"Unsupported alg for JWK export: {alg}")

    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        out = []
        for _kid, versions in self._store.items():
            if prefix_kids and not _kid.startswith(prefix_kids):
                continue
            v = max(versions)
            out.append(await self.get_public_jwk(_kid, v))
        return {"keys": out}

    async def random_bytes(self, n: int) -> bytes:
        return secrets.token_bytes(n)

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        return HKDF(
            algorithm=hashes.SHA256(), length=length, salt=salt, info=info
        ).derive(ikm)
