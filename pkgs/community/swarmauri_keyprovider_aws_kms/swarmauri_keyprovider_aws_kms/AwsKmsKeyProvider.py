from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional, Tuple, Literal

try:
    import boto3
    from botocore.exceptions import ClientError
except Exception as e:  # pragma: no cover
    raise ImportError(
        "AwsKmsKeyProvider requires 'boto3'. Install with: pip install boto3"
    ) from e

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec

from swarmauri_base.keys.KeyProviderBase import KeyProviderBase
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse
from swarmauri_core.crypto.types import KeyRef


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


@dataclass(frozen=True)
class _KmsSpec:
    KeySpec: str
    KeyUsage: str


class AwsKmsKeyProvider(KeyProviderBase):
    """
    AWS KMS-backed KeyProvider.

    - Creates new KMS CMKs per (kid, version); maintains stable alias:
        alias/<alias_prefix>/<kid>          -> latest version
        alias/<alias_prefix>/<kid>/v<ver>   -> specific version
    - Rotation = create new KMS key (same alg/usage), bump /vN alias, repoint "latest".
    - get_key(include_secret=...) never returns private material (KMS non-exportable).
    - get_public_jwk() parses GetPublicKey DER to RFC 7517 JWK.
    - jwks() publishes latest per 'kid' (resolved via stable alias) with kid.version.

    IAM needed (minimum):
      kms:CreateKey, kms:CreateAlias, kms:UpdateAlias, kms:ListAliases,
      kms:DescribeKey, kms:ListResourceTags, kms:GetPublicKey, kms:ScheduleKeyDeletion
    """

    type: Literal["AwsKmsKeyProvider"] = "AwsKmsKeyProvider"

    def __init__(
        self,
        *,
        region: str,
        alias_prefix: str = "swarmauri",
        key_policy: Optional[dict] = None,
    ):
        """
        region: AWS region name (e.g., "us-east-1")
        alias_prefix: alias namespace (no 'alias/' prefix here). Final aliases look like:
                      'alias/<alias_prefix>/<kid>' and 'alias/<alias_prefix>/<kid>/v<ver>'
        key_policy: optional explicit key policy JSON; if None, KMS uses account default.
        """
        super().__init__()
        self._region = region
        self._alias_prefix = alias_prefix.strip("/")

        self._kms = boto3.client("kms", region_name=region)
        self._key_policy = key_policy

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {
            "class": ("sym", "asym"),
            "algs": (
                KeyAlg.AES256_GCM,
                KeyAlg.RSA_OAEP_SHA256,
                KeyAlg.RSA_PSS_SHA256,
                KeyAlg.ECDSA_P256_SHA256,
            ),
            "features": ("rotate", "jwks", "non_exportable"),
        }

    def _gen_kid(self) -> str:
        return hashlib.sha256(os.urandom(16)).hexdigest()[:16]

    def _alias_latest(self, kid: str) -> str:
        return f"alias/{self._alias_prefix}/{kid}"

    def _alias_version(self, kid: str, version: int) -> str:
        return f"alias/{self._alias_prefix}/{kid}/v{version}"

    def _create_or_update_alias(self, alias_name: str, target_key_id: str) -> None:
        try:
            self._kms.create_alias(AliasName=alias_name, TargetKeyId=target_key_id)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "AlreadyExistsException":
                self._kms.update_alias(AliasName=alias_name, TargetKeyId=target_key_id)
            else:
                raise

    def _kms_spec_for_alg(self, spec: KeySpec) -> _KmsSpec:
        if spec.klass == KeyClass.symmetric:
            if spec.alg != KeyAlg.AES256_GCM:
                raise ValueError(f"Unsupported symmetric alg for AWS KMS: {spec.alg}")
            return _KmsSpec(KeySpec="SYMMETRIC_DEFAULT", KeyUsage="ENCRYPT_DECRYPT")

        if spec.alg == KeyAlg.RSA_OAEP_SHA256:
            bits = spec.size_bits or 3072
            if bits not in (2048, 3072, 4096):
                raise ValueError("AWS KMS RSA supports 2048/3072/4096 bit sizes")
            return _KmsSpec(KeySpec=f"RSA_{bits}", KeyUsage="ENCRYPT_DECRYPT")

        if spec.alg == KeyAlg.RSA_PSS_SHA256:
            bits = spec.size_bits or 3072
            if bits not in (2048, 3072, 4096):
                raise ValueError("AWS KMS RSA supports 2048/3072/4096 bit sizes")
            return _KmsSpec(KeySpec=f"RSA_{bits}", KeyUsage="SIGN_VERIFY")

        if spec.alg == KeyAlg.ECDSA_P256_SHA256:
            return _KmsSpec(KeySpec="ECC_NIST_P256", KeyUsage="SIGN_VERIFY")

        raise ValueError(f"Unsupported alg for AWS KMS: {spec.alg}")

    def _get_tags(self, key_id: str) -> Dict[str, str]:
        out: Dict[str, str] = {}
        paginator = self._kms.get_paginator("list_resource_tags")
        for page in paginator.paginate(KeyId=key_id):
            for t in page.get("Tags", []):
                out[t["TagKey"]] = t["TagValue"]
        return out

    def _public_jwk_from_der(self, der: bytes, jwk_kid: str) -> dict:
        pk = serialization.load_der_public_key(der)
        if isinstance(pk, rsa.RSAPublicKey):
            nums = pk.public_numbers()
            n = nums.n.to_bytes((nums.n.bit_length() + 7) // 8, "big")
            e = nums.e.to_bytes((nums.e.bit_length() + 7) // 8, "big")
            return {"kty": "RSA", "n": _b64u(n), "e": _b64u(e), "kid": jwk_kid}
        if isinstance(pk, ec.EllipticCurvePublicKey):
            curve = pk.curve
            if isinstance(curve, ec.SECP256R1):
                nums = pk.public_numbers()
                x = nums.x.to_bytes(32, "big")
                y = nums.y.to_bytes(32, "big")
                return {
                    "kty": "EC",
                    "crv": "P-256",
                    "x": _b64u(x),
                    "y": _b64u(y),
                    "kid": jwk_kid,
                }
        raise ValueError("Unsupported public key type returned by KMS")

    def _keyref_from_key_id(
        self,
        kid: str,
        version: int,
        key_id: str,
        *,
        tags: Optional[Dict[str, str]] = None,
    ) -> KeyRef:
        public: Optional[bytes] = None
        try:
            resp = self._kms.get_public_key(KeyId=key_id)
            der = resp.get("PublicKey")
            if der:
                public = serialization.load_der_public_key(der).public_bytes(
                    serialization.Encoding.PEM,
                    serialization.PublicFormat.SubjectPublicKeyInfo,
                )
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code not in (
                "UnsupportedOperationException",
                "NotFoundException",
                "InvalidArnException",
                "IncorrectKeySpecException",
            ):
                raise

        uses: Tuple[KeyUse, ...] = (KeyUse.encrypt, KeyUse.decrypt)
        try:
            md = self._kms.describe_key(KeyId=key_id)["KeyMetadata"]
            if md.get("KeyUsage") == "SIGN_VERIFY":
                uses = (KeyUse.sign, KeyUse.verify)
            elif md.get("KeyUsage") == "ENCRYPT_DECRYPT":
                uses = (KeyUse.encrypt, KeyUse.decrypt)
        except Exception:
            pass

        tag_map = dict(tags or {})
        return KeyRef(
            kid=kid,
            version=version,
            type="OPAQUE",
            uses=uses,
            export_policy=ExportPolicy.never_export_secret,
            public=public,
            material=None,
            tags={
                "alg": tag_map.get("saur:alg"),
                "kms:key_id": key_id,
                "kms:region": self._region,
                "label": tag_map.get("saur:label"),
            },
            fingerprint=self._fingerprint(public=public, kid=kid),
        )

    async def create_key(self, spec: KeySpec) -> KeyRef:
        kid = self._gen_kid()
        version = 1
        kms_spec = self._kms_spec_for_alg(spec)

        kwargs = {
            "KeyUsage": kms_spec.KeyUsage,
            "KeySpec": kms_spec.KeySpec,
            "Tags": [
                {"TagKey": "saur:kid", "TagValue": kid},
                {"TagKey": "saur:version", "TagValue": str(version)},
                {"TagKey": "saur:alg", "TagValue": spec.alg.value},
            ],
        }
        if spec.label:
            kwargs["Tags"].append({"TagKey": "saur:label", "TagValue": spec.label})
        if self._key_policy:
            kwargs["Policy"] = self._key_policy

        resp = self._kms.create_key(**kwargs)
        key_id = resp["KeyMetadata"]["KeyId"]

        self._create_or_update_alias(self._alias_version(kid, version), key_id)
        self._create_or_update_alias(self._alias_latest(kid), key_id)

        tags = {t["TagKey"]: t["TagValue"] for t in kwargs["Tags"]}
        return self._keyref_from_key_id(kid, version, key_id, tags=tags)

    async def import_key(
        self, spec: KeySpec, material: bytes, *, public: Optional[bytes] = None
    ) -> KeyRef:
        raise NotImplementedError(
            "AWS KMS does not support importing private keys via this provider; use create_key()."
        )

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ) -> KeyRef:
        latest_alias = self._alias_latest(kid)
        try:
            alias_desc = self._find_alias(latest_alias)
        except KeyError:
            raise KeyError(f"Unknown kid: {kid}")

        current_key_id = alias_desc["TargetKeyId"]
        current_tags = self._get_tags(current_key_id)
        current_alg = current_tags.get("saur:alg")
        if not current_alg:
            raise RuntimeError("Missing 'saur:alg' tag on current KMS key")

        alg = KeyAlg(current_alg)
        size_bits = (spec_overrides or {}).get("size_bits")
        label = (spec_overrides or {}).get("label", current_tags.get("saur:label"))
        uses = ()
        new_spec = KeySpec(
            klass=(
                KeyClass.symmetric if alg == KeyAlg.AES256_GCM else KeyClass.asymmetric
            ),
            alg=alg,
            size_bits=size_bits,
            label=label,
            export_policy=ExportPolicy.never_export_secret,
            uses=uses,
            tags=None,
        )

        try:
            versions = await self.list_versions(kid)
            next_version = (max(versions) + 1) if versions else 2
        except Exception:
            v = int(current_tags.get("saur:version", "1"))
            next_version = v + 1

        kms_spec = self._kms_spec_for_alg(new_spec)
        kwargs = {
            "KeyUsage": kms_spec.KeyUsage,
            "KeySpec": kms_spec.KeySpec,
            "Tags": [
                {"TagKey": "saur:kid", "TagValue": kid},
                {"TagKey": "saur:version", "TagValue": str(next_version)},
                {"TagKey": "saur:alg", "TagValue": alg.value},
            ],
        }
        if label:
            kwargs["Tags"].append({"TagKey": "saur:label", "TagValue": label})
        if self._key_policy:
            kwargs["Policy"] = self._key_policy

        resp = self._kms.create_key(**kwargs)
        new_key_id = resp["KeyMetadata"]["KeyId"]

        self._create_or_update_alias(self._alias_version(kid, next_version), new_key_id)
        self._create_or_update_alias(self._alias_latest(kid), new_key_id)

        return self._keyref_from_key_id(
            kid,
            next_version,
            new_key_id,
            tags={t["TagKey"]: t["TagValue"] for t in kwargs["Tags"]},
        )

    async def destroy_key(self, kid: str, version: Optional[int] = None) -> bool:
        try:
            if version is None:
                for ver in await self.list_versions(kid):
                    alias_name = self._alias_version(kid, ver)
                    alias_desc = self._find_alias(alias_name)
                    self._kms.schedule_key_deletion(
                        KeyId=alias_desc["TargetKeyId"], PendingWindowInDays=7
                    )
                return True
            else:
                alias_name = self._alias_version(kid, version)
                alias_desc = self._find_alias(alias_name)
                self._kms.schedule_key_deletion(
                    KeyId=alias_desc["TargetKeyId"], PendingWindowInDays=7
                )
                return True
        except Exception:
            return False

    async def get_key(
        self, kid: str, version: Optional[int] = None, *, include_secret: bool = False
    ) -> KeyRef:
        alias_name = (
            self._alias_version(kid, version) if version else self._alias_latest(kid)
        )
        alias_desc = self._find_alias(alias_name)
        key_id = alias_desc["TargetKeyId"]

        tags = self._get_tags(key_id)
        ver = int(tags.get("saur:version") or (version or 1))
        return self._keyref_from_key_id(kid, ver, key_id, tags=tags)

    async def list_versions(self, kid: str) -> Tuple[int, ...]:
        prefix = f"alias/{self._alias_prefix}/{kid}/v"
        out: list[int] = []
        paginator = self._kms.get_paginator("list_aliases")
        for page in paginator.paginate():
            for a in page.get("Aliases", []):
                name = a.get("AliasName")
                if not name or not name.startswith(prefix):
                    continue
                tail = name[len(prefix) :]
                if tail.isdigit():
                    out.append(int(tail))
        if not out:
            try:
                self._find_alias(self._alias_latest(kid))
                out = [1]
            except KeyError:
                pass
        out.sort()
        return tuple(out)

    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        alias_name = (
            self._alias_version(kid, version) if version else self._alias_latest(kid)
        )
        alias_desc = self._find_alias(alias_name)
        key_id = alias_desc["TargetKeyId"]

        tags = self._get_tags(key_id)
        ver = int(tags.get("saur:version") or (version or 1))
        jwk_kid = f"{kid}.{ver}"

        try:
            pk = self._kms.get_public_key(KeyId=key_id).get("PublicKey")
            if not pk:
                return {"kty": "oct", "alg": "A256GCM", "kid": jwk_kid}
            return self._public_jwk_from_der(pk, jwk_kid)
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code in ("UnsupportedOperationException", "IncorrectKeySpecException"):
                return {"kty": "oct", "alg": "A256GCM", "kid": jwk_kid}
            raise

    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        keys = []
        base_prefix = f"alias/{self._alias_prefix}/"
        paginator = self._kms.get_paginator("list_aliases")
        seen_latest: set[str] = set()
        for page in paginator.paginate():
            for a in page.get("Aliases", []):
                name = a.get("AliasName") or ""
                if not name.startswith(base_prefix):
                    continue
                tail = name[len(base_prefix) :]
                if "/v" in tail:
                    continue
                kid = tail
                if prefix_kids and not kid.startswith(prefix_kids):
                    continue
                if kid in seen_latest:
                    continue
                seen_latest.add(kid)
                try:
                    key_id = a["TargetKeyId"]
                    tags = self._get_tags(key_id)
                    ver = int(tags.get("saur:version", "1"))
                    jwk = await self.get_public_jwk(kid, ver)
                    keys.append(jwk)
                except Exception:
                    continue
        return {"keys": keys}

    async def random_bytes(self, n: int) -> bytes:
        return os.urandom(n)

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        from cryptography.hazmat.primitives import hashes

        return HKDF(
            algorithm=hashes.SHA256(), length=length, salt=salt, info=info
        ).derive(ikm)

    def _find_alias(self, alias_name: str) -> dict:
        paginator = self._kms.get_paginator("list_aliases")
        for page in paginator.paginate():
            for a in page.get("Aliases", []):
                if a.get("AliasName") == alias_name and "TargetKeyId" in a:
                    return a
        raise KeyError(f"Alias not found or no target: {alias_name}")
