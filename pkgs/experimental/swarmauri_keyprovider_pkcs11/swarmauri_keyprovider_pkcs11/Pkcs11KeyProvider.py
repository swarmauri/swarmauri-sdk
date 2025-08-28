from __future__ import annotations

import os
import base64
import hashlib
import secrets
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional, Tuple, Literal, Any

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec

from swarmauri_base.keys.KeyProviderBase import KeyProviderBase
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse
from swarmauri_core.crypto.types import KeyRef

try:  # pragma: no cover - optional dependency
    import pkcs11
    from pkcs11 import Attribute, ObjectClass, KeyType, Mechanism

    _PKCS11_OK = True
except Exception:  # pragma: no cover - dependency missing
    _PKCS11_OK = False


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


@dataclass(frozen=True)
class _IndexEntry:
    kid: str
    version: int
    label: str
    klass: KeyClass
    alg: KeyAlg
    handles: Dict[str, bytes]
    tags: Dict[str, Any]


class Pkcs11KeyProvider(KeyProviderBase):
    """PKCS#11-backed key provider."""

    type: Literal["Pkcs11KeyProvider"] = "Pkcs11KeyProvider"

    def __init__(
        self,
        module_path: str,
        *,
        slot: Optional[int] = None,
        token_label: Optional[str] = None,
        user_pin: Optional[str] = None,
        key_label_prefix: str = "sa:",
        allow_ec: bool = True,
        allow_rsa: bool = True,
        allow_aes: bool = True,
    ) -> None:
        super().__init__()
        if not _PKCS11_OK:
            raise ImportError(
                "python-pkcs11 is required. Install with: pip install python-pkcs11"
            )

        self._lib = pkcs11.lib(module_path)
        if token_label:
            self._slot = next(
                (
                    s
                    for s in self._lib.get_slots()
                    if s.get_token().label.strip() == token_label
                ),
                None,
            )
            if self._slot is None:
                raise RuntimeError(
                    f"PKCS#11 token with label={token_label!r} not found"
                )
        else:
            slots = list(self._lib.get_slots())
            if not slots:
                raise RuntimeError("No PKCS#11 slots available")
            self._slot = slots[slot or 0]

        self._pin = user_pin
        self._prefix = key_label_prefix
        self._idx: Dict[str, Dict[int, _IndexEntry]] = {}
        self._allow_ec = allow_ec
        self._allow_rsa = allow_rsa
        self._allow_aes = allow_aes

    def _session(self):  # pragma: no cover - thin wrapper
        return self._slot.get_token().open(rw=True, user_pin=self._pin)

    def supports(self) -> Mapping[str, Iterable[str]]:
        algs: list[str] = []
        if self._allow_aes:
            algs.append(KeyAlg.AES256_GCM.value)
        if self._allow_ec:
            algs.append(KeyAlg.ECDSA_P256_SHA256.value)
        if self._allow_rsa:
            algs.extend([KeyAlg.RSA_OAEP_SHA256.value, KeyAlg.RSA_PSS_SHA256.value])
        return {
            "class": ("sym", "asym"),
            "algs": tuple(algs),
            "features": (
                "create",
                "rotate",
                "jwks",
                "non_exportable",
                "random",
                "hkdf",
            ),
        }

    async def create_key(self, spec: KeySpec) -> KeyRef:
        kid = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
        version = 1
        label = f"{self._prefix}{kid}.v{version}"
        cka_id = secrets.token_bytes(8)

        if spec.klass == KeyClass.symmetric:
            if spec.alg != KeyAlg.AES256_GCM:
                raise ValueError("AES-256 only")
            if not self._allow_aes:
                raise RuntimeError("AES disabled")
            with self._session() as s:
                s.generate_key(
                    KeyType.AES,
                    256,
                    label=label,
                    id=cka_id,
                    template={
                        Attribute.SENSITIVE: True,
                        Attribute.EXTRACTABLE: False,
                        Attribute.ENCRYPT: True,
                        Attribute.DECRYPT: True,
                        Attribute.WRAP: True,
                        Attribute.UNWRAP: True,
                    },
                )
            entry = _IndexEntry(
                kid=kid,
                version=version,
                label=label,
                klass=KeyClass.symmetric,
                alg=spec.alg,
                handles={"sec_id": cka_id},
                tags={"label": spec.label, "module": "pkcs11", "kty": "oct"},
            )
            self._idx.setdefault(kid, {})[version] = entry
            return KeyRef(
                kid=kid,
                version=version,
                type="OPAQUE",
                uses=spec.uses,
                export_policy=ExportPolicy.NONE,
                public=None,
                material=None,
                tags={"label": spec.label, "alg": spec.alg.value, "provider": "pkcs11"},
                fingerprint=self._fingerprint(kid=kid),
            )

        if spec.alg in (KeyAlg.RSA_OAEP_SHA256, KeyAlg.RSA_PSS_SHA256):
            if not self._allow_rsa:
                raise RuntimeError("RSA disabled")
            size_bits = spec.size_bits or 3072
            with self._session() as s:
                pub, priv = s.generate_keypair(
                    KeyType.RSA,
                    mechanism=Mechanism.RSA_PKCS_KEY_PAIR_GEN,
                    store=True,
                    public_template={
                        Attribute.LABEL: label,
                        Attribute.ID: cka_id,
                        Attribute.VERIFY: True,
                        Attribute.ENCRYPT: True,
                        Attribute.WRAP: True,
                        Attribute.PUBLIC_EXPONENT: (65537).to_bytes(3, "big"),
                        Attribute.MODULUS_BITS: size_bits,
                    },
                    private_template={
                        Attribute.LABEL: label,
                        Attribute.ID: cka_id,
                        Attribute.SENSITIVE: True,
                        Attribute.EXTRACTABLE: False,
                        Attribute.SIGN: True,
                        Attribute.DECRYPT: True,
                        Attribute.UNWRAP: True,
                    },
                )
                n = pub[Attribute.MODULUS]
                e = pub[Attribute.PUBLIC_EXPONENT]
            entry = _IndexEntry(
                kid=kid,
                version=version,
                label=label,
                klass=KeyClass.asymmetric,
                alg=spec.alg,
                handles={"pub_id": cka_id, "priv_id": cka_id},
                tags={
                    "label": spec.label,
                    "module": "pkcs11",
                    "kty": "RSA",
                    "n_len": len(n) * 8,
                },
            )
            self._idx.setdefault(kid, {})[version] = entry
            pub_pem = serialization.load_der_public_key(
                rsa.RSAPublicNumbers(int.from_bytes(n, "big"), int.from_bytes(e, "big"))
                .public_key()
                .public_bytes(
                    serialization.Encoding.DER,
                    serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            ).public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            return KeyRef(
                kid=kid,
                version=version,
                type="OPAQUE",
                uses=spec.uses,
                export_policy=ExportPolicy.NONE,
                public=pub_pem,
                material=None,
                tags={"label": spec.label, "alg": spec.alg.value, "provider": "pkcs11"},
                fingerprint=self._fingerprint(public=pub_pem, kid=kid),
            )

        if spec.alg == KeyAlg.ECDSA_P256_SHA256:
            if not self._allow_ec:
                raise RuntimeError("EC disabled")
            P256_PARAM = bytes.fromhex("06082A8648CE3D030107")
            with self._session() as s:
                pub, priv = s.generate_keypair(
                    KeyType.EC,
                    store=True,
                    public_template={
                        Attribute.LABEL: label,
                        Attribute.ID: cka_id,
                        Attribute.VERIFY: True,
                        Attribute.EC_PARAMS: P256_PARAM,
                    },
                    private_template={
                        Attribute.LABEL: label,
                        Attribute.ID: cka_id,
                        Attribute.SENSITIVE: True,
                        Attribute.EXTRACTABLE: False,
                        Attribute.SIGN: True,
                    },
                )
                ec_point = pub[Attribute.EC_POINT]
            x, y = _parse_ec_point_uncompressed(ec_point, 32)
            entry = _IndexEntry(
                kid=kid,
                version=version,
                label=label,
                klass=KeyClass.asymmetric,
                alg=spec.alg,
                handles={"pub_id": cka_id, "priv_id": cka_id},
                tags={
                    "label": spec.label,
                    "module": "pkcs11",
                    "kty": "EC",
                    "crv": "P-256",
                },
            )
            self._idx.setdefault(kid, {})[version] = entry
            pub_pem = (
                ec.EllipticCurvePublicNumbers(
                    int.from_bytes(x, "big"),
                    int.from_bytes(y, "big"),
                    ec.SECP256R1(),
                )
                .public_key()
                .public_bytes(
                    serialization.Encoding.PEM,
                    serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )
            return KeyRef(
                kid=kid,
                version=version,
                type="OPAQUE",
                uses=spec.uses,
                export_policy=ExportPolicy.NONE,
                public=pub_pem,
                material=None,
                tags={"label": spec.label, "alg": spec.alg.value, "provider": "pkcs11"},
                fingerprint=self._fingerprint(public=pub_pem, kid=kid),
            )

        raise ValueError(f"Unsupported algorithm: {spec.alg}")

    async def import_key(
        self, spec: KeySpec, material: bytes, *, public: Optional[bytes] = None
    ) -> KeyRef:
        raise NotImplementedError("Private key import not supported")

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ) -> KeyRef:
        entry_latest = self._latest_entry(kid)
        spec = KeySpec(
            klass=entry_latest.klass,
            alg=entry_latest.alg,
            size_bits=spec_overrides.get("size_bits") if spec_overrides else None,
            label=entry_latest.tags.get("label"),
            export_policy=ExportPolicy.NONE,
            uses=entry_latest.tags.get("uses", (KeyUse.sign, KeyUse.verify)),
            tags=entry_latest.tags,
        )
        new_ref = await self.create_key(spec)
        latest_v = max(self._idx[kid].keys())
        new_entry = self._idx[new_ref.kid][1]
        self._idx.setdefault(kid, {})[latest_v + 1] = _IndexEntry(
            kid=kid,
            version=latest_v + 1,
            label=new_entry.label,
            klass=new_entry.klass,
            alg=new_entry.alg,
            handles=new_entry.handles,
            tags=new_entry.tags,
        )
        del self._idx[new_ref.kid]
        return KeyRef(
            kid=kid,
            version=latest_v + 1,
            type=new_ref.type,
            uses=new_ref.uses,
            export_policy=ExportPolicy.NONE,
            public=new_ref.public,
            material=None,
            tags=new_ref.tags,
            fingerprint=self._fingerprint(public=new_ref.public, kid=kid),
        )

    async def destroy_key(self, kid: str, version: Optional[int] = None) -> bool:
        if kid not in self._idx:
            return False
        versions = [version] if version is not None else list(self._idx[kid].keys())
        ok = True
        with self._session() as s:
            for v in versions:
                ent = self._idx[kid].get(v)
                if not ent:
                    ok = False
                    continue
                try:
                    for obj in s.get_objects({Attribute.LABEL: ent.label}):
                        obj.destroy()
                except pkcs11.PKCS11Error:
                    ok = False
                self._idx[kid].pop(v, None)
        if kid in self._idx and not self._idx[kid]:
            self._idx.pop(kid, None)
        return ok

    async def get_key(
        self, kid: str, version: Optional[int] = None, *, include_secret: bool = False
    ) -> KeyRef:
        ent = self._entry(kid, version)
        public_pem = None
        if ent.klass == KeyClass.asymmetric:
            with self._session() as s:
                pub_obj = _first_or_none(
                    s.get_objects(
                        {
                            Attribute.CLASS: ObjectClass.PUBLIC_KEY,
                            Attribute.LABEL: ent.label,
                        }
                    )
                )
                if not pub_obj:
                    raise KeyError("Public key not found on token")
                if ent.alg in (KeyAlg.RSA_OAEP_SHA256, KeyAlg.RSA_PSS_SHA256):
                    n = pub_obj[Attribute.MODULUS]
                    e = pub_obj[Attribute.PUBLIC_EXPONENT]
                    pub = rsa.RSAPublicNumbers(
                        int.from_bytes(n, "big"), int.from_bytes(e, "big")
                    ).public_key()
                    public_pem = pub.public_bytes(
                        serialization.Encoding.PEM,
                        serialization.PublicFormat.SubjectPublicKeyInfo,
                    )
                elif ent.alg == KeyAlg.ECDSA_P256_SHA256:
                    ec_point = pub_obj[Attribute.EC_POINT]
                    x, y = _parse_ec_point_uncompressed(ec_point, 32)
                    pub = ec.EllipticCurvePublicNumbers(
                        int.from_bytes(x, "big"),
                        int.from_bytes(y, "big"),
                        ec.SECP256R1(),
                    ).public_key()
                    public_pem = pub.public_bytes(
                        serialization.Encoding.PEM,
                        serialization.PublicFormat.SubjectPublicKeyInfo,
                    )
        return KeyRef(
            kid=ent.kid,
            version=ent.version,
            type="OPAQUE",
            uses=(KeyUse.sign, KeyUse.verify)
            if ent.klass == KeyClass.asymmetric
            else (KeyUse.wrap, KeyUse.unwrap),
            export_policy=ExportPolicy.NONE,
            public=public_pem,
            material=None,
            tags={
                "label": ent.tags.get("label"),
                "alg": ent.alg.value,
                "provider": "pkcs11",
            },
            fingerprint=self._fingerprint(public=public_pem, kid=ent.kid),
        )

    async def list_versions(self, kid: str) -> Tuple[int, ...]:
        if kid not in self._idx:
            raise KeyError("unknown kid")
        return tuple(sorted(self._idx[kid].keys()))

    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        ent = self._entry(kid, version)
        if ent.klass == KeyClass.symmetric:
            return {"kty": "oct", "alg": "A256GCM", "kid": f"{ent.kid}.{ent.version}"}
        with self._session() as s:
            pub_obj = _first_or_none(
                s.get_objects(
                    {
                        Attribute.CLASS: ObjectClass.PUBLIC_KEY,
                        Attribute.LABEL: ent.label,
                    }
                )
            )
            if not pub_obj:
                raise KeyError("Public key not found on token")
            if ent.alg in (KeyAlg.RSA_OAEP_SHA256, KeyAlg.RSA_PSS_SHA256):
                n = pub_obj[Attribute.MODULUS]
                e = pub_obj[Attribute.PUBLIC_EXPONENT]
                return {
                    "kty": "RSA",
                    "n": _b64u(n),
                    "e": _b64u(e),
                    "kid": f"{ent.kid}.{ent.version}",
                }
            if ent.alg == KeyAlg.ECDSA_P256_SHA256:
                ec_point = pub_obj[Attribute.EC_POINT]
                x, y = _parse_ec_point_uncompressed(ec_point, 32)
                return {
                    "kty": "EC",
                    "crv": "P-256",
                    "x": _b64u(x),
                    "y": _b64u(y),
                    "kid": f"{ent.kid}.{ent.version}",
                }
        raise ValueError("Unsupported algorithm for JWK export")

    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        out = []
        for kid, versions in self._idx.items():
            if prefix_kids and not kid.startswith(prefix_kids):
                continue
            v = max(versions)
            out.append(await self.get_public_jwk(kid, v))
        return {"keys": out}

    async def random_bytes(self, n: int) -> bytes:
        with self._session() as s:
            return s.generate_random(n)

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        return HKDF(
            algorithm=hashes.SHA256(), length=length, salt=salt, info=info
        ).derive(ikm)

    def _latest_entry(self, kid: str) -> _IndexEntry:
        if kid not in self._idx or not self._idx[kid]:
            raise KeyError("unknown kid")
        v = max(self._idx[kid].keys())
        return self._idx[kid][v]

    def _entry(self, kid: str, version: Optional[int]) -> _IndexEntry:
        if kid not in self._idx:
            raise KeyError("unknown kid")
        if version is None:
            return self._latest_entry(kid)
        ent = self._idx[kid].get(version)
        if not ent:
            raise KeyError("unknown key version")
        return ent


def _first_or_none(iterable):
    for x in iterable:
        return x
    return None


def _parse_ec_point_uncompressed(
    ec_point_attr: bytes, coord_len: int
) -> tuple[bytes, bytes]:
    data = bytes(ec_point_attr)
    if (
        len(data) >= 2
        and data[0] == 0x04
        and data[1] == len(data) - 2
        and data[1] in (coord_len * 2 + 1, coord_len * 2 + 2)
    ):
        if len(data) >= 3 and data[2] == 0x04 and len(data) == data[1] + 2:
            data = data[2:]
    if not data or data[0] != 0x04:
        raise ValueError("Unsupported EC_POINT encoding")
    if len(data) != 1 + 2 * coord_len:
        body = data[1:]
        if len(body) % 2 != 0:
            raise ValueError("Invalid EC_POINT length")
        half = len(body) // 2
        x = body[:half].rjust(coord_len, b"\x00")[-coord_len:]
        y = body[half:].rjust(coord_len, b"\x00")[-coord_len:]
        return x, y
    return data[1 : 1 + coord_len], data[1 + coord_len :]
