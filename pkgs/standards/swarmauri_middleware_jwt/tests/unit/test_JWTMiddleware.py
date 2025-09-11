from unittest.mock import AsyncMock, Mock

import jwt
import pytest
from fastapi import HTTPException, Request
from swarmauri_middleware_jwt.JWTMiddleware import JWTMiddleware


@pytest.fixture
def middleware():
    return JWTMiddleware(secret_key="secret")


@pytest.fixture
def valid_token():
    payload = {"sub": "user"}
    return jwt.encode(payload, "secret", algorithm="HS256")


@pytest.fixture
def mock_request(valid_token):
    req = Mock(spec=Request)
    req.headers = {"Authorization": f"Bearer {valid_token}"}
    req.state = Mock()
    return req


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_valid_token(middleware, mock_request):
    call_next = AsyncMock(return_value="ok")
    result = await middleware.dispatch(mock_request, call_next)
    assert result == "ok"
    assert mock_request.state.jwt_payload["sub"] == "user"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_missing_header(middleware):
    req = Mock(spec=Request)
    req.headers = {}
    req.state = Mock()
    call_next = AsyncMock()
    with pytest.raises(HTTPException):
        await middleware.dispatch(req, call_next)
    call_next.assert_not_called()
