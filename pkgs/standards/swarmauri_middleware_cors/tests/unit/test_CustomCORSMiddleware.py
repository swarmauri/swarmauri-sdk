import pytest
from fastapi import Request, Response
from swarmauri_middleware_cors.CustomCORSMiddleware import CustomCORSMiddleware


@pytest.fixture
def middleware():
    """Fixture providing a default CustomCORSMiddleware instance."""
    return CustomCORSMiddleware(
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[],
        max_age=600,
    )


@pytest.mark.unit
def test_init(middleware):
    """Test CustomCORSMiddleware initialization."""
    assert middleware.allow_origins == ["*"]
    assert middleware.allow_credentials is True
    assert middleware.allow_methods == ["*"]
    assert middleware.allow_headers == ["*"]
    assert middleware.expose_headers == []
    assert middleware.max_age == 600


@pytest.mark.asyncio
@pytest.mark.unit
async def test_dispatch_get_request(middleware):
    """Test dispatch method with a GET request."""
    # Fix: Create proper ASGI scope
    scope = {"type": "http", "method": "GET", "headers": []}
    request = Request(scope=scope, receive=lambda: b"")

    async def call_next(request):
        return Response(content="Test response")

    response = await middleware.dispatch(request, call_next)
    assert response is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_is_options_request_true(middleware):
    """Test is_options_request with OPTIONS method."""
    # Fix: Add type to scope
    scope = {"type": "http", "method": "OPTIONS", "headers": []}
    request = Request(scope=scope, receive=lambda: b"")
    assert await middleware.is_options_request(request) is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_is_options_request_false(middleware):
    """Test is_options_request with GET method."""
    # Fix: Add type to scope
    scope = {"type": "http", "method": "GET", "headers": []}
    request = Request(scope=scope, receive=lambda: b"")
    assert await middleware.is_options_request(request) is False


@pytest.mark.asyncio
@pytest.mark.unit
async def test_check_cors_origin_allowed():
    """Test check_cors_origin with allowed origin."""
    middleware = CustomCORSMiddleware(allow_origins=["http://test.com"])
    origin = "http://test.com"
    assert await middleware.check_cors_origin(origin) is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_check_cors_origin_disallowed():
    """Test check_cors_origin with disallowed origin."""
    middleware = CustomCORSMiddleware(allow_origins=["http://test.com"])
    origin = "http://other.com"
    assert await middleware.check_cors_origin(origin) is False


@pytest.mark.asyncio
@pytest.mark.unit
async def test_handle_options_request(middleware):
    """Test handle_options_request method."""
    # Fix: Add type to scope
    scope = {"type": "http", "method": "OPTIONS", "headers": []}
    request = Request(scope=scope, receive=lambda: b"")
    response = await middleware.handle_options_request(request)
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers


@pytest.mark.asyncio
@pytest.mark.unit
async def test_add_cors_headers(middleware):
    """Test add_cors_headers method."""
    response = Response()
    response = await middleware.add_cors_headers(response)

    assert response.headers["Access-Control-Allow-Origin"] == ",".join(["*"])
    assert response.headers["Access-Control-Allow-Methods"] == ",".join(["*"])
    assert response.headers["Access-Control-Allow-Headers"] == ",".join(["*"])
    assert response.headers["Access-Control-Expose-Headers"] == ",".join([])
    assert response.headers["Access-Control-Allow-Credentials"] == "true"
    assert response.headers["Access-Control-Max-Age"] == "600"


@pytest.mark.unit
def test_get_cors_error_response(middleware):
    """Test get_cors_error_response method."""
    response = middleware.get_cors_error_response("Test error")
    assert response.status_code == 403
    assert response.body == b"Test error"
