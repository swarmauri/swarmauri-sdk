from datetime import datetime
from unittest import mock

import pytest
from fastapi import Request, Response
from swarmauri_middleware_cachecontrol.CacheControlMiddleware import (
    CacheControlMiddleware,
)


@pytest.mark.unit
class TestCacheControlMiddleware:
    """Unit tests for CacheControlMiddleware class."""

    @pytest.fixture()
    def middleware(self):
        return CacheControlMiddleware()

    def test_ubc_type(self, middleware):
        """Test the type attribute of CacheControlMiddleware."""
        assert middleware.type == "CacheControlMiddleware"

    def test_ubc_resource(self, middleware):
        """Test the resource attribute of CacheControlMiddleware."""
        assert middleware.resource == "Middleware"

    def test_serialization(self, middleware):
        """Test serialization of CacheControlMiddleware instance."""
        serialized = middleware.model_dump_json()
        assert (
            CacheControlMiddleware.model_validate_json(serialized).id == middleware.id
        )

    def test_default(self, middleware):
        """Test default value of max_age attribute."""
        assert middleware.max_age == 3600
        assert middleware.enabled is True

    def test_custom(self):
        """Test custom value of max_age attribute."""
        middleware = CacheControlMiddleware(max_age=7200, enabled=False)
        assert middleware.max_age == 7200
        assert middleware.enabled is False

    @pytest.mark.asyncio
    async def test_dispatch_enabled(self):
        """Test dispatch method when enabled is True."""
        middleware = CacheControlMiddleware()
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
        }
        request = Request(scope=scope, receive=lambda: b"")

        async def call_next(request):
            response = Response(content=b"Test content")
            return response

        response = await middleware.dispatch(request, call_next)
        assert isinstance(response, Response)
        assert "Cache-Control" in response.headers
        assert "ETag" in response.headers
        assert "Vary" in response.headers

    @pytest.mark.asyncio
    async def test_dispatch_disabled(self):
        """Test dispatch method when enabled is False."""
        middleware = CacheControlMiddleware(enabled=False)
        request = Request(scope={"type": "http"})

        async def call_next(request):
            response = Response(content=b"Test content")
            return response

        response = await middleware.dispatch(request, call_next)
        assert isinstance(response, Response)
        assert "Cache-Control" not in response.headers
        assert "ETag" not in response.headers
        assert "Vary" not in response.headers

    def test_set_cache_control_headers(self):
        """Test setting of cache control headers."""
        middleware = CacheControlMiddleware()
        response = Response(content=b"Test content")
        middleware._set_cache_control_headers(response)
        assert "Cache-Control" in response.headers
        assert "max-age" in response.headers["Cache-Control"]
        assert "public" in response.headers["Cache-Control"]
        assert "ETag" in response.headers
        assert "Vary" in response.headers

    @pytest.mark.asyncio
    async def test_handle_conditional_request_if_modified_since(self):
        """Test handling of If-Modified-Since header."""
        middleware = CacheControlMiddleware()
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [[b"if-modified-since", b"Wed, 21 Oct 2020 07:28:00 GMT"]],
        }
        request = Request(scope=scope, receive=lambda: b"")
        response = Response(content=b"Test content")

        modified_since = datetime.strptime(
            "Wed, 21 Oct 2020 07:28:00 GMT", "%a, %d %b %Y %H:%M:%S %Z"
        ).timestamp()

        earlier_time = datetime.fromtimestamp(modified_since - 100)

        with mock.patch(
            "swarmauri_middleware_cachecontrol.CacheControlMiddleware.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = earlier_time
            mock_datetime.strptime = datetime.strptime

            result = await middleware._handle_conditional_request(request, response)
            assert result is True

    @pytest.mark.asyncio
    async def test_handle_conditional_request_if_none_match(self):
        """Test handling of If-None-Match header."""
        middleware = CacheControlMiddleware()
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [[b"if-none-match", b'"12345"']],
        }
        request = Request(scope=scope, receive=lambda: b"")
        response = Response(content=b"Test content")
        response.headers["ETag"] = '"12345"'

        result = await middleware._handle_conditional_request(request, response)
        assert result is True

    @pytest.mark.asyncio
    async def test_handle_conditional_request_no_match(self):
        """Test handling when no conditional headers match."""
        middleware = CacheControlMiddleware()
        # Fix: Add headers to scope
        scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
        request = Request(scope=scope, receive=lambda: b"")
        response = Response(content=b"Test content")

        result = await middleware._handle_conditional_request(request, response)
        assert result is False

    @pytest.mark.asyncio
    async def test_send_not_modified(self):
        """Test sending of 304 Not Modified response."""
        middleware = CacheControlMiddleware()
        response = Response(content=b"Test content")

        result = await middleware._send_not_modified(response)
        assert response.status_code == 304
        assert response.body == b""
        assert "Cache-Control" in response.headers
        assert "ETag" in response.headers
        assert "Vary" in response.headers
        assert result is True
