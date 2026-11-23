"""Unit tests for the Cognito ID-token algorithm allowlist (#6279).

``CognitoLoginMixin._decode_id_token`` must only accept ID tokens signed
with an algorithm from the implementation-owned allowlist (RS256, the only
algorithm Amazon Cognito user pools use to sign ID tokens). The allowlist
is never taken from the token's unverified ``alg`` header, so tokens that
claim an unsupported algorithm, claim no algorithm, or are unsigned are
rejected before signature verification.

Everything runs offline: the JWKS endpoint is stubbed to serve a local
throwaway RSA key, and the tokens are minted with that key. No network
access, credentials, or live Cognito account are needed, and nothing here
proves interoperability with Cognito's production service.
"""

from __future__ import annotations

import base64
import json
import time
from collections.abc import Mapping
from typing import Any

import jwt
import pytest
from pydantic import SecretBytes, SecretStr

from swarmauri_auth_idp_cognito import CognitoOIDC10Login

ISSUER = "https://cognito.example"
CLIENT_ID = "client"
JWKS_URI = "https://cognito.example/jwks"

# Throwaway RSA key for these tests only. The private half signs the ID
# tokens below; the public half is served through the stubbed JWKS
# endpoint. It is never used outside this file.
TEST_PRIVATE_KEY_PEM = (
    "-----BEGIN PRIVATE KEY-----\n"
    "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDsn4gUPdQqJ8d7\n"
    "WFYfJqHtnGMgNg47x887hnQEW3NlNNb8J4C8lCZMh4Zgnc+9zuCkWFj57PlRvNTS\n"
    "uCBlrRn2LSRbwN3c8LceqZyOb1dutAFkyRuKX/c6eW9g1LHBM3r/TQ9FZU95VKbu\n"
    "KbntCSV3CmPRqimnwcKOCZIxGwPD+6cN5kwW3VgYiLHNp07C3Y8r8+WlNGufBh1G\n"
    "TLeJypUc57k1nNNXG8uqKr2u1VVl7bbJWWBaED4HYXd1bS9guCaPbGCZwTlb1/nG\n"
    "zwpnIYabko57ZN7L8YruSm+qVP3zLxNR3lw1awW7/bNmOHXfT1b8S0OfjesiuU0r\n"
    "ILr0WrGjAgMBAAECggEADK9QHlkZmr4RwACUvDDF2cc1uuJ4rSbharPsEtcnEO9w\n"
    "XmT/KZzZReZtcQXt437aEqelzpXUlzMD2biVeb3nuD5R2Mw2fSgS7+CVQvYN6/3F\n"
    "gVrwUE6Rj+jIo1E/FIEVAHnVgHUDMKt+7ti0XeaDw8oQXvjgce8ZCn/2R6B9i52M\n"
    "mpY0vugzRKjPcdL4ix5gsAgWOnBcoXJbueOQS2OeX7IPkh8+YoZWo436UteOZNvO\n"
    "TOnpWbirJdfTfX+e96D9i1kh4it+J7LeWrQ3TmuS+tGqeJQkKCERXAha32z4vr+e\n"
    "Gi3Ix17+KKzN5OJFKsU74GSe3zW+4P4zWDRTVj8LkQKBgQD+fXZIivX9+70BTxUo\n"
    "iuKLmCuDyXMokhoPdTSM80XIAiKk7un+mV0Vfgx3Ir8ynmGsMlAAZoPhFaxWkgVz\n"
    "uF+n5zRHE0TrUG6mSRBwamZMYqV1ta6pmgQuqP3BQBVDaKwGfR3Y2p1iNGdXae/o\n"
    "AEP3Xva3lH9tSQl/Z+knNG3p2wKBgQDuBu6UQtVMtHSzSjupVxb6PcvRu3ahomnJ\n"
    "qIyai5MHAqaSClj7MJeKDe1xd9lL0Iliwf3Pu/CFpkhN8AjBHWHkbTXq68NYu0cT\n"
    "O8T4qsFPAz031k/W7ZKbOEb720vyhdJxjrcIfakQHTnhvRYDNCzQSFemjDFuAV9L\n"
    "DXiWIimV2QKBgHUvjKIG6xNTMktCATo0CfHB1nfO8apC7KEllVc6Rm29HfrY0QMd\n"
    "19Enw9GwPF6ws8U5PcGRczTYaA1NHBmXUuTcACSiaN/6n5kOl/VL6WNPIWW8jXsn\n"
    "orlhs8ejHKd3sY8jWfUbZdFs1BFahNBOHv3vyqfqR2spcKgsTx5wdBR1AoGAEytf\n"
    "v3T6dKj71QyfbW3kHdcoOQXd8fqAhosad7/R4XinLY/DxscNDUM94iuCxoZO6jMx\n"
    "W6+JGVpg7FXufo79OUZKV1cRbm32tWfU3ynxU4mxPnP2Dhsn+XQ400PABBIe9qJF\n"
    "v1tPaErSRInT4gIrscKBvJoByRg3MnYtRfoOW1ECgYAVGNrcLRZgPuMahkntlV26\n"
    "07gjPWEHNULkb75Oz9q+HBz//idWBRYaBrDJhgQlK6j5BZFPHjjwdKWxxo6PZ3Fz\n"
    "+e7KLS8QS0LZAX7PCSN+hL4xw3gQ+IWSAD37B9azUrRUlJsCPtfRU4yRmywl12GU\n"
    "TDMDED07kAvv9W5bGF6/XQ==\n"
    "-----END PRIVATE KEY-----\n"
)
TEST_JWK = {
    "kty": "RSA",
    "kid": "test-key-1",
    "use": "sig",
    "alg": "RS256",
    "n": (
        "7J-IFD3UKifHe1hWHyah7ZxjIDYOO8fPO4Z0BFtzZTTW_CeAvJQmTIeGYJ3Pvc7g"
        "pFhY-ez5UbzU0rggZa0Z9i0kW8Dd3PC3Hqmcjm9XbrQBZMkbil_3OnlvYNSxwTN6"
        "_00PRWVPeVSm7im57Qkldwpj0aopp8HCjgmSMRsDw_unDeZMFt1YGIixzadOwt2P"
        "K_PlpTRrnwYdRky3icqVHOe5NZzTVxvLqiq9rtVVZe22yVlgWhA-B2F3dW0vYLgm"
        "j2xgmcE5W9f5xs8KZyGGm5KOe2Tey_GK7kpvqlT98y8TUd5cNWsFu_2zZjh1309W"
        "_EtDn43rIrlNKyC69Fqxow"
    ),
    "e": "AQAB",
}
TEST_JWKS = {"keys": [TEST_JWK]}


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _claims(**overrides: Any) -> dict[str, Any]:
    now = int(time.time())
    claims = {
        "sub": "user-123",
        "email": "user@example.com",
        "iss": ISSUER,
        "aud": CLIENT_ID,
        "iat": now,
        "exp": now + 3600,
    }
    claims.update(overrides)
    return claims


