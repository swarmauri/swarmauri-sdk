"""Offline contract tests for the AWS IAM Identity Center logins and
identity resolver (#6274).

Covers the primary public operation of each exported class, which the
existing unit tests only touch through resolver construction and one
``lookup_user_min`` happy path:

- ``AwsOAuth20Login.auth_url``: authorization endpoint, default
  ``openid aws sso:account:access`` scope, PKCE S256 challenge, and the
  signed state round-tripping the verifier.
- ``AwsOAuth20Login.exchange_and_identity``: token POST (URL, form fields,
  ``Accept`` header) and the ``aws-workforce`` issuer wrapper.
- ``AwsOAuth21Login.auth_url``: same contract plus ``prompt=consent``.
- ``AwsOAuth21Login.exchange_and_identity``: same token exchange contract.
- ``AwsIdentityResolver._get_role_credentials``: regional SSO endpoint
  construction, ``account_id``/``role_name`` params, and the bearer header.
- ``AwsIdentityResolver.lookup_user_min``: role-credential forwarding into
  the boto3 Session, IdentityStore request arguments, and returned user
  fields. The resolver lists a single user (``MaxResults=1``); that result
  is the first user in the store, which this issue does not establish as
  the authenticated caller.

Everything runs offline: a fake async HTTP client serves the token
endpoint, ``httpx.get`` and ``boto3.Session`` are stubbed for the resolver,
and no network access, credentials, or live AWS account are needed.
Nothing here proves interoperability with AWS's production service.
"""

from __future__ import annotations

import base64
import hashlib
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from pydantic import SecretStr

from swarmauri_auth_idp_aws import (
    AwsIdentityResolver,
    AwsOAuth20Login,
    AwsOAuth21Login,
)
from swarmauri_base.auth_idp import sign_state, verify_state

AUTH_ENDPOINT = "https://portal.sso.us-east-1.amazonaws.com/oauth2/authorize"
TOKEN_ENDPOINT = "https://portal.sso.us-east-1.amazonaws.com/oauth2/token"
CLIENT_ID = "aws-client-id"
REDIRECT_URI = "https://example.com/callback"
STATE_SECRET = b"test-state-secret-32-bytes-long!!"
DEFAULT_SCOPE = "openid aws sso:account:access"


class FakeResponse:
    """Minimal stand-in for an httpx response."""

    def __init__(
        self, payload: Any, *, status: int = 200, error: bool = False
    ) -> None:
        self._payload = payload
        self.status_code = status
        self._error = error

    def raise_for_status(self) -> None:
        if self._error:
            request = httpx.Request("POST", TOKEN_ENDPOINT)
            raise httpx.HTTPStatusError(
                "provider error",
                request=request,
                response=httpx.Response(self.status_code, request=request),
            )

    def json(self) -> Any:
        return self._payload


class FakeClient:
    """Fake async HTTP client recording ``post_retry`` calls."""

    def __init__(self, factory: FakeClientFactory) -> None:
        self._factory = factory

    async def __aenter__(self) -> FakeClient:  # noqa: PYI034
        return self

    async def __aexit__(self, *exc: object) -> bool:
        return False

    async def post_retry(
        self,
        url: str,
        *,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> FakeResponse:
        self._factory.calls.append(
            {
                "method": "POST",
                "url": url,
                "data": dict(data or {}),
                "headers": dict(headers or {}),
            }
        )
        return self._factory.responses.pop(0)


class FakeClientFactory:
    """Queue of fake token responses plus a call log."""

    def __init__(self, responses: list[FakeResponse] | None = None) -> None:
        self.responses = list(responses or [])
        self.calls: list[dict[str, Any]] = []

    def __call__(self) -> FakeClient:
        return FakeClient(self)

    def posts(self) -> list[dict[str, Any]]:
        return [c for c in self.calls if c["method"] == "POST"]


def _login(cls: type, factory: FakeClientFactory, **overrides: Any):
    kwargs: dict[str, Any] = {
        "authorization_endpoint": AUTH_ENDPOINT,
        "token_endpoint": TOKEN_ENDPOINT,
        "client_id": CLIENT_ID,
        "client_secret": SecretStr("client-secret"),
        "redirect_uri": REDIRECT_URI,
        "state_secret": STATE_SECRET,
    }
    kwargs.update(overrides)
    login = cls(**kwargs)
    login._http_client_factory = factory
    return login


def _token_payload() -> dict[str, Any]:
    return {
        "access_token": "aws-access-token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": "aws-id-token",
    }


def _assert_auth_url(url: str, *, prompt: str | None = None) -> str:
    parsed = urlsplit(url)
    assert parsed.scheme == "https"
    assert parsed.netloc == "portal.sso.us-east-1.amazonaws.com"
    assert parsed.path == "/oauth2/authorize"
    query = parse_qs(parsed.query)
    assert query["response_type"] == ["code"]
    assert query["client_id"] == [CLIENT_ID]
    assert query["redirect_uri"] == [REDIRECT_URI]
    assert query["scope"] == [DEFAULT_SCOPE]
    assert query["code_challenge_method"] == ["S256"]
    assert query["code_challenge"]
    if prompt is None:
        assert "prompt" not in query
    else:
        assert query["prompt"] == [prompt]
    state = query["state"][0]
    payload = verify_state(STATE_SECRET, state)
    verifier = payload["verifier"]
    expected_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .decode()
        .rstrip("=")
    )
    assert query["code_challenge"] == [expected_challenge]
    return state


