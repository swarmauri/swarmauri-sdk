import hashlib
import json
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_github import GitHubOAuth20Login
from swarmauri_base.auth_idp.utils import base64url_encode, verify_state

TOKENS = {
    "access_token": "gho_test",
    "token_type": "bearer",
    "scope": "read:user,user:email",
}
API_HEADERS = {
    "Authorization": "Bearer gho_test",
    "Accept": "application/vnd.github+json",
}


@pytest.fixture
def login() -> GitHubOAuth20Login:
    return GitHubOAuth20Login(
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"signing-secret"),
    )


@pytest.mark.unit
def test_resource(login: GitHubOAuth20Login) -> None:
    assert login.resource == "OAuth20Login"


@pytest.mark.unit
def test_type(login: GitHubOAuth20Login) -> None:
    assert login.type == "GitHubOAuth20Login"


@pytest.mark.unit
def test_serialization_round_trip(login: GitHubOAuth20Login) -> None:
    serialized = login.model_dump_json()
    payload = json.loads(serialized)

    restored = GitHubOAuth20Login.model_construct(**payload)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_contains_github_base(
    login: GitHubOAuth20Login,
) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith(
        "https://github.com/login/oauth/authorize?"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: GitHubOAuth20Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange_and_identity("code", "invalid-state")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_query_parameters(login: GitHubOAuth20Login) -> None:
    payload = await login.auth_url()
    parts = urlsplit(payload["url"])
    query = parse_qs(parts.query)

    assert (parts.scheme, parts.netloc, parts.path) == (
        "https",
        "github.com",
        "/login/oauth/authorize",
    )
    assert query["client_id"] == ["client"]
    assert query["redirect_uri"] == ["https://example.com/callback"]
    assert query["scope"] == ["read:user user:email"]
    assert query["state"] == [payload["state"]]
    assert query["code_challenge_method"] == ["S256"]
    verifier = verify_state(b"signing-secret", payload["state"])["verifier"]
    expected_challenge = base64url_encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    )
    assert query["code_challenge"] == [expected_challenge]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_and_identity_contract(
    login: GitHubOAuth20Login, recording_client
) -> None:
    state = (await login.auth_url())["state"]
    verifier = verify_state(b"signing-secret", state)["verifier"]
    user = {
        "id": 101,
        "login": "octocat",
        "name": "The Octocat",
        "email": "octocat@example.com",
    }
    stub = recording_client((200, TOKENS), (200, user))
    login.http_client_factory = lambda: stub  # type: ignore[assignment]

    identity = await login.exchange_and_identity("auth-code", state)

    assert identity == {
        "issuer": "github-oauth20",
        "sub": "101",
        "email": "octocat@example.com",
        "name": "The Octocat",
        "raw": {"tokens": TOKENS, "user": user},
    }
    token_request, user_request = stub.requests
    assert token_request.method == "POST"
    assert token_request.url == "https://github.com/login/oauth/access_token"
    assert token_request.headers == {"Accept": "application/json"}
    assert token_request.data == {
        "client_id": "client",
        "client_secret": "secret",
        "code": "auth-code",
        "redirect_uri": "https://example.com/callback",
        "code_verifier": verifier,
    }
    assert user_request.method == "GET"
    assert user_request.url == "https://api.github.com/user"
    assert user_request.headers == API_HEADERS


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_looks_up_primary_verified_email(
    login: GitHubOAuth20Login, recording_client
) -> None:
    state = (await login.auth_url())["state"]
    user = {"id": 101, "login": "octocat", "name": None, "email": None}
    emails = [
        {"email": "secondary@example.com", "primary": False, "verified": True},
        {"email": "primary@example.com", "primary": True, "verified": True},
    ]
    stub = recording_client((200, TOKENS), (200, user), (200, emails))
    login.http_client_factory = lambda: stub  # type: ignore[assignment]

    identity = await login.exchange_and_identity("auth-code", state)

    assert identity["email"] == "primary@example.com"
    assert identity["name"] == "octocat"
    assert identity["raw"]["user"]["email"] == "primary@example.com"
    emails_request = stub.requests[2]
    assert emails_request.method == "GET"
    assert emails_request.url == "https://api.github.com/user/emails"
    assert emails_request.headers == API_HEADERS


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_email_falls_back_to_first_entry(
    login: GitHubOAuth20Login, recording_client
) -> None:
    # Current behavior: without a primary verified entry the first entry is
    # used, even when it is unverified.
    state = (await login.auth_url())["state"]
    user = {"id": 101, "login": "octocat", "email": None}
    emails = [
        {"email": "first@example.com", "primary": False, "verified": False},
        {"email": "second@example.com", "primary": True, "verified": False},
    ]
    stub = recording_client((200, TOKENS), (200, user), (200, emails))
    login.http_client_factory = lambda: stub  # type: ignore[assignment]

    identity = await login.exchange_and_identity("auth-code", state)

    assert identity["email"] == "first@example.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_oauth_and_api_base_overrides(
    login: GitHubOAuth20Login, recording_client
) -> None:
    login.oauth_base = "https://ghe.example.com/login/oauth/"
    login.api_base = "https://ghe.example.com/api/v3/"
    auth = await login.auth_url()
    user = {"id": 101, "login": "octocat", "email": None}
    stub = recording_client((200, TOKENS), (200, user), (200, []))
    login.http_client_factory = lambda: stub  # type: ignore[assignment]

    await login.exchange_and_identity("auth-code", auth["state"])

    assert auth["url"].startswith(
        "https://ghe.example.com/login/oauth/authorize?"
    )
    assert [request.url for request in stub.requests] == [
        "https://ghe.example.com/login/oauth/access_token",
        "https://ghe.example.com/api/v3/user",
        "https://ghe.example.com/api/v3/user/emails",
    ]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_token_http_error(
    login: GitHubOAuth20Login, recording_client
) -> None:
    state = (await login.auth_url())["state"]
    stub = recording_client((401, {"message": "Bad credentials"}))
    login.http_client_factory = lambda: stub  # type: ignore[assignment]

    with pytest.raises(httpx.HTTPStatusError):
        await login.exchange_and_identity("auth-code", state)
    assert len(stub.requests) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_missing_access_token(
    login: GitHubOAuth20Login, recording_client
) -> None:
    # Current behavior: GitHub reports bad codes with HTTP 200 and an error
    # body, which surfaces as KeyError before any profile request is made.
    state = (await login.auth_url())["state"]
    stub = recording_client((200, {"error": "bad_verification_code"}))
    login.http_client_factory = lambda: stub  # type: ignore[assignment]

    with pytest.raises(KeyError):
        await login.exchange_and_identity("auth-code", state)
    assert len(stub.requests) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_email_lookup_error_is_ignored(
    login: GitHubOAuth20Login, recording_client
) -> None:
    # Current behavior: email lookup failures are swallowed.
    state = (await login.auth_url())["state"]
    user = {"id": 101, "login": "octocat", "email": None}
    stub = recording_client(
        (200, TOKENS), (200, user), (403, {"message": "Forbidden"})
    )
    login.http_client_factory = lambda: stub  # type: ignore[assignment]

    identity = await login.exchange_and_identity("auth-code", state)

    assert identity["email"] is None
    assert identity["sub"] == "101"
