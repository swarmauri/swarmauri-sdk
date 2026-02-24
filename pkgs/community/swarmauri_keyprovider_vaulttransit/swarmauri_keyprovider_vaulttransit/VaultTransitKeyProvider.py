"""HashiCorp Vault Transit key provider."""

from __future__ import annotations

import base64
import hashlib
import os
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Literal

try:  # pragma: no cover - import guard
    import hvac  # type: ignore
except Exception:  # pragma: no cover - no dependency during tests
    hvac = None

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519

from swarmauri_base.key_providers.KeyProviderBase import KeyProviderBase
from swarmauri_core.key_providers.types import KeyAlg, KeySpec, ExportPolicy
from swarmauri_core.crypto.types import KeyRef


__all__ = ["VaultTransitKeyProvider"]


def _b64u(b: bytes) -> str:
    """Encode bytes using URL-safe base64 without padding.

    b (bytes): The byte string to encode.
    RETURNS (str): The base64url representation.
    """
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def _pem_to_jwk(pem: bytes) -> dict:
    """Convert a PEM public key to a JWK dict.

    pem (bytes): The PEM-encoded public key.
    RETURNS (dict): The corresponding JWK representation.
    """
    pub = serialization.load_pem_public_key(pem)
    if isinstance(pub, rsa.RSAPublicKey):
        nums = pub.public_numbers()
        n = nums.n.to_bytes((nums.n.bit_length() + 7) // 8, "big")
        e = nums.e.to_bytes((nums.e.bit_length() + 7) // 8, "big")
        return {"kty": "RSA", "n": _b64u(n), "e": _b64u(e)}
    if isinstance(pub, ec.EllipticCurvePublicKey):
        curve = pub.curve
        nums = pub.public_numbers()
        if isinstance(curve, ec.SECP256R1):
            x = nums.x.to_bytes(32, "big")
            y = nums.y.to_bytes(32, "big")
            return {"kty": "EC", "crv": "P-256", "x": _b64u(x), "y": _b64u(y)}
        raise ValueError("Unsupported EC curve for JWKS export")
    if isinstance(pub, ed25519.Ed25519PublicKey):
        raw = pub.public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        return {"kty": "OKP", "crv": "Ed25519", "x": _b64u(raw)}
    raise ValueError("Unsupported public key type")


class VaultTransitKeyProvider(KeyProviderBase):
    """Key provider backed by HashiCorp Vault's Transit engine.

    Supports key creation, rotation, listing and JWKS export.
    """

    type: Literal["VaultTransitKeyProvider"] = "VaultTransitKeyProvider"

    def __init__(
        self,
        url: str,
        token: str,
        *,
        mount: str = "transit",
        namespace: Optional[str] = None,
        verify: bool | str = True,
        prefer_vault_rng: bool = True,
        client: Any | None = None,
    ) -> None:
        """Initialize the key provider.

        url (str): Base URL of the Vault server.
        token (str): Authentication token for Vault.
        mount (str): Path where the Transit engine is mounted.
        namespace (str or None): Optional Vault namespace.
        verify (bool or str): TLS verification settings.
        prefer_vault_rng (bool): Prefer Vault's RNG for random bytes.
        client (Any or None): Preconfigured hvac client to use.
        """
        super().__init__()
        if hvac is None and client is None:  # pragma: no cover - runtime guard
            raise ImportError(
                "hvac is required for VaultTransitKeyProvider (pip install hvac)"
            )
        self._client = client or hvac.Client(
            url=url, token=token, namespace=namespace, verify=verify
        )  # type: ignore[attr-defined]
        if not self._client.is_authenticated():
            raise RuntimeError(
                "VaultTransitKeyProvider: failed to authenticate to Vault"
            )
        self._mount = mount
        self._transit = self._client.secrets.transit
        self._prefer_vault_rng = prefer_vault_rng

    # ------------------------------------------------------------------
    def supports(self) -> Mapping[str, Iterable[str]]:
        """Describe supported key types, algorithms and features.

        RETURNS (Mapping[str, Iterable[str]]): Supported capabilities.
        """
        return {
            "class": ("sym", "asym"),
            "algs": (
                KeyAlg.AES256_GCM,
                KeyAlg.RSA_OAEP_SHA256,
                KeyAlg.RSA_PSS_SHA256,
                KeyAlg.ECDSA_P256_SHA256,
                KeyAlg.ED25519,
            ),
            "features": ("create", "rotate", "jwks", "non_exportable"),
        }

    # ------------------------------------------------------------------
    @staticmethod
    def _vault_type_for_alg(alg: KeyAlg) -> Tuple[str, str]:
        """Map a KeyAlg to Vault key type and purpose.

        alg (KeyAlg): The algorithm to map.
        RETURNS (Tuple[str, str]): Vault key type and purpose.
        """
        if alg == KeyAlg.AES256_GCM:
            return "aes256-gcm96", "encryption"
        if alg == KeyAlg.RSA_OAEP_SHA256:
            return "rsa-3072", "encryption"
        if alg == KeyAlg.RSA_PSS_SHA256:
            return "rsa-3072", "signing"
        if alg == KeyAlg.ECDSA_P256_SHA256:
            return "ecdsa-p256", "signing"
        if alg == KeyAlg.ED25519:
            return "ed25519", "signing"
        raise ValueError(f"Unsupported alg: {alg}")

    def _export_type_for_purpose(self, purpose: str) -> str:
        """Resolve Vault export type for a given key purpose.

        purpose (str): Either ``"encryption"`` or ``"signing"``.
        RETURNS (str): The corresponding export type.
        """
        if purpose == "encryption":
            return "encryption-key"
        if purpose == "signing":
            return "signing-key"
        raise ValueError("Unknown purpose")

    def _key_status(self, name: str) -> dict:
        """Fetch metadata for a key from Vault.

        name (str): The Vault key name.
        RETURNS (dict): Raw key status information.
        """
        res = self._transit.read_key(name=name, mount_point=self._mount)
        return res["data"]

    def _list_key_names(self) -> List[str]:
        """List all key names in the configured mount.

        RETURNS (List[str]): Available key identifiers.
        """
        res = self._transit.list_keys(mount_point=self._mount)
        return (res.get("data") or {}).get("keys", []) or []

    def _export_public_pem(
        self, name: str, version: Optional[int], purpose: str
    ) -> Optional[bytes]:
        """Export the PEM-encoded public key from Vault.

        name (str): The Vault key name.
        version (int or None): Specific key version or latest.
        purpose (str): Key purpose, ``"signing"`` or ``"encryption"``.
        RETURNS (bytes or None): The PEM public key if available.
        """
        export_type = self._export_type_for_purpose(purpose)
        try:
            res = self._transit.export_key(
                name=name,
                key_type=export_type,
                version=None if version is None else str(int(version)),
                mount_point=self._mount,
            )
            data = res.get("data") or {}
            keys = data.get("keys") or {}
            if version is None:
                if keys:
                    ver = max(int(v) for v in keys.keys())
                    val = keys.get(str(ver))
                else:
                    val = None
            else:
                val = keys.get(str(int(version)))
            if isinstance(val, str) and "BEGIN PUBLIC KEY" in val:
                return val.encode("utf-8")
        except Exception:  # pragma: no cover - soft failure
            pass
        try:
            status = self._key_status(name)
            keys = status.get("keys") or {}
            idx = str(version or status.get("latest_version"))
            entry = keys.get(idx) or {}
            val = entry.get("public_key")
            if isinstance(val, str) and "BEGIN PUBLIC KEY" in val:
                return val.encode("utf-8")
        except Exception:  # pragma: no cover
            pass
        return None

    # ------------------------------------------------------------------
    async def create_key(self, spec: KeySpec) -> KeyRef:
        """Create a new key in Vault.

        spec (KeySpec): Desired key specification.
        RETURNS (KeyRef): Reference to the created key.
        """
        vtype, purpose = self._vault_type_for_alg(spec.alg)
        name = (
            spec.label or f"k-{hashlib.sha256(os.urandom(16)).hexdigest()[:12]}"
        ).strip()
        self._transit.create_key(
            name=name,
            type=vtype,
            exportable=False,
            allow_plaintext_backup=False,
            mount_point=self._mount,
        )
        status = self._key_status(name)
        latest = int(status["latest_version"])
        public_pem = None
        if purpose in ("signing", "encryption") and spec.alg != KeyAlg.AES256_GCM:
            public_pem = self._export_public_pem(name, latest, purpose)
        return KeyRef(
            kid=name,
            version=latest,
            type="OPAQUE",
            uses=spec.uses,
            export_policy=ExportPolicy.NONE,
            public=public_pem,
            material=None,
            tags={
                "label": spec.label,
                "alg": spec.alg.value,
                "vault_mount": self._mount,
                "vault_type": vtype,
                "vault_purpose": purpose,
            },
            fingerprint=self._fingerprint(public=public_pem, kid=name),
        )

    async def import_key(
        self, spec: KeySpec, material: bytes, *, public: Optional[bytes] = None
    ) -> KeyRef:
        """Import a key into Vault.

        This provider does not support importing existing key material.

        spec (KeySpec): Specification of the key to import.
        material (bytes): Raw key material.
        public (bytes or None): Optional public portion of the key.
        RAISES (NotImplementedError): Always raised.
        """
        raise NotImplementedError(
            "VaultTransitKeyProvider.import_key is intentionally not supported"
        )

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ) -> KeyRef:
        """Rotate an existing key.

        kid (str): Identifier of the key to rotate.
        spec_overrides (dict or None): Optional override values.
        RETURNS (KeyRef): Reference to the rotated key version.
        """
        self._transit.rotate_key(name=kid, mount_point=self._mount)
        status = self._key_status(kid)
        latest = int(status["latest_version"])
        purpose = "signing"
        public_pem = None
        for p in ("signing", "encryption"):
            public_pem = self._export_public_pem(kid, latest, p)
            if public_pem:
                purpose = p
                break
        return KeyRef(
            kid=kid,
            version=latest,
            type="OPAQUE",
            uses=(),
            export_policy=ExportPolicy.NONE,
            public=public_pem,
            material=None,
            tags={
                "vault_mount": self._mount,
                "vault_purpose": purpose,
            },
            fingerprint=self._fingerprint(public=public_pem, kid=kid),
        )

    async def destroy_key(self, kid: str, version: Optional[int] = None) -> bool:
        """Destroy a key or specific key version.

        kid (str): Key identifier.
        version (int or None): Specific version to destroy or all versions.
        RETURNS (bool): ``True`` when the operation succeeds.
        """
        if version is None:
            self._transit.delete_key(name=kid, mount_point=self._mount)
            return True
        self._transit.destroy_key(
            name=kid, versions=[int(version)], mount_point=self._mount
        )
        return True

    async def get_key(
        self, kid: str, version: Optional[int] = None, *, include_secret: bool = False
    ) -> KeyRef:
        """Retrieve a key reference from Vault.

        kid (str): Key identifier.
        version (int or None): Desired version or latest.
        include_secret (bool): Unused, kept for interface parity.
        RETURNS (KeyRef): Reference describing the key.
        """
        status = self._key_status(kid)
        latest = int(status["latest_version"])
        ver = int(version or latest)
        public_pem = None
        purpose_detected = None
        for p in ("signing", "encryption"):
            public_pem = self._export_public_pem(kid, ver, p)
            if public_pem:
                purpose_detected = p
                break
        return KeyRef(
            kid=kid,
            version=ver,
            type="OPAQUE",
            uses=(),
            export_policy=ExportPolicy.NONE,
            public=public_pem,
            material=None,
            tags={
                "vault_mount": self._mount,
                "vault_purpose": purpose_detected,
                "latest_version": latest,
            },
            fingerprint=self._fingerprint(public=public_pem, kid=kid),
        )

    async def list_versions(self, kid: str) -> Tuple[int, ...]:
        """List available versions for a key.

        kid (str): Key identifier.
        RETURNS (Tuple[int, ...]): Sorted tuple of version numbers.
        """
        status = self._key_status(kid)
        keys = status.get("keys") or {}
        return tuple(sorted(int(v) for v in keys.keys()))

    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        """Export a public key in JWK format.

        kid (str): Key identifier.
        version (int or None): Specific version or latest.
        RETURNS (dict): JSON Web Key representation.
        """
        ref = await self.get_key(kid, version)
        if isinstance(ref.public, (bytes, bytearray)):
            jwk = _pem_to_jwk(bytes(ref.public))
            jwk["kid"] = f"{ref.kid}.{ref.version}"
            return jwk
        return {"kty": "oct", "alg": "A256GCM", "kid": f"{ref.kid}.{ref.version}"}

    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        """Return a JWKS document with all available keys.

        prefix_kids (str or None): Optional prefix filter for key IDs.
        RETURNS (dict): JWKS containing available public keys.
        """
        out: List[dict] = []
        try:
            names = self._list_key_names()
        except Exception:  # pragma: no cover
            names = []
        for name in names:
            if prefix_kids and not str(name).startswith(prefix_kids):
                continue
            try:
                status = self._key_status(name)
                latest = int(status.get("latest_version", 1))
                jwk = await self.get_public_jwk(name, latest)
                out.append(jwk)
            except Exception:  # pragma: no cover
                continue
        return {"keys": out}

    async def random_bytes(self, n: int) -> bytes:
        """Generate cryptographically secure random bytes.

        n (int): Number of bytes to generate.
        RETURNS (bytes): Random byte string.
        """
        if self._prefer_vault_rng:
            try:
                res = self._client.sys.generate_random_bytes(n_bytes=n)
                data = res.get("data") or {}
                b64 = data.get("random_bytes")
                if b64:
                    return base64.b64decode(b64)
            except Exception:  # pragma: no cover
                pass
        return os.urandom(n)

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        """Derive key material using HKDF-SHA256.

        ikm (bytes): Input keying material.
        salt (bytes): HKDF salt value.
        info (bytes): Contextual information.
        length (int): Length of derived key.
        RETURNS (bytes): Derived key bytes.
        """
        return HKDF(
            algorithm=hashes.SHA256(), length=length, salt=salt, info=info
        ).derive(ikm)
