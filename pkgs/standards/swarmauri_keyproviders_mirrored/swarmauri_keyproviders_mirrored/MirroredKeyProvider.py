from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Iterable, Literal, Mapping, Optional, Tuple

from swarmauri_base.keys.KeyProviderBase import KeyProviderBase
from swarmauri_core.keys.IKeyProvider import IKeyProvider
from swarmauri_core.keys.types import ExportPolicy, KeyAlg, KeyClass, KeySpec
from swarmauri_core.crypto.types import KeyRef

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class _ShadowRef:
    """Mapping from a primary (kid,version) to a secondary (kid,version)."""

    sec_kid: str
    sec_version: int


class MirroredKeyProvider(KeyProviderBase):
    """Mirror/Failover key provider.

    Primary is the system of record. Secondary is best-effort replication:
      - mirror_mode="full"         → replicate private material when policy allows
      - mirror_mode="public_only"  → replicate only public JWK/PEM (verification)
      - mirror_mode="none"         → no replication, but reads may failover

    Reads:
      - get_key/get_public_jwk: primary first; on failure (or missing), try secondary
      - jwks(): union (primary dominates on kid collisions)

    Writes:
      - create/import/rotate/destroy: do primary first; if ok, attempt to mirror
        and record (kid,version) → (sec_kid,sec_version) mapping. Mapping is used
        for destroy/version lookups on the secondary.

    Notes:
      - We never *require* secrets from primary to mirror. If policy forbids
        export, we still mirror public material (when available).
      - list_versions() comes from primary. If primary is unavailable, we try
        secondary (best effort).
      - This class is process-memory stateful (mapping). Persist externally if
        you need cross-process coherence.
    """

    type: Literal["MirroredKeyProvider"] = "MirroredKeyProvider"

    def __init__(
        self,
        primary: IKeyProvider,
        secondary: IKeyProvider,
        *,
        mirror_mode: Literal["full", "public_only", "none"] = "public_only",
        fail_open_reads: bool = True,
    ) -> None:
        super().__init__()
        self._p = primary
        self._s = secondary
        self._mode = mirror_mode
        self._fail_open_reads = fail_open_reads
        # {(kid -> {version -> _ShadowRef})}
        self._shadow: Dict[str, Dict[int, _ShadowRef]] = {}

    def supports(self) -> Mapping[str, Iterable[str]]:
        """Combine capabilities from primary and secondary."""
        try:
            p = self._p.supports()
        except Exception:
            p = {}
        try:
            s = self._s.supports()
        except Exception:
            s = {}

        def _u(k: str) -> Tuple[str, ...]:
            up = tuple(map(str, p.get(k, ())))
            us = tuple(map(str, s.get(k, ())))
            return tuple(dict.fromkeys([*up, *us]))

        feats = list(
            dict.fromkeys([*(p.get("features", ())), *(s.get("features", ()))])
        )
        feats.extend(["mirror", f"mirror:{self._mode}", "failover"])
        return {
            "class": _u("class"),
            "algs": _u("algs"),
            "features": tuple(dict.fromkeys(feats)),
        }

    def _set_shadow(self, kid: str, version: int, sec: KeyRef) -> None:
        self._shadow.setdefault(kid, {})[version] = _ShadowRef(
            sec_kid=sec.kid, sec_version=sec.version
        )

    def _get_shadow(self, kid: str, version: int) -> Optional[_ShadowRef]:
        return self._shadow.get(kid, {}).get(version)

    async def _mirror_created(
        self, spec: KeySpec, primary_ref: KeyRef, *, imported_material: Optional[bytes]
    ) -> Optional[KeyRef]:
        """Mirror a freshly created or imported key."""
        if self._mode == "none":
            return None
        try:
            if self._mode == "public_only":
                if primary_ref.public:
                    sec_ref = await self._s.import_key(
                        KeySpec(
                            klass=KeyClass.asymmetric,
                            alg=KeyAlg(primary_ref.tags["alg"]),
                            size_bits=None,
                            label=primary_ref.tags.get("label"),
                            export_policy=ExportPolicy.PUBLIC_ONLY,
                            uses=tuple(primary_ref.uses),
                            tags={**primary_ref.tags, "mirrored": True},
                        ),
                        material=b"",
                        public=primary_ref.public,
                    )
                    self._set_shadow(primary_ref.kid, primary_ref.version, sec_ref)
                    return sec_ref
                return None
            if self._mode == "full":
                if imported_material:
                    sec_ref = await self._s.import_key(
                        KeySpec(
                            klass=KeyClass.symmetric
                            if primary_ref.public is None
                            else KeyClass.asymmetric,
                            alg=KeyAlg(primary_ref.tags["alg"]),
                            size_bits=None,
                            label=primary_ref.tags.get("label"),
                            export_policy=primary_ref.export_policy,
                            uses=tuple(primary_ref.uses),
                            tags={**primary_ref.tags, "mirrored": True},
                        ),
                        material=imported_material,
                        public=primary_ref.public,
                    )
                    self._set_shadow(primary_ref.kid, primary_ref.version, sec_ref)
                    return sec_ref
                if primary_ref.public:
                    sec_ref = await self._s.import_key(
                        KeySpec(
                            klass=KeyClass.asymmetric,
                            alg=KeyAlg(primary_ref.tags["alg"]),
                            size_bits=None,
                            label=primary_ref.tags.get("label"),
                            export_policy=ExportPolicy.PUBLIC_ONLY,
                            uses=tuple(primary_ref.uses),
                            tags={
                                **primary_ref.tags,
                                "mirrored": True,
                                "mirror_mode": "public_only_fallback",
                            },
                        ),
                        material=b"",
                        public=primary_ref.public,
                    )
                    self._set_shadow(primary_ref.kid, primary_ref.version, sec_ref)
                    return sec_ref
                return None
        except Exception as e:  # best-effort
            log.warning(
                "MirroredKeyProvider: secondary mirror failed for %s.%s (%s)",
                primary_ref.kid,
                primary_ref.version,
                e,
                exc_info=True,
            )
            return None

    async def create_key(self, spec: KeySpec) -> KeyRef:
        pref = await self._p.create_key(spec)
        material: Optional[bytes] = None
        try:
            if spec.export_policy == ExportPolicy.SECRET_WHEN_ALLOWED:
                got = await self._p.get_key(pref.kid, pref.version, include_secret=True)
                material = got.material
        except Exception:
            material = None
        await self._mirror_created(spec, pref, imported_material=material)
        return pref

    async def import_key(
        self, spec: KeySpec, material: bytes, *, public: Optional[bytes] = None
    ) -> KeyRef:
        pref = await self._p.import_key(spec, material, public=public)
        await self._mirror_created(spec, pref, imported_material=material)
        return pref

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ) -> KeyRef:
        pref = await self._p.rotate_key(kid, spec_overrides=spec_overrides)
        material: Optional[bytes] = None
        try:
            got = await self._p.get_key(pref.kid, pref.version, include_secret=True)
            material = got.material
        except Exception:
            material = None
        await self._mirror_created(
            KeySpec(
                klass=KeyClass.symmetric
                if pref.public is None
                else KeyClass.asymmetric,
                alg=KeyAlg(pref.tags["alg"]),
                size_bits=(spec_overrides or {}).get("size_bits")
                if spec_overrides
                else None,
                label=pref.tags.get("label"),
                export_policy=pref.export_policy,
                uses=tuple(pref.uses),
                tags=pref.tags,
            ),
            pref,
            imported_material=material,
        )
        return pref

    async def destroy_key(self, kid: str, version: Optional[int] = None) -> bool:
        ok = await self._p.destroy_key(kid, version)
        if version is None:
            for v, sref in list(self._shadow.get(kid, {}).items()):
                try:
                    await self._s.destroy_key(sref.sec_kid, sref.sec_version)
                except Exception:
                    pass
            self._shadow.pop(kid, None)
        else:
            shadow = self._get_shadow(kid, version)
            if shadow:
                try:
                    await self._s.destroy_key(shadow.sec_kid, shadow.sec_version)
                except Exception:
                    pass
                self._shadow.get(kid, {}).pop(version, None)
                if not self._shadow.get(kid):
                    self._shadow.pop(kid, None)
        return ok

    async def get_key(
        self, kid: str, version: Optional[int] = None, *, include_secret: bool = False
    ) -> KeyRef:
        try:
            return await self._p.get_key(kid, version, include_secret=include_secret)
        except Exception as e:
            if not self._fail_open_reads:
                raise
            log.warning(
                "MirroredKeyProvider: primary get_key failed for %s.%s (%s); failing over",
                kid,
                version,
                e,
            )
            if version is not None:
                sref = self._get_shadow(kid, version)
                if sref:
                    return await self._s.get_key(
                        sref.sec_kid, sref.sec_version, include_secret=include_secret
                    )
            return await self._s.get_key(kid, version, include_secret=include_secret)

    async def list_versions(self, kid: str) -> Tuple[int, ...]:
        try:
            return await self._p.list_versions(kid)
        except Exception as e:
            if not self._fail_open_reads:
                raise
            log.warning(
                "MirroredKeyProvider: primary list_versions failed for %s (%s); trying secondary",
                kid,
                e,
            )
            return await self._s.list_versions(kid)

    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        try:
            return await self._p.get_public_jwk(kid, version)
        except Exception as e:
            if not self._fail_open_reads:
                raise
            log.warning(
                "MirroredKeyProvider: primary get_public_jwk failed for %s.%s (%s); failing over",
                kid,
                version,
                e,
            )
            if version is not None:
                sref = self._get_shadow(kid, version)
                if sref:
                    return await self._s.get_public_jwk(sref.sec_kid, sref.sec_version)
            return await self._s.get_public_jwk(kid, version)

    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        try:
            p = await self._p.jwks(prefix_kids=prefix_kids)  # type: ignore[arg-type]
        except TypeError:
            p = await self._p.jwks()
        except Exception as e:
            if not self._fail_open_reads:
                raise
            log.warning(
                "MirroredKeyProvider: primary jwks failed (%s); using secondary only", e
            )
            try:
                s = await self._s.jwks(prefix_kids=prefix_kids)  # type: ignore[arg-type]
            except TypeError:
                s = await self._s.jwks()
            return s
        try:
            s = await self._s.jwks(prefix_kids=prefix_kids)  # type: ignore[arg-type]
        except TypeError:
            s = await self._s.jwks()
        except Exception:
            return p
        by_kid: Dict[str, dict] = {}
        for jwk in s.get("keys", []):
            kid = jwk.get("kid")
            if kid:
                by_kid[kid] = jwk
        for jwk in p.get("keys", []):
            kid = jwk.get("kid")
            if kid:
                by_kid[kid] = jwk
        return {"keys": list(by_kid.values())}

    async def random_bytes(self, n: int) -> bytes:
        try:
            return await self._p.random_bytes(n)
        except Exception as e:
            if not self._fail_open_reads:
                raise
            log.warning(
                "MirroredKeyProvider: primary random_bytes failed (%s); using secondary",
                e,
            )
            return await self._s.random_bytes(n)

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        try:
            return await self._p.hkdf(ikm, salt=salt, info=info, length=length)
        except Exception as e:
            if not self._fail_open_reads:
                raise
            log.warning(
                "MirroredKeyProvider: primary hkdf failed (%s); using secondary",
                e,
            )
            return await self._s.hkdf(ikm, salt=salt, info=info, length=length)


__all__ = ["MirroredKeyProvider"]
