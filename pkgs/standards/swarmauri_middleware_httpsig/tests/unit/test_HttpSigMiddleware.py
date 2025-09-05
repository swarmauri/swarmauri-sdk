import base64
import hashlib
import hmac
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException
from swarmauri_middleware_httpsig.HttpSigMiddleware import HttpSigMiddleware


@pytest.fixture
def middleware():
    return HttpSigMiddleware(secret_key="secret")


@pytest.fixture
def mock_request():
    request = Mock()
    request.headers = {}
    request.body = AsyncMock(return_value=b"payload")
    return request


@pytest.mark.unit
def test_ubc_type(middleware):
    assert middleware.type == "HttpSigMiddleware"


@pytest.mark.unit
def test_ubc_resource(middleware):
    assert middleware.resource == "Middleware"


@pytest.mark.unit
def test_serialization(middleware):
    serialized = middleware.model_dump_json()
    assert HttpSigMiddleware.model_validate_json(serialized).id == middleware.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_valid_signature(middleware, mock_request):
    digest = hmac.new(b"secret", b"payload", hashlib.sha256).digest()
    mock_request.headers[middleware.header_name] = base64.b64encode(digest).decode()
    call_next = AsyncMock(return_value="ok")
    result = await middleware.dispatch(mock_request, call_next)
    assert result == "ok"
    call_next.assert_called_once_with(mock_request)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_missing_signature(middleware, mock_request):
    call_next = AsyncMock()
    with pytest.raises(HTTPException):
        await middleware.dispatch(mock_request, call_next)
    call_next.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_invalid_signature(middleware, mock_request):
    mock_request.headers[middleware.header_name] = "invalid"
    call_next = AsyncMock()
    with pytest.raises(HTTPException):
        await middleware.dispatch(mock_request, call_next)
    call_next.assert_not_called()
