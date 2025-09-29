"""Mixin providing shared helpers for PoP signers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, PrivateAttr

from swarmauri_core.pop import IPoPSigner as IPopSigning, PoPKind, VerifyPolicy
from swarmauri_base import register_model

from .util import canon_htm_htu, sha256_b64u


@register_model()
class PopSignerMixin(BaseModel, IPopSigning):
    """Common helpers for `IPopSigning` implementations."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _kind: PoPKind = PrivateAttr()
    _header_name: str = PrivateAttr()
    _include_query: bool = PrivateAttr(default=False)

    def __init__(
        self,
        *,
        kind: PoPKind,
        header_name: str,
        include_query: bool = False,
        **data,
    ) -> None:
        super().__init__(**data)
        self._kind = kind
        self._header_name = header_name
        self._include_query = include_query

    @property
    def kind(self) -> PoPKind:
        return self._kind

    def header_name(self) -> str:
        return self._header_name

    def _canon(self, method: str, url: str) -> tuple[str, str]:
        return canon_htm_htu(method, url, include_query=self._include_query)

    def _now(self) -> int:
        return int(datetime.now(timezone.utc).timestamp())

    def _new_jti(self) -> str:
        return uuid4().hex

    def _base_claims(
        self,
        method: str,
        url: str,
        *,
        jti: Optional[str],
        ath_b64u: Optional[str],
    ) -> dict[str, object]:
        htm, htu = self._canon(method, url)
        claims: dict[str, object] = {
            "htm": htm,
            "htu": htu,
            "iat": self._now(),
            "jti": jti or self._new_jti(),
        }
        if ath_b64u is not None:
            claims["ath"] = ath_b64u
        return claims

    def _merge_claims(
        self,
        base_claims: Mapping[str, object],
        extra_claims: Mapping[str, object] | None,
    ) -> dict[str, object]:
        merged = dict(base_claims)
        if extra_claims:
            merged.update(extra_claims)
        return merged

    def ath_from_token(self, token: bytes | str) -> str:
        if isinstance(token, str):
            token_bytes = token.encode("utf-8")
        else:
            token_bytes = token
        return sha256_b64u(token_bytes)


@dataclass(frozen=True)
class RequestContext:
    method: str
    htu: str
    policy: VerifyPolicy
