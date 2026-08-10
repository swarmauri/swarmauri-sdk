"""Framework-neutral validation for registered and application JWT claims."""

from __future__ import annotations

import time
from collections.abc import Iterable, Mapping
from typing import Any


class JWTClaimsValidationError(ValueError):
    """Raised when an authenticated JWT payload violates claim policy."""


class JWTClaimsValidator:
    """Validate claims independently of HTTP transport and JWS verification."""

    def __init__(
        self,
        *,
        required_claims: Iterable[str] = (),
        issuer: str | Iterable[str] | None = None,
        audience: str | Iterable[str] | None = None,
        leeway_s: int = 0,
        verify_exp: bool = True,
        verify_nbf: bool = True,
        verify_iat: bool = True,
        required_scopes: Iterable[str] = (),
        scope_claim: str = "scope",
        required_roles: Iterable[str] = (),
        roles_claim: str = "roles",
    ) -> None:
        if leeway_s < 0:
            raise ValueError("leeway_s must be non-negative")
        self.required_claims = frozenset(required_claims)
        self.issuers = self._normalize_expected(issuer)
        self.audiences = self._normalize_expected(audience)
        self.leeway_s = leeway_s
        self.verify_exp = verify_exp
        self.verify_nbf = verify_nbf
        self.verify_iat = verify_iat
        self.required_scopes = frozenset(required_scopes)
        self.scope_claim = scope_claim
        self.required_roles = frozenset(required_roles)
        self.roles_claim = roles_claim

    def validate(
        self, claims: Mapping[str, Any], *, now: int | None = None
    ) -> dict[str, Any]:
        """Return a validated copy of ``claims`` or raise a policy error."""

        if not isinstance(claims, Mapping):
            raise JWTClaimsValidationError("JWT claims must be a mapping")
        payload = dict(claims)
        missing = sorted(self.required_claims.difference(payload))
        if missing:
            raise JWTClaimsValidationError(
                f"Missing required claims: {', '.join(missing)}"
            )

        current_time = int(time.time()) if now is None else int(now)
        if self.verify_exp and "exp" in payload:
            exp = self._numeric_date(payload, "exp")
            if current_time >= exp + self.leeway_s:
                raise JWTClaimsValidationError("Token has expired")
        if self.verify_nbf and "nbf" in payload:
            nbf = self._numeric_date(payload, "nbf")
            if current_time + self.leeway_s < nbf:
                raise JWTClaimsValidationError("Token is not yet valid")
        if self.verify_iat and "iat" in payload:
            iat = self._numeric_date(payload, "iat")
            if current_time + self.leeway_s < iat:
                raise JWTClaimsValidationError(
                    "Token was issued in the future"
                )

        if self.issuers and payload.get("iss") not in self.issuers:
            raise JWTClaimsValidationError("Invalid token issuer")
        if self.audiences:
            token_audiences = self._claim_values(payload.get("aud"))
            if not self.audiences.intersection(token_audiences):
                raise JWTClaimsValidationError("Invalid token audience")

        self._require_values(
            payload, self.scope_claim, self.required_scopes, "scopes"
        )
        self._require_values(
            payload, self.roles_claim, self.required_roles, "roles"
        )
        self.validate_custom_claims(payload)
        return payload

    def validate_custom_claims(self, claims: Mapping[str, Any]) -> None:
        """Hook for application-specific claim policy."""

    @staticmethod
    def _normalize_expected(
        value: str | Iterable[str] | None,
    ) -> frozenset[str]:
        if value is None:
            return frozenset()
        if isinstance(value, str):
            return frozenset({value})
        return frozenset(value)

    @staticmethod
    def _claim_values(value: Any) -> frozenset[str]:
        if value is None:
            return frozenset()
        if isinstance(value, str):
            return frozenset(value.split())
        if isinstance(value, Iterable):
            return frozenset(item for item in value if isinstance(item, str))
        return frozenset()

    @staticmethod
    def _numeric_date(claims: Mapping[str, Any], name: str) -> int:
        value = claims[name]
        if isinstance(value, bool):
            raise JWTClaimsValidationError(
                f"Claim '{name}' must be a NumericDate"
            )
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise JWTClaimsValidationError(
                f"Claim '{name}' must be a NumericDate"
            ) from exc

    @classmethod
    def _require_values(
        cls,
        claims: Mapping[str, Any],
        claim_name: str,
        required: frozenset[str],
        label: str,
    ) -> None:
        if not required:
            return
        actual = cls._claim_values(claims.get(claim_name))
        missing = sorted(required.difference(actual))
        if missing:
            raise JWTClaimsValidationError(
                f"Missing required {label}: {', '.join(missing)}"
            )
