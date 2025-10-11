from __future__ import annotations

from typing import Callable, Dict, Iterable, Optional, Tuple, Literal
import base64
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import parse_qs

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.crypto.types import (
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider


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
        chain: Iterable[object] | None,
        *,
        include_secret: bool,
        tags: Optional[Dict[str, str]] = None,
        key_type: KeyType | None = None,
        export_public: Callable[[object], Optional[bytes]] | None = None,
        export_private: Callable[[object], Optional[bytes]] | None = None,
        export_chain: Callable[[object], Optional[bytes]] | None = None,
    ) -> KeyRef:
        """Construct a :class:`KeyRef` from provider-specific key material.

        Parameters
        ----------
        private_key:
            Provider-specific handle to the private key. Downstream providers
            SHOULD supply ``export_public``/``export_private`` callables when the
            object cannot be expressed without third-party dependencies.
        chain:
            Optional iterable describing the certificate chain or related
            metadata. Items are expected to already be ``bytes`` objects unless
            ``export_chain`` is provided.
        include_secret:
            When ``True`` the resulting :class:`KeyRef` will contain private key
            material. Providers MUST supply ``export_private`` if the private
            material is not directly representable without additional
            dependencies.
        tags:
            Additional tags to merge into the returned :class:`KeyRef`.
        key_type:
            Explicit key type override. When omitted ``_infer_key_type`` is used
            which defaults to :class:`KeyType.OPAQUE` for unknown structures.
        export_public / export_private / export_chain:
            Optional callables responsible for turning provider specific objects
            into ``bytes``. They allow downstream implementations to keep the
            serialization logic (and any third-party imports) out of the base
            class.
        """

        public_bytes = self._resolve_public_bytes(
            private_key, export_public=export_public
        )
        material: Optional[bytes] = None
        if include_secret:
            material = self._resolve_private_bytes(
                private_key, export_private=export_private
            )
        chain_bytes = self._resolve_chain_bytes(chain, export_chain=export_chain)

        kid = self._fingerprint(public=public_bytes, material=material)
        resolved_key_type = key_type or self._infer_key_type(private_key)
        export_policy = (
            ExportPolicy.SECRET_WHEN_ALLOWED
            if include_secret and material is not None
            else ExportPolicy.PUBLIC_ONLY
        )
        merged_tags = {"chain_len": str(len(chain_bytes))}
        if tags:
            merged_tags.update(tags)

        return KeyRef(
            kid=kid,
            version=1,
            type=resolved_key_type,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=export_policy,
            material=material,
            public=public_bytes,
            tags=merged_tags,
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
        if isinstance(private_key, dict):
            hint = private_key.get("kty") or private_key.get("type")
            if isinstance(hint, str):
                normalized = hint.upper()
                if normalized == "RSA":
                    return KeyType.RSA
                if normalized in {"EC", "ECDSA", "ELLIPTIC"}:
                    return KeyType.EC
                if normalized in {"ED25519", "OKP", "OKP-ED25519"}:
                    return KeyType.ED25519
                if normalized == "OCT":
                    return KeyType.SYMMETRIC
        return KeyType.OPAQUE

    # ------------------------------------------------------------------
    def _resolve_public_bytes(
        self,
        private_key,
        *,
        export_public: Callable[[object], Optional[bytes]] | None = None,
    ) -> Optional[bytes]:
        if export_public is not None:
            result = export_public(private_key)
            return self._coerce_to_bytes(result, allow_none=True)
        if isinstance(private_key, dict):
            if "public" in private_key:
                return self._coerce_to_bytes(private_key["public"], allow_none=True)
            if "pub" in private_key:
                return self._coerce_to_bytes(private_key["pub"], allow_none=True)
        if isinstance(private_key, (bytes, bytearray, memoryview)):
            return None
        raise NotImplementedError(
            "Provide export_public to serialize provider-specific key objects"
        )

    def _resolve_private_bytes(
        self,
        private_key,
        *,
        export_private: Callable[[object], Optional[bytes]] | None = None,
    ) -> Optional[bytes]:
        if export_private is not None:
            result = export_private(private_key)
            return self._coerce_to_bytes(result, allow_none=True)
        if isinstance(private_key, dict):
            if "private" in private_key:
                return self._coerce_to_bytes(private_key["private"], allow_none=True)
            if "secret" in private_key:
                return self._coerce_to_bytes(private_key["secret"], allow_none=True)
        if isinstance(private_key, (bytes, bytearray, memoryview)):
            return bytes(private_key)
        raise NotImplementedError(
            "Provide export_private to serialize provider-specific key objects"
        )

    def _resolve_chain_bytes(
        self,
        chain: Iterable[object] | None,
        *,
        export_chain: Callable[[object], Optional[bytes]] | None = None,
    ) -> Tuple[bytes, ...]:
        if not chain:
            return ()
        resolved: list[bytes] = []
        for item in chain:
            value = None
            if export_chain is not None:
                value = export_chain(item)
            else:
                try:
                    value = self._coerce_to_bytes(item, allow_none=True)
                except TypeError as exc:  # pragma: no cover - defensive
                    raise NotImplementedError(
                        "Provide export_chain to serialize chain entries"
                    ) from exc
            if value is not None:
                resolved.append(value)
        return tuple(resolved)

    def _coerce_to_bytes(
        self, value: object, *, allow_none: bool = False
    ) -> Optional[bytes]:
        if value is None:
            if allow_none:
                return None
            raise TypeError("Cannot coerce None to bytes without allow_none")
        if isinstance(value, (bytes, bytearray, memoryview)):
            return bytes(value)
        if isinstance(value, str):
            return value.encode("utf-8")
        if isinstance(value, dict):
            return json.dumps(value, sort_keys=True).encode("utf-8")
        raise TypeError(
            "Unable to coerce value to bytes; supply an explicit export callable"
        )

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