def _assert_token_post(
    factory: FakeClientFactory, *, state: str, code: str = "auth-code-123"
) -> dict[str, Any]:
    posts = factory.posts()
    assert len(posts) == 1
    post = posts[0]
    assert post["url"] == TOKEN_ENDPOINT
    assert post["headers"] == {"Accept": "application/json"}
    data = post["data"]
    assert data["grant_type"] == "authorization_code"
    assert data["code"] == code
    assert data["redirect_uri"] == REDIRECT_URI
    assert data["client_id"] == CLIENT_ID
    assert data["client_secret"] == "client-secret"
    assert (
        data["code_verifier"] == verify_state(STATE_SECRET, state)["verifier"]
    )
    return data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_auth_url_contract() -> None:
    login = _login(AwsOAuth20Login, FakeClientFactory())
    result = await login.auth_url()
    assert set(result) == {"url", "state"}
    returned_state = _assert_auth_url(result["url"])
    assert result["state"] == returned_state


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_auth_url_custom_scope() -> None:
    login = _login(
        AwsOAuth20Login,
        FakeClientFactory(),
        scope="openid aws sso:account:access email",
    )
    result = await login.auth_url()
    query = parse_qs(urlsplit(result["url"]).query)
    assert query["scope"] == ["openid aws sso:account:access email"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_and_identity() -> None:
    factory = FakeClientFactory([FakeResponse(_token_payload())])
    login = _login(AwsOAuth20Login, factory)
    state = (await login.auth_url())["state"]
    result = await login.exchange_and_identity("auth-code-123", state)
    _assert_token_post(factory, state=state)
    assert result["issuer"] == "aws-workforce"
    assert result["tokens"] == _token_payload()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_tampered_state_raises() -> None:
    factory = FakeClientFactory([FakeResponse(_token_payload())])
    login = _login(AwsOAuth20Login, factory)
    state = (await login.auth_url())["state"]
    with pytest.raises(ValueError):
        await login.exchange_and_identity("auth-code-123", state + "x")
    assert factory.posts() == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_token_http_error_raises() -> None:
    factory = FakeClientFactory(
        [FakeResponse({"error": "server_error"}, status=500, error=True)]
    )
    login = _login(AwsOAuth20Login, factory)
    state = (await login.auth_url())["state"]
    with pytest.raises(httpx.HTTPStatusError):
        await login.exchange_and_identity("auth-code-123", state)
    assert len(factory.posts()) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth20_exchange_state_without_verifier_raises() -> None:
    factory = FakeClientFactory([FakeResponse(_token_payload())])
    login = _login(AwsOAuth20Login, factory)
    state = sign_state(STATE_SECRET, {})
    with pytest.raises(KeyError):
        await login.exchange_and_identity("auth-code-123", state)
    assert factory.posts() == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_auth_url_contract_includes_prompt_consent() -> None:
    login = _login(AwsOAuth21Login, FakeClientFactory())
    result = await login.auth_url()
    assert set(result) == {"url", "state"}
    returned_state = _assert_auth_url(result["url"], prompt="consent")
    assert result["state"] == returned_state


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_and_identity() -> None:
    factory = FakeClientFactory([FakeResponse(_token_payload())])
    login = _login(AwsOAuth21Login, factory)
    state = (await login.auth_url())["state"]
    result = await login.exchange_and_identity("auth-code-123", state)
    _assert_token_post(factory, state=state)
    assert result["issuer"] == "aws-workforce"
    assert result["tokens"] == _token_payload()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth21_exchange_tampered_state_raises() -> None:
    factory = FakeClientFactory([FakeResponse(_token_payload())])
    login = _login(AwsOAuth21Login, factory)
    state = (await login.auth_url())["state"]
    with pytest.raises(ValueError):
        await login.exchange_and_identity("auth-code-123", state + "x")
    assert factory.posts() == []


def _resolver() -> AwsIdentityResolver:
    return AwsIdentityResolver(
        region="us-east-1",
        sso_region="us-west-2",
        identity_store_id="d-123",
        account_id="123456789012",
        role_name="WorkforceReader",
    )


class _FakeHttpGet:
    """Captures ``httpx.get`` calls for the resolver."""

    def __init__(self, payload: Any, *, error: bool = False) -> None:
        self.payload = payload
        self.error = error
        self.calls: list[dict[str, Any]] = []

    def __call__(self, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        return FakeResponse(
            self.payload, status=500 if self.error else 200, error=self.error
        )


class _FakeIdentityStore:
    def __init__(self, users: list[dict[str, Any]]) -> None:
        self.users = users
        self.calls: list[dict[str, Any]] = []

    def list_users(self, IdentityStoreId: str, MaxResults: int):
        self.calls.append(
            {"IdentityStoreId": IdentityStoreId, "MaxResults": MaxResults}
        )
        return {"Users": self.users}


class _FakeSession:
    def __init__(self, store: _FakeIdentityStore, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.store = store

    def client(self, name: str) -> _FakeIdentityStore:
        assert name == "identitystore"
        return self.store


def _user(user_id: str = "u-1") -> dict[str, Any]:
    return {
        "UserId": user_id,
        "UserName": "jdoe",
        "DisplayName": "Jane Doe",
        "Emails": [{"Value": "jane@example.com"}],
    }


def _role_creds() -> dict[str, Any]:
    return {
        "roleCredentials": {
            "accessKeyId": "ak",
            "secretAccessKey": "sk",
            "sessionToken": "st",
        }
    }


@pytest.mark.unit
def test_resolver_role_credentials_regional_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get = _FakeHttpGet(_role_creds())
    monkeypatch.setattr("httpx.get", get)
    creds = _resolver()._get_role_credentials("access-token")
    assert creds == _role_creds()["roleCredentials"]
    assert len(get.calls) == 1
    call = get.calls[0]
    assert (
        call["url"]
        == "https://portal.sso.us-west-2.amazonaws.com/federation/credentials"
    )
    assert call["params"] == {
        "account_id": "123456789012",
        "role_name": "WorkforceReader",
    }
    assert call["headers"] == {"x-amz-sso_bearer_token": "access-token"}
    assert call["timeout"] == 30


@pytest.mark.unit
def test_resolver_role_credentials_other_region(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get = _FakeHttpGet(_role_creds())
    monkeypatch.setattr("httpx.get", get)
    resolver = AwsIdentityResolver(
        region="eu-west-1",
        sso_region="eu-west-1",
        identity_store_id="d-999",
        account_id="999999999999",
        role_name="Reader",
    )
    resolver._get_role_credentials("tok")
    assert get.calls[0]["url"] == (
        "https://portal.sso.eu-west-1.amazonaws.com/federation/credentials"
    )


@pytest.mark.unit
def test_resolver_lookup_user_min_forwards_role_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get = _FakeHttpGet(_role_creds())
    store = _FakeIdentityStore([_user()])
    sessions: list[_FakeSession] = []

    def _make_session(**kwargs: Any) -> _FakeSession:
        session = _FakeSession(store, **kwargs)
        sessions.append(session)
        return session

    monkeypatch.setattr("httpx.get", get)
    monkeypatch.setattr("boto3.Session", _make_session)
    result = _resolver().lookup_user_min("access-token")
    assert result == {
        "userId": "u-1",
        "userName": "jdoe",
        "displayName": "Jane Doe",
        "emails": ["jane@example.com"],
    }
    assert len(sessions) == 1
    assert sessions[0].kwargs == {
        "aws_access_key_id": "ak",
        "aws_secret_access_key": "sk",
        "aws_session_token": "st",
        "region_name": "us-east-1",
    }
    assert store.calls == [
        {"IdentityStoreId": "d-123", "MaxResults": 1},
    ]


@pytest.mark.unit
def test_resolver_lookup_user_min_lists_first_user_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # lookup_user_min lists one user (MaxResults=1); the returned record is
    # the first user in the store, which does not establish that it is the
    # authenticated caller.
    get = _FakeHttpGet(_role_creds())
    store = _FakeIdentityStore([_user("u-1"), _user("u-2")])
    monkeypatch.setattr("httpx.get", get)
    monkeypatch.setattr(
        "boto3.Session", lambda **kwargs: _FakeSession(store, **kwargs)
    )
    result = _resolver().lookup_user_min("access-token")
    assert result["userId"] == "u-1"


@pytest.mark.unit
def test_resolver_credentials_http_error_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get = _FakeHttpGet({"error": "boom"}, error=True)
    monkeypatch.setattr("httpx.get", get)
    with pytest.raises(httpx.HTTPStatusError):
        _resolver()._get_role_credentials("access-token")


@pytest.mark.unit
def test_resolver_missing_role_credentials_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get = _FakeHttpGet({})
    monkeypatch.setattr("httpx.get", get)

    def unexpected_session(**kwargs: Any):
        pytest.fail("Missing role credentials must not create an AWS session")

    monkeypatch.setattr("boto3.Session", unexpected_session)
    # The original resolver raises KeyError; #6345 raises ValueError.
    with pytest.raises((KeyError, ValueError), match="roleCredentials"):
        _resolver().lookup_user_min("access-token")


@pytest.mark.unit
def test_resolver_lookup_user_min_empty_users_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Current behavior, recorded: an empty Users list raises IndexError.
    get = _FakeHttpGet(_role_creds())
    store = _FakeIdentityStore([])
    monkeypatch.setattr("httpx.get", get)
    monkeypatch.setattr(
        "boto3.Session", lambda **kwargs: _FakeSession(store, **kwargs)
    )
    with pytest.raises(IndexError):
        _resolver().lookup_user_min("access-token")
