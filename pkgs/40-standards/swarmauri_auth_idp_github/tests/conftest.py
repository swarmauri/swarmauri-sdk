"""Offline HTTP fakes and throwaway keys shared by the GitHub IdP tests."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@dataclass
class RecordedRequest:
    method: str
    url: str
    headers: Optional[Dict[str, str]]
    data: Optional[Dict[str, Any]]
    json: Optional[Any]


class RecordingClient:
    """Record requests and replay queued ``(status, payload)`` responses."""

    def __init__(self, responses: Tuple[Tuple[int, Any], ...]) -> None:
        self._responses = list(responses)
        self.requests: List[RecordedRequest] = []

    async def __aenter__(self) -> "RecordingClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    def _respond(
        self, method: str, url: str, kwargs: Dict[str, Any]
    ) -> httpx.Response:
        self.requests.append(
            RecordedRequest(
                method=method,
                url=url,
                headers=kwargs.get("headers"),
                data=kwargs.get("data"),
                json=kwargs.get("json"),
            )
        )
        if not self._responses:
            raise AssertionError(f"unexpected request: {method} {url}")
        status, payload = self._responses.pop(0)
        return httpx.Response(
            status, json=payload, request=httpx.Request(method, url)
        )

    async def post_retry(self, url: str, **kwargs: Any) -> httpx.Response:
        return self._respond("POST", url, kwargs)

    async def get_retry(self, url: str, **kwargs: Any) -> httpx.Response:
        return self._respond("GET", url, kwargs)


@pytest.fixture
def recording_client() -> Callable[..., RecordingClient]:
    def make(*responses: Tuple[int, Any]) -> RecordingClient:
        return RecordingClient(responses)

    return make


@pytest.fixture(scope="session")
def rsa_key_pair() -> Tuple[str, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")
    public_pem = (
        key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("ascii")
    )
    return private_pem, public_pem
