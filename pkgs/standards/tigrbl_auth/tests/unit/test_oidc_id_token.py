import base64
import json

import asyncio
import pytest

from tigrbl_auth.oidc_id_token import mint_id_token, verify_id_token


@pytest.mark.unit
@pytest.mark.usefixtures("temp_key_file")
def test_mint_and_verify_id_token():
    token = asyncio.run(
        mint_id_token(
            sub="user1",
            aud="client1",
            nonce="n-0S6_WzA2Mj",
            issuer="https://example.com",
        )
    )
    header_b64, payload_b64, _ = token.split(".")
    header = json.loads(base64.urlsafe_b64decode(header_b64 + "=="))
    assert header["alg"] == "RS256"

    claims = asyncio.run(
        verify_id_token(token, issuer="https://example.com", audience="client1")
    )
    assert claims["sub"] == "user1"
    assert claims["aud"] == "client1"
    assert claims["iss"] == "https://example.com"
    assert claims["nonce"] == "n-0S6_WzA2Mj"
    assert "exp" in claims and "iat" in claims
