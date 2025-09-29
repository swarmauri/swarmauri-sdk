"""Mixin providing shared verification helpers for PoP verifiers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Mapping, Optional

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from swarmauri_core.pop import (
    BindType,
    CnfBinding,
    Feature,
    HttpParts,
    IPoPVerifier as IPopVerifier,
    KeyResolver,
    PoPBindingError,
    PoPParseError,
    PoPVerificationError,
    PoPKind,
    ReplayHooks,
    VerifyPolicy,
)
from swarmauri_base import register_model
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

from .PopSignerMixin import RequestContext
from .binding import normalize_cnf
from .util import canon_htm_htu, sha256_b64u


@register_model()
class PopVerifierMixin(BaseModel, IPopVerifier):
    """Provide default behaviours for IPoPVerifier implementations."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _kind: PoPKind = PrivateAttr()
    _header_name: str = PrivateAttr()
    _features: Feature = PrivateAttr()
    _algorithms: tuple[str, ...] = PrivateAttr()

    def __init__(
        self,
        *,
        kind: PoPKind,
        header_name: str,
        features: Feature,
        algorithms: Iterable[str],
        **data,
    ) -> None:
        super().__init__(**data)
        self._kind = kind
        self._header_name = header_name
        self._features = features
        self._algorithms = tuple(algorithms)

    @property
    def kind(self) -> PoPKind:
        return self._kind

    @property
    def header_name(self) -> str:
        return self._header_name

    def features(self) -> Feature:
        return self._features

    def algs(self) -> Iterable[str]:
        return self._algorithms

    async def verify_http(
        self,
        req: HttpParts,
        cnf: CnfBinding,
        *,
        policy: VerifyPolicy = VerifyPolicy(),
        replay: ReplayHooks | None = None,
        keys: KeyResolver | None = None,
        extras: Mapping[str, object] | None = None,
    ) -> None:
        extras = extras or {}
        header_value = self._extract_proof(req)
        htm, htu = canon_htm_htu(req.method, req.url, include_query=policy.htu_exact)
        context = RequestContext(method=htm, htu=htu, policy=policy)
        await self._verify_core(
            header_value,
            context,
            cnf,
            replay=replay,
            keys=keys,
            extras=extras,
        )

    def _extract_proof(self, req: HttpParts) -> str:
        try:
            value = req.headers[self._header_name]
        except KeyError as exc:
            raise PoPParseError(f"Missing {self._header_name} header") from exc
        if not value:
            raise PoPParseError(f"Empty {self._header_name} header")
        return value

    async def _verify_core(
        self,
        proof: str,
        context: RequestContext,
        cnf: CnfBinding,
        *,
        replay: ReplayHooks | None,
        keys: KeyResolver | None,
        extras: Mapping[str, object],
    ) -> None:
        raise NotImplementedError

    def _enforce_alg_policy(self, alg: str, policy: VerifyPolicy) -> None:
        if policy.alg_allow and alg not in policy.alg_allow:
            raise PoPVerificationError(f"Algorithm {alg} not permitted")

    def _enforce_bind_type(
        self,
        cnf: CnfBinding,
        policy: VerifyPolicy,
        *,
        expected: BindType | None = None,
    ) -> None:
        if policy.require_bind and cnf.bind_type is not policy.require_bind:
            raise PoPBindingError(
                f"Access token requires {policy.require_bind.value} but received {cnf.bind_type.value} proof"
            )
        if expected and cnf.bind_type is not expected:
            raise PoPBindingError(
                f"Expected {expected.value} binding but received {cnf.bind_type.value}"
            )

    def _check_replay(
        self,
        *,
        replay: ReplayHooks | None,
        scope: str,
        key: str,
        ttl_s: int,
    ) -> None:
        if replay is None:
            return
        if replay.seen(scope, key):
            raise PoPVerificationError("Replay detected for proof")
        replay.mark(scope, key, ttl_s)

    def _require_ath(
        self,
        *,
        ath_claim: Optional[str],
        policy: VerifyPolicy,
        extras: Mapping[str, object],
    ) -> None:
        if policy.require_ath:
            if not ath_claim:
                raise PoPVerificationError("Access-token hash (ath) required by policy")
            access_token = extras.get("access_token")
            if access_token is None:
                raise PoPVerificationError(
                    "Access-token material required to verify ath claim"
                )
            expected = self._compute_ath(access_token)
            if expected != ath_claim:
                raise PoPVerificationError(
                    "ath claim does not match provided access token"
                )

    def _compute_ath(self, token: bytes | str) -> str:
        if isinstance(token, str):
            token_bytes = token.encode("utf-8")
        else:
            token_bytes = token
        return sha256_b64u(token_bytes)

    def _now(self) -> int:
        return int(datetime.now(timezone.utc).timestamp())

    def _validate_iat(self, iat: int, policy: VerifyPolicy) -> None:
        now = self._now()
        if abs(now - iat) > policy.max_skew_s:
            raise PoPVerificationError("iat outside permitted skew")

    def _load_cnf(self, cnf_claim: Mapping[str, object]) -> CnfBinding:
        return normalize_cnf(cnf_claim)


@ComponentBase.register_model()
class PopVerifierBase(PopVerifierMixin, ComponentBase):
    """Component base for PoP verifiers."""

    resource: Optional[str] = Field(default=ResourceTypes.CRYPTO.value, frozen=True)
    type: str = "PopVerifierBase"


# Backwards compatibility alias
PopVerifier = PopVerifierBase
