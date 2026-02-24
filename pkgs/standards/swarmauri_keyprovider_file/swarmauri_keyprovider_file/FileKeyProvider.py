from __future__ import annotations

import base64
import json
import os
import secrets
import shutil
import threading
import time
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional, Tuple, Literal

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, ec, x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from swarmauri_base.key_providers.KeyProviderBase import KeyProviderBase
from swarmauri_core.key_providers.types import (
    KeySpec,
    KeyAlg,
    KeyClass,
    ExportPolicy,
    KeyUse,
)
from swarmauri_core.crypto.types import KeyRef


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def _hash_hex(b: bytes, nbytes: int = 16) -> str:
    h = hashes.Hash(hashes.SHA256())
    h.update(b)
    return h.finalize().hex()[: 2 * nbytes]


def _serialize_keypair(priv, spec: KeySpec) -> tuple[bytes, Optional[bytes]]:
    """Serialize private and public key material according to ``spec``."""

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

    return public, material


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _now() -> int:
    return int(time.time())


class FileKeyProvider(KeyProviderBase):
    """File-backed key provider."""

    type: Literal["FileKeyProvider"] = "FileKeyProvider"

    def __init__(self, root_dir: str | Path) -> None:
        super().__init__()
        self.root = Path(root_dir)
        _ensure_dir(self.root)
        _ensure_dir(self.root / "keys")
        object.__setattr__(self, "_lock", threading.RLock())

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "class": ("sym", "asym"),
            "algs": (
                KeyAlg.AES256_GCM,
                KeyAlg.ED25519,
                KeyAlg.X25519,
                KeyAlg.RSA_OAEP_SHA256,
                KeyAlg.RSA_PSS_SHA256,
                KeyAlg.ECDSA_P256_SHA256,
            ),
            "features": (
                "create",
                "rotate",
                "import",
                "jwks",
                "hkdf",
                "random",
                "persist",
            ),
        }

    def _key_dir(self, kid: str) -> Path:
        return self.root / "keys" / kid

    def _ver_dir(self, kid: str, version: int) -> Path:
        return self._key_dir(kid) / f"v{version}"

    def _meta_path(self, kid: str) -> Path:
        return self._key_dir(kid) / "meta.json"

    def _write_meta(
        self,
        kid: str,
        *,
        klass: KeyClass,
        alg: KeyAlg,
        uses: Tuple[KeyUse, ...],
        export_policy: ExportPolicy,
        label: Optional[str],
        tags: Optional[Dict[str, object]],
    ) -> None:
        p = self._meta_path(kid)
        meta = {
            "kid": kid,
            "klass": klass.value,
            "alg": alg.value,
            "uses": [u.value for u in uses],
            "export_policy": export_policy.value,
            "label": label,
            "tags": tags or {},
            "created_at": _now(),
        }
        _ensure_dir(p.parent)
        p.write_text(json.dumps(meta, indent=2))

    def _read_meta(self, kid: str) -> dict:
        p = self._meta_path(kid)
        if not p.exists():
            raise KeyError(f"unknown kid: {kid}")
        return json.loads(p.read_text())

    def _latest_version(self, kid: str) -> int:
        kd = self._key_dir(kid)
        if not kd.exists():
            raise KeyError(f"unknown kid: {kid}")
        max_v = 0
        for entry in kd.iterdir():
            if entry.is_dir() and entry.name.startswith("v"):
                try:
                    v = int(entry.name[1:])
                    if v > max_v:
                        max_v = v
                except Exception:
                    continue
        if max_v == 0:
            raise KeyError(f"no versions for kid: {kid}")
        return max_v

    async def create_key(self, spec: KeySpec) -> KeyRef:
        with self._lock:
            kid = _hash_hex(os.urandom(16))
            version = 1
            vdir = self._ver_dir(kid, version)
            _ensure_dir(vdir)

            public: Optional[bytes] = None
            material: Optional[bytes] = None

            if spec.klass == KeyClass.symmetric:
                if spec.alg != KeyAlg.AES256_GCM:
                    raise ValueError(f"Unsupported symmetric alg: {spec.alg}")
                raw = secrets.token_bytes(32)
                if spec.export_policy != ExportPolicy.PUBLIC_ONLY:
                    material = raw
                    (vdir / "private.pem").write_text(
                        json.dumps({"kty": "oct", "k": _b64u(raw)})
                    )
                (vdir / "public.jwk").write_text(
                    json.dumps({"kty": "oct", "alg": "A256GCM"})
                )
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

                public, material = _serialize_keypair(sk, spec)
                (vdir / "public.pem").write_bytes(public)
                if material is not None:
                    (vdir / "private.pem").write_bytes(material)

            self._write_meta(
                kid,
                klass=spec.klass,
                alg=spec.alg,
                uses=spec.uses,
                export_policy=spec.export_policy,
                label=spec.label,
                tags=spec.tags,
            )

            return KeyRef(
                kid=kid,
                version=version,
                type="OPAQUE",
                uses=spec.uses,
                export_policy=spec.export_policy,
                public=public,
                material=material,
                tags={"label": spec.label, "alg": spec.alg.value, **(spec.tags or {})},
                fingerprint=self._fingerprint(
                    public=public, material=material, kid=kid
                ),
            )

    async def import_key(
        self, spec: KeySpec, material: bytes, *, public: Optional[bytes] = None
    ) -> KeyRef:
        with self._lock:
            kid = _hash_hex(material if material else os.urandom(16))
            version = 1
            vdir = self._ver_dir(kid, version)
            _ensure_dir(vdir)

            if spec.klass == KeyClass.symmetric:
                if spec.export_policy == ExportPolicy.PUBLIC_ONLY:
                    (vdir / "private.pem").write_text(
                        json.dumps({"kty": "oct", "k": None})
                    )
                    mat_out = None
                else:
                    (vdir / "private.pem").write_text(
                        json.dumps({"kty": "oct", "k": _b64u(material)})
                    )
                    mat_out = material
                (vdir / "public.jwk").write_text(
                    json.dumps({"kty": "oct", "alg": "A256GCM"})
                )
                pub_out = None
            else:
                if public:
                    (vdir / "public.pem").write_bytes(public)
                    pub_out = public
                else:
                    try:
                        sk = serialization.load_pem_private_key(material, password=None)
                        pub_out = sk.public_key().public_bytes(
                            serialization.Encoding.PEM,
                            serialization.PublicFormat.SubjectPublicKeyInfo,
                        )
                        (vdir / "public.pem").write_bytes(pub_out)
                    except Exception:
                        pub_out = None
                if spec.export_policy != ExportPolicy.PUBLIC_ONLY:
                    (vdir / "private.pem").write_bytes(material)
                    mat_out = material
                else:
                    mat_out = None

            self._write_meta(
                kid,
                klass=spec.klass,
                alg=spec.alg,
                uses=spec.uses,
                export_policy=spec.export_policy,
                label=spec.label,
                tags=spec.tags,
            )

            return KeyRef(
                kid=kid,
                version=version,
                type="OPAQUE",
                uses=spec.uses,
                export_policy=spec.export_policy,
                public=pub_out,
                material=mat_out,
                tags={
                    "label": spec.label,
                    "alg": spec.alg.value,
                    "imported": True,
                    **(spec.tags or {}),
                },
                fingerprint=self._fingerprint(
                    public=pub_out, material=mat_out, kid=kid
                ),
            )

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ) -> KeyRef:
        with self._lock:
            meta = self._read_meta(kid)
            latest = self._latest_version(kid)
            next_v = latest + 1
            klass = KeyClass(meta["klass"])
            alg = KeyAlg(meta["alg"])
            uses = tuple(KeyUse(u) for u in meta["uses"])
            export_policy = ExportPolicy(meta["export_policy"])
            label = meta.get("label")
            tags = meta.get("tags") or {}

            vdir = self._ver_dir(kid, next_v)
            _ensure_dir(vdir)

            ov = spec_overrides or {}
            material: Optional[bytes] = None
            public: Optional[bytes] = None

            if klass == KeyClass.symmetric:
                raw = secrets.token_bytes(32)
                if export_policy != ExportPolicy.PUBLIC_ONLY:
                    material = raw
                    (vdir / "private.pem").write_text(
                        json.dumps({"kty": "oct", "k": _b64u(raw)})
                    )
                (vdir / "public.jwk").write_text(
                    json.dumps({"kty": "oct", "alg": "A256GCM"})
                )
            else:
                if alg == KeyAlg.ED25519:
                    sk = ed25519.Ed25519PrivateKey.generate()
                elif alg == KeyAlg.X25519:
                    sk = x25519.X25519PrivateKey.generate()
                elif alg in (KeyAlg.RSA_OAEP_SHA256, KeyAlg.RSA_PSS_SHA256):
                    bits = int(ov.get("size_bits") or 3072)
                    sk = rsa.generate_private_key(public_exponent=65537, key_size=bits)
                elif alg == KeyAlg.ECDSA_P256_SHA256:
                    sk = ec.generate_private_key(ec.SECP256R1())
                else:
                    raise ValueError(f"Unsupported alg during rotate: {alg}")

                tmp_spec = KeySpec(
                    klass=klass,
                    alg=alg,
                    uses=uses,
                    export_policy=export_policy,
                )
                public, material = _serialize_keypair(sk, tmp_spec)
                (vdir / "public.pem").write_bytes(public)
                if material is not None:
                    (vdir / "private.pem").write_bytes(material)

            if ov:
                new_meta = dict(meta)
                if "label" in ov:
                    new_meta["label"] = ov["label"]
                    label = ov["label"]
                if "tags" in ov and isinstance(ov["tags"], dict):
                    tags.update(ov["tags"])
                    new_meta["tags"] = tags
                self._meta_path(kid).write_text(json.dumps(new_meta, indent=2))

            return KeyRef(
                kid=kid,
                version=next_v,
                type="OPAQUE",
                uses=uses,
                export_policy=export_policy,
                public=public,
                material=material,
                tags={"label": label, "alg": alg.value, **tags},
                fingerprint=self._fingerprint(
                    public=public, material=material, kid=kid
                ),
            )

    async def destroy_key(self, kid: str, version: Optional[int] = None) -> bool:
        with self._lock:
            kdir = self._key_dir(kid)
            if not kdir.exists():
                return False
            if version is None:
                shutil.rmtree(kdir, ignore_errors=True)
                return True
            vdir = self._ver_dir(kid, version)
            if vdir.exists():
                shutil.rmtree(vdir, ignore_errors=True)
            try:
                _ = self._latest_version(kid)
            except Exception:
                if self._meta_path(kid).exists():
                    self._meta_path(kid).unlink(missing_ok=True)
                if kdir.exists():
                    try:
                        kdir.rmdir()
                    except Exception:
                        pass
            return True

    async def get_key(
        self, kid: str, version: Optional[int] = None, *, include_secret: bool = False
    ) -> KeyRef:
        with self._lock:
            meta = self._read_meta(kid)
            v = version or self._latest_version(kid)
            vdir = self._ver_dir(kid, v)
            if not vdir.exists():
                raise KeyError(f"unknown version: {kid}.v{v}")

            export_policy = ExportPolicy(meta["export_policy"])
            alg = KeyAlg(meta["alg"])
            uses = tuple(KeyUse(u) for u in meta["uses"])

            public: Optional[bytes] = None
            material: Optional[bytes] = None

            pem_pub = vdir / "public.pem"
            if pem_pub.exists():
                public = pem_pub.read_bytes()
            else:
                jwk_pub = vdir / "public.jwk"
                if jwk_pub.exists():
                    public = jwk_pub.read_bytes()

            if include_secret and export_policy != ExportPolicy.PUBLIC_ONLY:
                pem_priv = vdir / "private.pem"
                if pem_priv.exists():
                    try:
                        obj = json.loads(pem_priv.read_text())
                        if obj.get("kty") == "oct" and obj.get("k"):
                            material = base64.urlsafe_b64decode(obj["k"] + "==")
                        else:
                            material = pem_priv.read_bytes()
                    except json.JSONDecodeError:
                        material = pem_priv.read_bytes()

            return KeyRef(
                kid=kid,
                version=v,
                type="OPAQUE",
                uses=uses,
                export_policy=export_policy,
                public=public,
                material=material,
                tags={
                    "label": meta.get("label"),
                    "alg": alg.value,
                    **(meta.get("tags") or {}),
                },
                fingerprint=self._fingerprint(
                    public=public, material=material, kid=kid
                ),
            )

    async def list_versions(self, kid: str) -> Tuple[int, ...]:
        with self._lock:
            kd = self._key_dir(kid)
            if not kd.exists():
                raise KeyError(f"unknown kid: {kid}")
            vs: list[int] = []
            for entry in kd.iterdir():
                if entry.is_dir() and entry.name.startswith("v"):
                    try:
                        vs.append(int(entry.name[1:]))
                    except Exception:
                        pass
            if not vs:
                raise KeyError(f"no versions for kid: {kid}")
            vs.sort()
            return tuple(vs)

    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        ref = await self.get_key(kid, version, include_secret=False)
        alg = KeyAlg(ref.tags["alg"])

        if alg == KeyAlg.AES256_GCM:
            return {
                "kty": "oct",
                "alg": "A256GCM",
                "kid": f"{ref.kid}.{ref.version}",
            }

        if ref.public is None:
            vdir = self._ver_dir(ref.kid, ref.version)
            pem_pub = vdir / "public.pem"
            if not pem_pub.exists():
                raise RuntimeError("Public material unavailable for asymmetric key")
            pub_bytes = pem_pub.read_bytes()
        else:
            pub_bytes = ref.public

        pk = serialization.load_pem_public_key(pub_bytes)

        if alg == KeyAlg.ED25519:
            raw = pk.public_bytes(
                serialization.Encoding.Raw, serialization.PublicFormat.Raw
            )
            return {
                "kty": "OKP",
                "crv": "Ed25519",
                "x": _b64u(raw),
                "kid": f"{ref.kid}.{ref.version}",
            }

        if alg == KeyAlg.X25519:
            raw = pk.public_bytes(
                serialization.Encoding.Raw, serialization.PublicFormat.Raw
            )
            return {
                "kty": "OKP",
                "crv": "X25519",
                "x": _b64u(raw),
                "kid": f"{ref.kid}.{ref.version}",
            }

        if alg in (KeyAlg.RSA_OAEP_SHA256, KeyAlg.RSA_PSS_SHA256):
            nums = pk.public_numbers()
            n = nums.n.to_bytes((nums.n.bit_length() + 7) // 8, "big")
            e = nums.e.to_bytes((nums.e.bit_length() + 7) // 8, "big")
            return {
                "kty": "RSA",
                "n": _b64u(n),
                "e": _b64u(e),
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

        raise ValueError(f"Unsupported alg for JWK export: {alg}")

    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        with self._lock:
            out = []
            kroot = self.root / "keys"
            for kid_dir in kroot.iterdir():
                if not kid_dir.is_dir():
                    continue
                kid = kid_dir.name
                if prefix_kids and not kid.startswith(prefix_kids):
                    continue
                try:
                    latest = self._latest_version(kid)
                    out.append(await self.get_public_jwk(kid, latest))
                except Exception:
                    continue
            return {"keys": out}

    async def random_bytes(self, n: int) -> bytes:
        return secrets.token_bytes(n)

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        return HKDF(
            algorithm=hashes.SHA256(), length=length, salt=salt, info=info
        ).derive(ikm)
