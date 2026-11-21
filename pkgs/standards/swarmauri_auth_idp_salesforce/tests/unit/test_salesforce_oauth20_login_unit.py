import json
from urllib.parse import parse_qs, urlsplit

import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_salesforce import SalesforceOAuth20Login


@pytest.fixture
def login() -> SalesforceOAuth20Login:
    instance = SalesforceOAuth20Login(
        base_url="https://login.salesforce.com",
        client_id="client",
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance.AUTH_PATH = "/services/oauth2/authorize"
    instance.TOKEN_PATH = "/services/oauth2/token"
    instance.USERINFO_PATH = "/services/oauth2/userinfo"
    return instance


@pytest.mark.unit
def test_resource(login: SalesforceOAuth20Login) -> None:
    assert login.resource == "OAuth20Login"


@pytest.mark.unit
def test_type(login: SalesforceOAuth20Login) -> None:
    assert login.type == "SalesforceOAuth20Login"


@pytest.mark.unit
def test_serialization(login: SalesforceOAuth20Login) -> None:
    payload = json.loads(login.model_dump_json())

    restored = SalesforceOAuth20Login.model_construct(**payload)
    restored.client_secret = login.client_secret
    restored.state_secret = login.state_secret

    assert restored.id == login.id
    assert restored.resource == login.resource
    assert restored.type == login.type


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_contains_salesforce(
    login: SalesforceOAuth20Login,
) -> None:
    payload = await login.auth_url()
    assert payload["url"].startswith(
        "https://login.salesforce.com/services/oauth2/authorize?"
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_invalid_state(login: SalesforceOAuth20Login) -> None:
    with pytest.raises(ValueError):
        await login.exchange_and_identity("code", "invalid-state")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_url_encodes_special_characters(
    login: SalesforceOAuth20Login,
) -> None:

    login.client_id = "client&admin=true+test"
    login.redirect_uri = "https://example.com/callback?next=/home&a=1+2"
    login.scope = "refresh_token profile+email=café"

    payload = await login.auth_url()
    params = parse_qs(urlsplit(payload["url"]).query)

    assert params["client_id"] == [login.client_id]
    assert params["redirect_uri"] == [login.redirect_uri]
    assert params["scope"] == [login.scope]
    assert "admin" not in params
    assert params["code_challenge_method"] == ["S256"]
    assert params["state"] == [payload["state"]]
