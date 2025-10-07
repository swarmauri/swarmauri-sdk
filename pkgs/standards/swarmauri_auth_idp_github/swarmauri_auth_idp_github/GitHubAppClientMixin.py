"""Shared helpers for GitHub App installation token clients."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

import jwt
from pydantic import ConfigDict, Field, SecretStr

from swarmauri_base.auth_idp.http import RetryingAsyncClient


class GitHubAppClientMixin:
    """Reusable JWT and caching helpers for GitHub App installation tokens."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    app_id: str
    installation_id: int
    private_key_pem: SecretStr
    api_base: str = Field(default="https://api.github.com")
    permissions: Optional[Mapping[str, str]] = None
    repository_ids: Optional[Sequence[int]] = None
    repository_names: Optional[Sequence[str]] = None
    cache_skew_seconds: int = Field(default=30, ge=0)
    http_client_factory: Callable[[], RetryingAsyncClient] = Field(
        default=RetryingAsyncClient, exclude=True, repr=False
    )
    cached_token: Optional[Tuple[str, float]] = Field(
        default=None, exclude=True, repr=False
    )

    def _installation_endpoint(self) -> str:
        base = self.api_base.rstrip("/")
        return f"{base}/app/installations/{self.installation_id}/access_tokens"

    def _private_key_value(self) -> str:
        return self.private_key_pem.get_secret_value()

    def _app_jwt(self) -> str:
        now = int(time.time())
        payload = {"iat": now - 60, "exp": now + 600, "iss": self.app_id}
        return jwt.encode(payload, self._private_key_value(), algorithm="RS256")

    def _request_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if self.permissions:
            payload["permissions"] = dict(self.permissions)
        if self.repository_ids:
            payload["repository_ids"] = list(self.repository_ids)
        if self.repository_names:
            payload["repository_names"] = list(self.repository_names)
        return payload

    @staticmethod
    def _expires_at(payload: Mapping[str, Any]) -> float:
        expires_at = payload.get("expires_at")
        if isinstance(expires_at, str):
            try:
                if expires_at.endswith("Z"):
                    expires_at = expires_at[:-1] + "+00:00"
                return (
                    datetime.fromisoformat(expires_at)
                    .astimezone(timezone.utc)
                    .timestamp()
                )
            except ValueError:
                pass
        expires_in = payload.get("expires_in")
        if isinstance(expires_in, (int, float)):
            return time.time() + float(expires_in)
        return time.time() + 3600

    async def _fetch_token(self) -> Tuple[str, float]:
        payload = self._request_payload()
        async with self.http_client_factory() as client:
            response = await client.post_retry(
                self._installation_endpoint(),
                json=payload or {},
                headers={
                    "Authorization": f"Bearer {self._app_jwt()}",
                    "Accept": "application/vnd.github+json",
                },
            )
            response.raise_for_status()
            data = response.json()
        token = data["token"]
        expires = self._expires_at(data)
        return token, expires

    async def _cached_access_token(self) -> str:
        cached = self.cached_token
        now = time.time()
        if cached and now < cached[1] - self.cache_skew_seconds:
            return cached[0]
        token, expires_at = await self._fetch_token()
        self.cached_token = (token, expires_at)
        return token


__all__ = ["GitHubAppClientMixin"]
