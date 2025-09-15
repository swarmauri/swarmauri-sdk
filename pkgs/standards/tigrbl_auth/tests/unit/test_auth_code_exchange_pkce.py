import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import Request

from tigrbl_auth.orm import AuthCode
from tigrbl_auth.rfc.rfc7636_pkce import makeCodeChallenge, makeCodeVerifier


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_accepts_hex_client_id(monkeypatch):
    verifier = makeCodeVerifier()
    challenge = makeCodeChallenge(verifier)
    client_uuid = uuid.uuid4()

    auth_code = AuthCode(
        id=uuid.uuid4(),
        client_id=client_uuid,
        redirect_uri="https://client/cb",
        code_challenge=challenge,
        nonce=None,
        scope=None,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        claims=None,
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
    )

    class DummyJWT:
        async def async_sign_pair(self, **kwargs):  # pragma: no cover - trivial
            return "access", "refresh"

    async def fake_mint(**kwargs):  # pragma: no cover - trivial
        return "id"

    async def fake_delete(payload):  # pragma: no cover - trivial
        return None

    monkeypatch.setattr("tigrbl_auth.orm.auth_code._jwt", DummyJWT())
    monkeypatch.setattr("tigrbl_auth.orm.auth_code.mint_id_token", fake_mint)
    monkeypatch.setattr(
        "tigrbl_auth.orm.auth_code.AuthCode.handlers.delete.core", fake_delete
    )

    request = Request(scope={"type": "http", "scheme": "https"})
    db = SimpleNamespace(get=lambda *args, **kwargs: None)
    payload = {
        "client_id": client_uuid.hex,
        "redirect_uri": "https://client/cb",
        "code_verifier": verifier,
    }

    result = await AuthCode.exchange(
        {"request": request, "db": db, "payload": payload}, auth_code
    )
    assert result["access_token"] == "access"
    assert result["refresh_token"] == "refresh"
    assert result["id_token"] == "id"
