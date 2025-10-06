"""Shared helpers for AWS Workforce OAuth login implementations."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import random
import secrets
import time
from typing import Any, Callable, Dict, Mapping, Tuple

import httpx
from pydantic import ConfigDict, Field, PrivateAttr, SecretStr


class RetryingAsyncClient(httpx.AsyncClient):
    """Async HTTP client with exponential backoff and jitter."""

    def __init__(self, *, timeout_sec: float | None = None, **kwargs) -> None:
        timeout = httpx.Timeout(timeout_sec or 30.0)
        super().__init__(timeout=timeout, **kwargs)

    async def _sleep(
        self, attempt: int, *, base: float = 0.25, cap: float = 4.0
    ) -> None:
        delay = min(cap, base * (2**attempt)) * (1.0 + 0.1 * random.random())
        await asyncio.sleep(delay)

    async def post_retry(
        self, url: str, *, max_retries: int = 4, **kwargs
    ) -> httpx.Response:
        for attempt in range(max_retries + 1):
            response = await self.post(url, **kwargs)
            if response.status_code < 500 and response.status_code not in (429,):
                return response
            await self._sleep(attempt)
        response.raise_for_status()
        return response


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def make_pkce_pair() -> Tuple[str, str]:
    """Generate a PKCE verifier and challenge pair."""

    verifier = _b64u(secrets.token_bytes(32))
    challenge = _b64u(hashlib.sha256(verifier.encode("ascii")).digest())
    return verifier, challenge


def sign_state(secret: bytes, payload: Dict[str, Any], ttl_sec: int = 600) -> str:
    """Sign and encode OAuth state to protect PKCE verifier."""

    body = _b64u(
        json.dumps({**payload, "exp": int(time.time()) + ttl_sec}).encode("utf-8")
    )
    digest = hmac.new(secret, body.encode("ascii"), hashlib.sha256).digest()
    mac = _b64u(digest)
    return f"{body}.{mac}"


def verify_state(secret: bytes, state: str) -> Dict[str, Any]:
    """Validate a signed state structure and return its payload."""

    try:
        body, mac = state.split(".", 1)
    except ValueError as exc:  # pragma: no cover - defensive path
        raise ValueError("invalid state format") from exc
    expected = _b64u(hmac.new(secret, body.encode("ascii"), hashlib.sha256).digest())
    if not hmac.compare_digest(mac, expected):
        raise ValueError("bad-mac")
    payload = json.loads(base64.urlsafe_b64decode(body + "=="))
    if payload.get("exp", 0) < time.time():
        raise ValueError("expired")
    return payload


class AwsLoginMixin:
    """Common PKCE/state/token helpers shared across Workforce logins."""

    model_config = ConfigDict(extra="forbid")

    authorization_endpoint: str
    token_endpoint: str
    client_id: str
    client_secret: SecretStr
    redirect_uri: str
    state_secret: bytes
    scope: str = Field(default="openid aws sso:account:access")

    _http_client_factory: Callable[[], RetryingAsyncClient] = PrivateAttr(
        default=RetryingAsyncClient
    )

    def _client_secret_value(self) -> str:
        return self.client_secret.get_secret_value()

    def _state_secret(self) -> bytes:
        return self.state_secret

    async def _auth_payload(self) -> Dict[str, str]:
        verifier, challenge = make_pkce_pair()
        state = sign_state(self._state_secret(), {"verifier": verifier})
        url = (
            f"{self.authorization_endpoint}?response_type=code"
            f"&client_id={self.client_id}&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}&state={state}"
            f"&code_challenge={challenge}&code_challenge_method=S256"
        )
        return {"url": url, "state": state, "verifier": verifier}

    async def _post_token(self, form: Mapping[str, Any]) -> Mapping[str, Any]:
        async with self._http_client_factory() as client:
            response = await client.post_retry(
                self.token_endpoint,
                data=form,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def _exchange_tokens(self, code: str, state: str) -> Mapping[str, Any]:
        payload = verify_state(self._state_secret(), state)
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self._client_secret_value(),
            "code_verifier": payload["verifier"],
        }
        return await self._post_token(form)


__all__ = [
    "AwsLoginMixin",
    "RetryingAsyncClient",
    "make_pkce_pair",
    "sign_state",
    "verify_state",
]
