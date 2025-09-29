from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Optional

from pydantic import PrivateAttr

from swarmauri_base.signing.SigningBase import SigningBase
from swarmauri_core.crypto.types import Alg, KeyRef
from swarmauri_core.signing import Canon, Envelope, ISigning
from swarmauri_core.signing.types import Signature

DEFAULT_OPS = ("bytes", "digest", "envelope", "stream")


class Signer(SigningBase):
    """Aggregate multiple :class:`ISigning` providers behind a single interface."""

    type: str = "Signer"

    _providers: list[ISigning] = PrivateAttr(default_factory=list)
    _providers_without_alg: list[ISigning] = PrivateAttr(default_factory=list)
    _alg_index: dict[str, ISigning] = PrivateAttr(default_factory=dict)
    _alg_tokens: dict[str, Any] = PrivateAttr(default_factory=dict)
    _default_alg_token: Optional[str] = PrivateAttr(default=None)

    def __init__(
        self,
        *,
        providers: Optional[Iterable[ISigning]] = None,
        default_alg: Optional[Alg] = None,
        **data: Any,
    ) -> None:
        super().__init__(**data)
        self._default_alg_token = self._normalize_alg_token(default_alg)
        if providers:
            for provider in providers:
                self.add_provider(provider)

    # ------------------------------------------------------------------
    def add_provider(self, provider: ISigning) -> None:
        """Register an :class:`ISigning` implementation with the aggregator."""

        if provider in self._providers:
            return

        self._providers.append(provider)
        caps = provider.supports() or {}
        algs = caps.get("algs", ()) or ()
        added_alg = False
        for alg in algs:
            normalized = self._normalize_alg_token(alg)
            if normalized is None:
                continue
            self._alg_index[normalized] = provider
            self._alg_tokens[normalized] = alg
            added_alg = True
        if not added_alg:
            self._providers_without_alg.append(provider)

    # ------------------------------------------------------------------
    def providers(self) -> Sequence[ISigning]:
        """Return the registered providers in insertion order."""

        return tuple(self._providers)

    # ------------------------------------------------------------------
    def supports(self) -> Mapping[str, Iterable[str]]:
        algs: list[Any] = []
        canons: list[str] = []
        signs: list[str] = []
        verifies: list[str] = []
        envelopes: list[str] = []
        features: list[str] = []

        for provider in self._providers or self._providers_without_alg:
            caps = provider.supports() or {}
            self._extend_unique(algs, caps.get("algs", ()))
            self._extend_unique(canons, caps.get("canons", ()))
            self._extend_unique(signs, caps.get("signs", DEFAULT_OPS))
            self._extend_unique(verifies, caps.get("verifies", DEFAULT_OPS))
            self._extend_unique(envelopes, caps.get("envelopes", ()))
            self._extend_unique(features, caps.get("features", ()))

        return {
            "algs": tuple(algs),
            "canons": tuple(canons),
            "signs": tuple(signs or DEFAULT_OPS),
            "verifies": tuple(verifies or DEFAULT_OPS),
            "envelopes": tuple(envelopes),
            "features": tuple(features),
        }

    # ------------------------------------------------------------------
    async def canonicalize_envelope(
        self,
        env: Envelope,
        *,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bytes:
        provider = self._provider_for_canon(canon)
        return await provider.canonicalize_envelope(env, canon=canon, opts=opts)

    # ------------------------------------------------------------------
    async def sign_bytes(
        self,
        key: KeyRef,
        payload: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        provider, resolved_alg = self._provider_for_alg(alg)
        return await provider.sign_bytes(
            key, payload, alg=resolved_alg or alg, opts=opts
        )

    # ------------------------------------------------------------------
    async def sign_digest(
        self,
        key: KeyRef,
        digest: bytes,
        *,
        alg: Optional[Alg] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        provider, resolved_alg = self._provider_for_alg(alg)
        return await provider.sign_digest(
            key, digest, alg=resolved_alg or alg, opts=opts
        )

    # ------------------------------------------------------------------
    async def sign_envelope(
        self,
        key: KeyRef,
        env: Envelope,
        *,
        alg: Optional[Alg] = None,
        canon: Optional[Canon] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> Sequence[Signature]:
        provider, resolved_alg = self._provider_for_alg(alg)
        return await provider.sign_envelope(
            key,
            env,
            alg=resolved_alg or alg,
            canon=canon,
            opts=opts,
        )

    # ------------------------------------------------------------------
    async def verify_bytes(
        self,
        payload: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        providers = self._providers_for_verification(signatures, require)
        if not providers:
            raise ValueError("Signer has no providers available for verification")

        verified = False
        for provider in providers:
            if not await provider.verify_bytes(
                payload, signatures, require=require, opts=opts
            ):
                return False
            verified = True
        return verified

    # ------------------------------------------------------------------
    async def verify_digest(
        self,
        digest: bytes,
        signatures: Sequence[Signature],
        *,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        providers = self._providers_for_verification(signatures, require)
        if not providers:
            raise ValueError("Signer has no providers available for verification")

        verified = False
        for provider in providers:
            if not await provider.verify_digest(
                digest, signatures, require=require, opts=opts
            ):
                return False
            verified = True
        return verified

    # ------------------------------------------------------------------
    async def verify_envelope(
        self,
        env: Envelope,
        signatures: Sequence[Signature],
        *,
        canon: Optional[Canon] = None,
        require: Optional[Mapping[str, object]] = None,
        opts: Optional[Mapping[str, object]] = None,
    ) -> bool:
        providers = self._providers_for_verification(signatures, require)
        if not providers:
            raise ValueError("Signer has no providers available for verification")

        verified = False
        for provider in providers:
            if not await provider.verify_envelope(
                env,
                signatures,
                canon=canon,
                require=require,
                opts=opts,
            ):
                return False
            verified = True
        return verified

    # ------------------------------------------------------------------
    def _provider_for_canon(self, canon: Optional[Canon]) -> ISigning:
        if canon is not None:
            for provider in self._providers:
                caps = provider.supports() or {}
                if canon in tuple(caps.get("canons", ())):
                    return provider
        if self._providers:
            return self._providers[0]
        if self._providers_without_alg:
            return self._providers_without_alg[0]
        raise ValueError("Signer has no registered providers")

    # ------------------------------------------------------------------
    def _provider_for_alg(self, alg: Optional[Alg]) -> tuple[ISigning, Optional[Any]]:
        if alg is not None:
            normalized = self._normalize_alg_token(alg)
            if normalized and normalized in self._alg_index:
                return self._alg_index[normalized], self._alg_tokens.get(
                    normalized, alg
                )
            raise ValueError(f"No provider registered for algorithm '{alg}'")

        if self._default_alg_token and self._default_alg_token in self._alg_index:
            provider = self._alg_index[self._default_alg_token]
            return provider, self._alg_tokens.get(self._default_alg_token)

        if len(self._providers) == 1:
            provider = self._providers[0]
            alg_choice = next(iter(provider.supports().get("algs", ())), None)
            return provider, alg_choice

        if self._providers_without_alg:
            return self._providers_without_alg[0], None

        if self._providers:
            provider = self._providers[0]
            alg_choice = next(iter(provider.supports().get("algs", ())), None)
            return provider, alg_choice

        raise ValueError("Signer has no registered providers")

    # ------------------------------------------------------------------
    def _providers_for_verification(
        self,
        signatures: Sequence[Signature],
        require: Optional[Mapping[str, object]],
    ) -> list[ISigning]:
        required_tokens: list[str] = []

        if require and require.get("algs"):
            for token in require["algs"]:  # type: ignore[index]
                normalized = self._normalize_alg_token(token)
                if normalized is not None:
                    required_tokens.append(normalized)

        for sig in signatures:
            normalized = self._normalize_alg_token(sig.get("alg"))
            if normalized is not None:
                required_tokens.append(normalized)

        providers: list[ISigning] = []
        for token in required_tokens:
            provider = self._alg_index.get(token)
            if provider and provider not in providers:
                providers.append(provider)

        if not providers:
            providers.extend(self._providers)
        if not providers:
            providers.extend(self._providers_without_alg)

        return providers

    # ------------------------------------------------------------------
    @staticmethod
    def _extend_unique(target: list, values: Iterable[Any]) -> None:
        for value in values:
            if value not in target:
                target.append(value)

    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_alg_token(token: Any) -> Optional[str]:
        if token is None:
            return None
        if hasattr(token, "value"):
            token = getattr(token, "value")
        return str(token)
