"""In-memory key provider for symmetric and asymmetric algorithms.

This module offers :class:`LocalKeyProvider` for quick development and testing
without external dependencies.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
from typing import Iterable, Mapping, Optional, Tuple, Dict, Literal

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, ec, x25519

from swarmauri_base.keys.KeyProviderBase import KeyProviderBase
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy
from swarmauri_core.crypto.types import KeyRef, KeyType


def _b64u(b: bytes) -> str:
    """URL-safe base64 encoding without padding.

    b (bytes): Data to encode.
    RETURNS (str): Encoded string.
    """

    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def _serialize_keypair(priv, spec: KeySpec) -> tuple[bytes, Optional[bytes]]:
    """Serialize a private key and its public counterpart.

    priv: The private key to serialize.
    spec (KeySpec): Options controlling the encoding.
    RETURNS (Tuple[bytes, Optional[bytes]]): Private bytes and public bytes.
    """

    encoding = (
        serialization.Encoding[spec.encoding]
        if spec.encoding
        else serialization.Encoding.PEM
    )
    public_format = (
        serialization.PublicFormat[spec.public_format]
        if spec.public_format
        else serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public = priv.public_key().public_bytes(encoding=encoding, format=public_format)

    material: Optional[bytes] = None
    if spec.export_policy != ExportPolicy.PUBLIC_ONLY:
        private_format = (
            serialization.PrivateFormat[spec.private_format]
            if spec.private_format
            else serialization.PrivateFormat.PKCS8
        )
        if spec.encryption and spec.encryption != "NoEncryption":
            raise ValueError(f"Unsupported encryption: {spec.encryption}")
        material = priv.private_bytes(
            encoding,
            private_format,
            serialization.NoEncryption(),
        )

    return material, public


class LocalKeyProvider(KeyProviderBase):
    """Store and manage keys entirely in memory.

    create_key(spec) -> KeyRef:
        Generate a key according to ``spec`` and store it.
    import_key(spec, material, public=None) -> KeyRef:
        Register an existing key pair or secret.
    rotate_key(kid, spec_overrides=None) -> KeyRef:
        Produce a new version for ``kid``.
    jwks(prefix_kids=None) -> dict:
        Export all public keys as a JWKS document.
    """

    type: Literal["LocalKeyProvider"] = "LocalKeyProvider"

    def __init__(self) -> None:
        super().__init__()
        self._store: Dict[str, Dict[int, KeyRef]] = {}

    def supports(self) -> Mapping[str, Iterable[str]]:
        algs: tuple[str, ...] = (
            KeyAlg.AES256_GCM.value,
            KeyAlg.ED25519.value,
            KeyAlg.X25519.value,
            KeyAlg.X25519MLKEM768.value,
            KeyAlg.RSA_OAEP_SHA256.value,
            KeyAlg.RSA_PSS_SHA256.value,
            KeyAlg.ECDSA_P256_SHA256.value,
        )
        return {
            "class": ("sym", "asym"),
            "algs": algs,
            "features": ("create", "rotate", "import", "jwks", "hkdf", "random"),
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
            elif spec.alg == KeyAlg.X25519MLKEM768:
                priv_struct, pub_struct = _generate_x25519_mlkem768()
                material = (
                    _encode_json(priv_struct)
                    if spec.export_policy != ExportPolicy.PUBLIC_ONLY
                    else None
                )
                public = _encode_json(pub_struct)
                sk = None  # type: ignore[assignment]
            else:
                raise ValueError(f"Unsupported asymmetric alg: {spec.alg}")

            if spec.alg != KeyAlg.X25519MLKEM768:
                material, public = _serialize_keypair(sk, spec)
                if spec.export_policy == ExportPolicy.PUBLIC_ONLY:
                    material = None

        key_type = _key_type_for_alg(spec.alg)

        ref = KeyRef(
            kid=kid,
            version=version,
            type=key_type,
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
        if spec.alg == KeyAlg.X25519MLKEM768:
            priv_struct = _validate_hybrid_payload(material)
            if public is not None:
                pub_struct = _validate_hybrid_payload(public)
            else:
                pub_struct = _derive_hybrid_public(priv_struct)
            public = _encode_json(pub_struct)
            if spec.export_policy != ExportPolicy.PUBLIC_ONLY:
                material = _encode_json(priv_struct)
            else:
                material = None
        ref = KeyRef(
            kid=kid,
            version=1,
            type=_key_type_for_alg(spec.alg),
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
        if alg == KeyAlg.X25519MLKEM768:
            payload = ref.public
            if payload is None and ref.material is not None:
                priv_struct = _validate_hybrid_payload(ref.material)
                payload = _encode_json(_derive_hybrid_public(priv_struct))
            if payload is None:
                raise ValueError("Public material unavailable for X25519MLKEM768")
            data = _validate_hybrid_payload(payload)
            x_data = data.get("x25519") or {}
            kem_data = data.get("mlkem768") or {}
            if not isinstance(x_data, dict) or not isinstance(kem_data, dict):
                raise ValueError("Malformed X25519MLKEM768 public payload")
            return {
                "kty": HYBRID_KTY,
                "x25519": {"crv": "X25519", "x": x_data.get("public")},
                "mlkem768": {"public": kem_data.get("public")},
                "kid": f"{ref.kid}.{ref.version}",
            }
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


HYBRID_KTY = "X25519+ML-KEM-768"
MLKEM768_PUBLIC_KEY_LEN = 1184
MLKEM768_SECRET_KEY_LEN = 2400


def _encode_json(data: Dict[str, object]) -> bytes:
    return json.dumps(data, sort_keys=True).encode("utf-8")


def _generate_x25519_mlkem768() -> tuple[Dict[str, object], Dict[str, object]]:
    sk = x25519.X25519PrivateKey.generate()
    priv_raw = sk.private_bytes(
        serialization.Encoding.Raw,
        serialization.PrivateFormat.Raw,
        serialization.NoEncryption(),
    )
    pub_raw = sk.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    mlkem_pub = os.urandom(MLKEM768_PUBLIC_KEY_LEN)
    mlkem_secret = os.urandom(MLKEM768_SECRET_KEY_LEN)
    public_struct: Dict[str, object] = {
        "kty": HYBRID_KTY,
        "x25519": {"public": _b64u(pub_raw)},
        "mlkem768": {"public": _b64u(mlkem_pub)},
    }
    private_struct: Dict[str, object] = {
        "kty": HYBRID_KTY,
        "x25519": {"public": _b64u(pub_raw), "private": _b64u(priv_raw)},
        "mlkem768": {"public": _b64u(mlkem_pub), "secret": _b64u(mlkem_secret)},
    }
    return private_struct, public_struct


def _validate_hybrid_payload(payload: bytes) -> Dict[str, object]:
    try:
        data = json.loads(payload.decode("utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError("Invalid X25519MLKEM768 payload") from exc
    if not isinstance(data, dict) or data.get("kty") != HYBRID_KTY:
        raise ValueError("Invalid X25519MLKEM768 structure")
    return data


def _derive_hybrid_public(private_struct: Dict[str, object]) -> Dict[str, object]:
    x = private_struct.get("x25519") or {}
    kem = private_struct.get("mlkem768") or {}
    if not isinstance(x, dict) or not isinstance(kem, dict):
        raise ValueError("Invalid X25519MLKEM768 private structure")
    if "public" not in x or "public" not in kem:
        raise ValueError("X25519MLKEM768 private structure missing public keys")
    return {
        "kty": HYBRID_KTY,
        "x25519": {"public": x["public"]},
        "mlkem768": {"public": kem["public"]},
    }


def _key_type_for_alg(alg: KeyAlg) -> KeyType:
    if alg == KeyAlg.AES256_GCM:
        return KeyType.SYMMETRIC
    if alg in (KeyAlg.RSA_OAEP_SHA256, KeyAlg.RSA_PSS_SHA256):
        return KeyType.RSA
    if alg == KeyAlg.ECDSA_P256_SHA256:
        return KeyType.EC
    if alg == KeyAlg.ED25519:
        return KeyType.ED25519
    if alg == KeyAlg.X25519:
        return KeyType.X25519
    if alg == KeyAlg.X25519MLKEM768:
        return KeyType.X25519_MLKEM768
    return KeyType.OPAQUE
