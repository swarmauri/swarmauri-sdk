from __future__ import annotations

from typing import Dict, Optional, Tuple, Literal
import base64
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import parse_qs

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, ed448, rsa
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.crypto.types import (
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_core.keys.IKeyProvider import IKeyProvider


class KeyProviderBase(IKeyProvider, ComponentBase):
    """Base class for key providers within the Swarmauri ecosystem."""

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: Literal["KeyProviderBase"] = "KeyProviderBase"

    def _fingerprint(
        self,
        *,
        public: bytes | None = None,
        material: bytes | None = None,
        kid: str | None = None,
    ) -> str:
        data = public or material or (kid.encode("utf-8") if kid else b"")
        return hashlib.sha256(data).hexdigest()

    async def get_key_by_ref(
        self,
        key_ref: str,
        *,
        include_secret: bool = False,
    ) -> KeyRef:
        """Resolve simple URI-style key references into :class:`KeyRef` objects.

        Subclasses must implement provider-specific resolution logic.
        """

        raise NotImplementedError("get_key_by_ref must be implemented by subclasses")

    # ------------------------------------------------------------------
    def _split_path_params(self, spec: str) -> Tuple[Path, Dict[str, str]]:
        if "?" not in spec:
            return Path(os.path.expanduser(spec)), {}
        raw_path, raw_params = spec.split("?", 1)
        params = {
            k: v[0] for k, v in parse_qs(raw_params, keep_blank_values=True).items()
        }
        return Path(os.path.expanduser(raw_path)), params

    def _resolve_password(self, spec: Optional[str]) -> Optional[bytes]:
        if spec is None or spec == "":
            return None
        if spec.startswith("env:"):
            value = os.getenv(spec[4:])
            if value is None:
                raise ValueError(
                    f"Environment variable {spec[4:]} not set for password"
                )
            return value.encode("utf-8")
        if spec.startswith("literal:"):
            return spec[len("literal:") :].encode("utf-8")
        if spec.startswith("base64:"):
            return base64.b64decode(spec[len("base64:") :])
        return spec.encode("utf-8")

    def _build_keyref_from_private(
        self,
        private_key,
        chain,
        *,
        include_secret: bool,
        tags: Optional[Dict[str, str]] = None,
    ) -> KeyRef:
        public_bytes = private_key.public_key().public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        material: Optional[bytes] = None
        if include_secret:
            material = private_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        kid = self._fingerprint(public=public_bytes)
        chain_der = [cert.public_bytes(serialization.Encoding.DER) for cert in chain]
        key_type = self._infer_key_type(private_key)
        return KeyRef(
            kid=kid,
            version=1,
            type=key_type,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=(
                ExportPolicy.SECRET_WHEN_ALLOWED
                if include_secret
                else ExportPolicy.PUBLIC_ONLY
            ),
            material=material,
            public=public_bytes,
            tags={**(tags or {}), "chain_len": str(len(chain_der))}
            if tags
            else {"chain_len": str(len(chain_der))},
        )

    def _build_keyref_from_jwk(
        self,
        jwk: Dict[str, object],
        *,
        include_secret: bool,
    ) -> KeyRef:
        kid_hint = jwk.get("kid") if isinstance(jwk.get("kid"), str) else None
        key_type = self._infer_key_type_from_jwk(jwk)
        public_jwk = {
            k: v
            for k, v in jwk.items()
            if k not in {"d", "p", "q", "dp", "dq", "qi", "k"}
        }
        public_bytes = json.dumps(public_jwk, sort_keys=True).encode("utf-8")
        material: Optional[bytes] = None
        export_policy = ExportPolicy.PUBLIC_ONLY
        if include_secret:
            material = json.dumps(jwk, sort_keys=True).encode("utf-8")
            export_policy = ExportPolicy.SECRET_WHEN_ALLOWED
        kid = kid_hint or self._fingerprint(public=public_bytes)
        return KeyRef(
            kid=kid,
            version=1,
            type=key_type,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=export_policy,
            material=material,
            public=public_bytes,
            tags={"source": "jwk"},
        )

    def _infer_key_type(self, private_key) -> KeyType:
        if isinstance(private_key, rsa.RSAPrivateKey):
            return KeyType.RSA
        if isinstance(private_key, ec.EllipticCurvePrivateKey):
            return KeyType.EC
        if isinstance(private_key, ed25519.Ed25519PrivateKey):
            return KeyType.ED25519
        if isinstance(private_key, ed448.Ed448PrivateKey):
            return KeyType.ED25519
        return KeyType.OPAQUE

    def _infer_key_type_from_jwk(self, jwk: Dict[str, object]) -> KeyType:
        kty = jwk.get("kty")
        if kty == "RSA":
            return KeyType.RSA
        if kty == "EC":
            return KeyType.EC
        if kty in {"OKP", "OKP-Ed25519", "ED25519"}:
            return KeyType.ED25519
        if kty == "oct":
            return KeyType.SYMMETRIC
        return KeyType.OPAQUE