def _mint_token(
    *, algorithm: str = "RS256", key: Any = TEST_PRIVATE_KEY_PEM, **claims: Any
) -> str:
    return jwt.encode(
        _claims(**claims),
        key,
        algorithm=algorithm,
        headers={"kid": "test-key-1"},
    )


def _mint_token_without_alg() -> str:
    header = _b64url(
        json.dumps({"kid": "test-key-1", "typ": "JWT"}).encode("utf-8")
    )
    payload = _b64url(json.dumps(_claims()).encode("utf-8"))
    return f"{header}.{payload}."


@pytest.fixture
def login() -> CognitoOIDC10Login:
    instance = CognitoOIDC10Login(
        issuer=ISSUER,
        client_id=CLIENT_ID,
        client_secret=SecretStr("secret"),
        redirect_uri="https://example.com/callback",
        state_secret=SecretBytes(b"state-secret"),
    )
    instance._discovery = {
        "authorization_endpoint": "https://cognito.example/authorize",
        "token_endpoint": "https://cognito.example/token",
        "jwks_uri": JWKS_URI,
    }
    return instance


@pytest.fixture
def stubbed_jwks(login: CognitoOIDC10Login) -> CognitoOIDC10Login:
    async def fake_http_get(
        url: str, *, headers: Mapping[str, str] | None = None
    ) -> Mapping[str, Any]:
        assert url == JWKS_URI
        return TEST_JWKS

    login._http_get = fake_http_get  # type: ignore[method-assign]
    return login


@pytest.mark.unit
@pytest.mark.asyncio
async def test_valid_rs256_token_decodes(
    stubbed_jwks: CognitoOIDC10Login,
) -> None:
    token = _mint_token()
    claims = await stubbed_jwks._decode_id_token(
        token,
        jwks_uri=JWKS_URI,
        expected_audience=CLIENT_ID,
        issuer=ISSUER,
    )
    assert claims["sub"] == "user-123"
    assert claims["email"] == "user@example.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hs256_token_rejected(stubbed_jwks: CognitoOIDC10Login) -> None:
    token = _mint_token(algorithm="HS256", key="shared-secret")
    with pytest.raises(ValueError, match="unsupported id_token"):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_unsigned_token_rejected(
    stubbed_jwks: CognitoOIDC10Login,
) -> None:
    token = _mint_token(algorithm="none", key=None)
    with pytest.raises(ValueError, match="unsupported id_token"):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_missing_alg_rejected(stubbed_jwks: CognitoOIDC10Login) -> None:
    token = _mint_token_without_alg()
    with pytest.raises(ValueError, match="missing alg"):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_missing_kid_rejected(stubbed_jwks: CognitoOIDC10Login) -> None:
    token = jwt.encode(
        _claims(),
        TEST_PRIVATE_KEY_PEM,
        algorithm="RS256",
        headers={"typ": "JWT"},
    )
    with pytest.raises(ValueError, match="missing kid"):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_expired_token_rejected(
    stubbed_jwks: CognitoOIDC10Login,
) -> None:
    token = _mint_token(exp=int(time.time()) - 60)
    with pytest.raises(jwt.ExpiredSignatureError):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_wrong_audience_rejected(
    stubbed_jwks: CognitoOIDC10Login,
) -> None:
    token = _mint_token(aud="other-client")
    with pytest.raises(jwt.InvalidAudienceError):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_wrong_issuer_rejected(
    stubbed_jwks: CognitoOIDC10Login,
) -> None:
    token = _mint_token(iss="https://cognito.other")
    with pytest.raises(jwt.InvalidIssuerError):
        await stubbed_jwks._decode_id_token(
            token,
            jwks_uri=JWKS_URI,
            expected_audience=CLIENT_ID,
            issuer=ISSUER,
        )
