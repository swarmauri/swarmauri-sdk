from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Dict,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    Literal,
)

from swarmauri_base.key_providers.KeyProviderBase import KeyProviderBase
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider
from swarmauri_core.key_providers.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse
from swarmauri_core.crypto.types import KeyRef


@dataclass(frozen=True)
class CreateRule:
    """
    Route selection rule for create/import.
    Any provided field narrows the match. Lists/tuples mean "any-of".
    """

    provider: str
    klass: Optional[KeyClass] = None
    algs: Optional[Iterable[KeyAlg]] = None
    uses: Optional[Iterable[KeyUse]] = None
    export_policies: Optional[Iterable[ExportPolicy]] = None


def _normalize_iter(x):
    if x is None:
        return None
    return tuple(x)


def _match_create_rule(spec: KeySpec, rule: CreateRule) -> bool:
    if rule.klass and spec.klass != rule.klass:
        return False
    if rule.algs and spec.alg not in rule.algs:
        return False
    if rule.export_policies and spec.export_policy not in rule.export_policies:
        return False
    if rule.uses:
        # require that at least one desired use is requested (any-of)
        if not any(u in spec.uses for u in rule.uses):
            return False
    return True


class HierarchicalKeyProvider(KeyProviderBase):
    """
    A policy-driven composite IKeyProvider.

    Responsibilities
    ----------------
    - Route create/import to child providers according to CreateRule policy.
    - Maintain a kid → provider-name index (in-memory; optional JSON persistence).
    - Forward rotate/destroy/get/list/jwks/hkdf/random to the owning (or designated) provider.
    - Merge JWKS from all children.

    Notes
    -----
    - On get_key(kid, ...) for an unknown kid, this class will probe children (in order)
      until it finds it, then caches kid→provider in the index.
    - For random_bytes/hkdf, you can specify a designated provider; defaults to the first.
    """

    type: Literal["HierarchicalKeyProvider"] = "HierarchicalKeyProvider"

    def __init__(
        self,
        providers: Mapping[str, IKeyProvider],
        *,
        create_policy: Iterable[CreateRule] | None = None,
        import_policy: Iterable[CreateRule] | None = None,
        index_file: str | os.PathLike | None = None,
        randomness_provider: str | None = None,
        derivation_provider: str | None = None,
    ) -> None:
        super().__init__()
        if not providers:
            raise ValueError(
                "HierarchicalKeyProvider requires at least one child provider"
            )

        # child providers, keyed by a stable name
        self._children: Dict[str, IKeyProvider] = dict(providers)

        # ordered routing policies
        self._create_rules: Tuple[CreateRule, ...] = tuple(
            CreateRule(
                provider=r.provider,
                klass=r.klass,
                algs=_normalize_iter(r.algs),
                uses=_normalize_iter(r.uses),
                export_policies=_normalize_iter(r.export_policies),
            )
            for r in (create_policy or ())
        )
        self._import_rules: Tuple[CreateRule, ...] = tuple(
            CreateRule(
                provider=r.provider,
                klass=r.klass,
                algs=_normalize_iter(r.algs),
                uses=_normalize_iter(r.uses),
                export_policies=_normalize_iter(r.export_policies),
            )
            for r in (import_policy or ())
        )

        # where to persist kid→provider index (optional)
        self._index_path: Optional[Path] = Path(index_file) if index_file else None
        self._kid_index: Dict[str, str] = {}
        self._mutex = threading.RLock()

        # designate providers for random/hkdf if desired
        self._rand_name = randomness_provider or next(iter(self._children.keys()))
        self._hkdf_name = derivation_provider or self._rand_name

        # load existing index if present
        if self._index_path and self._index_path.exists():
            try:
                data = json.loads(self._index_path.read_text())
                if isinstance(data, dict):
                    # validate only known providers
                    self._kid_index = {
                        k: v for k, v in data.items() if v in self._children
                    }
            except Exception:
                # ignore corrupted index; start fresh
                self._kid_index = {}

    # ───────────────────────── utilities ─────────────────────────

    def _persist_index_unlocked(self) -> None:
        if not self._index_path:
            return
        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._index_path.with_suffix(self._index_path.suffix + ".tmp")
        tmp.write_text(json.dumps(self._kid_index, indent=2, sort_keys=True))
        tmp.replace(self._index_path)

    def _record_owner_unlocked(self, kid: str, provider_name: str) -> None:
        if self._kid_index.get(kid) == provider_name:
            return
        self._kid_index[kid] = provider_name
        self._persist_index_unlocked()

    def _owner_unlocked(self, kid: str) -> Optional[IKeyProvider]:
        name = self._kid_index.get(kid)
        return self._children.get(name) if name else None

    def _pick_by_policy(
        self, spec: KeySpec, rules: Tuple[CreateRule, ...]
    ) -> IKeyProvider:
        # First match wins
        for rule in rules:
            if _match_create_rule(spec, rule):
                prov = self._children.get(rule.provider)
                if prov:
                    return prov
        # Fallback: try simple heuristics if no rules matched
        #  - favor asymmetric to HSM/KMS if present; symmetric to local/file
        #  - otherwise first child in dict order
        names = tuple(self._children.keys())

        # heuristic buckets
        # Look for a child with "kms" or "pkcs11" in its name for asymmetric/private ops
        if spec.klass == KeyClass.asymmetric:
            preferred = next(
                (n for n in names if "kms" in n.lower() or "pkcs11" in n.lower()), None
            )
            if preferred:
                return self._children[preferred]
        # symmetric → prefer local/file
        if spec.klass == KeyClass.symmetric:
            preferred = next(
                (n for n in names if "local" in n.lower() or "file" in n.lower()), None
            )
            if preferred:
                return self._children[preferred]
        # default
        return self._children[names[0]]

    def _first_child(self) -> IKeyProvider:
        return next(iter(self._children.values()))

    # ───────────────────────── capabilities ─────────────────────────

    def supports(self) -> Mapping[str, Iterable[str]]:
        # Union of capabilities with a couple of meta flags
        out: Dict[str, set] = {
            "class": set(),
            "algs": set(),
            "features": {"hierarchical"},
        }
        for prov in self._children.values():
            caps = prov.supports()
            for k in ("class", "algs", "features"):
                if k in caps:
                    out.setdefault(k, set()).update(caps[k])  # type: ignore[arg-type]
        if self._index_path:
            out.setdefault("features", set()).add("index_persistence")
        return {k: tuple(v) for k, v in out.items()}  # type: ignore[return-value]

    # ───────────────────────── lifecycle ─────────────────────────

    async def create_key(self, spec: KeySpec) -> KeyRef:
        with self._mutex:
            prov = self._pick_by_policy(spec, self._create_rules)
        ref = await prov.create_key(spec)
        with self._mutex:
            self._record_owner_unlocked(ref.kid, self._resolve_name(prov))
        return ref

    async def import_key(
        self, spec: KeySpec, material: bytes, *, public: Optional[bytes] = None
    ) -> KeyRef:
        with self._mutex:
            # choose provider using import policy if provided; else reuse create policy
            rules = self._import_rules if self._import_rules else self._create_rules
            prov = self._pick_by_policy(spec, rules)
        ref = await prov.import_key(spec, material, public=public)
        with self._mutex:
            self._record_owner_unlocked(ref.kid, self._resolve_name(prov))
        return ref

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ) -> KeyRef:
        with self._mutex:
            prov = self._owner_unlocked(kid)
        if prov is None:
            # probe children to discover ownership
            prov = await self._probe_owner(kid)
        new_ref = await prov.rotate_key(kid, spec_overrides=spec_overrides)
        # rotation keeps same kid; owner unchanged
        return new_ref

    async def destroy_key(self, kid: str, version: Optional[int] = None) -> bool:
        with self._mutex:
            prov = self._owner_unlocked(kid)
        if prov is None:
            # best effort: try all children
            ok_any = False
            for p in self._children.values():
                try:
                    ok = await p.destroy_key(kid, version)
                    ok_any = ok_any or ok
                except Exception:
                    continue
            if ok_any and version is None:
                with self._mutex:
                    self._kid_index.pop(kid, None)
                    self._persist_index_unlocked()
            return ok_any
        ok = await prov.destroy_key(kid, version)
        if ok and version is None:
            with self._mutex:
                self._kid_index.pop(kid, None)
                self._persist_index_unlocked()
        return ok

    async def get_key(
        self, kid: str, version: Optional[int] = None, *, include_secret: bool = False
    ) -> KeyRef:
        with self._mutex:
            prov = self._owner_unlocked(kid)
        if prov is None:
            prov = await self._probe_owner(kid)
        return await prov.get_key(kid, version, include_secret=include_secret)

    async def list_versions(self, kid: str) -> Tuple[int, ...]:
        with self._mutex:
            prov = self._owner_unlocked(kid)
        if prov is None:
            prov = await self._probe_owner(kid)
        return await prov.list_versions(kid)

    # ───────────────────────── public export ─────────────────────────

    async def get_public_jwk(self, kid: str, version: Optional[int] = None) -> dict:
        with self._mutex:
            prov = self._owner_unlocked(kid)
        if prov is None:
            prov = await self._probe_owner(kid)
        return await prov.get_public_jwk(kid, version)

    async def jwks(self, *, prefix_kids: Optional[str] = None) -> dict:
        # Merge all children JWKS; keep order stable by provider name
        keys = []
        for name in sorted(self._children.keys()):
            try:
                jwks = await self._children[name].jwks(prefix_kids=prefix_kids)  # type: ignore[arg-type]
            except TypeError:
                # Some providers may not accept prefix_kids; call without it
                jwks = await self._children[name].jwks()
            kid_set = set()
            for k in jwks.get("keys", []):
                # Dedup by kid if multiple providers expose the same public
                kid = k.get("kid")
                if kid and kid not in kid_set:
                    keys.append(k)
                    kid_set.add(kid)
        return {"keys": keys}

    # ───────────────────────── material helpers ─────────────────────────

    async def random_bytes(self, n: int) -> bytes:
        prov = self._children[self._rand_name]
        return await prov.random_bytes(n)

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:
        prov = self._children[self._hkdf_name]
        return await prov.hkdf(ikm, salt=salt, info=info, length=length)

    # ───────────────────────── internals ─────────────────────────

    async def _probe_owner(self, kid: str) -> IKeyProvider:
        """
        Try to locate which child owns 'kid' by attempting a benign get_key.
        Caches result in index on success.
        """
        last_err: Optional[Exception] = None
        for name, prov in self._children.items():
            try:
                _ = await prov.get_key(kid, None, include_secret=False)
                with self._mutex:
                    self._record_owner_unlocked(kid, name)
                return prov
            except Exception as e:
                last_err = e
                continue
        # Nothing found; rethrow the last error (usually KeyError) for context
        raise last_err if last_err else KeyError(f"Unknown kid: {kid}")

    def _resolve_name(self, provider: IKeyProvider) -> str:
        # reverse-lookup by identity
        for name, prov in self._children.items():
            if prov is provider:
                return name
        # fallback (shouldn't happen)
        return next(iter(self._children.keys()))
