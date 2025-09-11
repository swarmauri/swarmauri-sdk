import pytest
from fastapi import Request, Response
from swarmauri_middleware_gzipcompression.GzipCompressionMiddleware import (
    GzipCompressionMiddleware,
)


@pytest.mark.unit
class TestGzipCompressionMiddleware:
    """Unit tests for GzipCompressionMiddleware."""

    def test_init(self):
        """Test initialization of GzipCompressionMiddleware."""
        middleware = GzipCompressionMiddleware()
        assert middleware.type == "GzipCompressionMiddleware"

    @pytest.mark.asyncio  # Add this decorator
    async def test_dispatch_with_gzip_support(self):
        """Test dispatch with gzip support."""
        middleware = GzipCompressionMiddleware()

        # Create a request with gzip support
        scope = {
            "type": "http",
            "method": "GET",
            "headers": [[b"accept-encoding", b"gzip"]],
        }
        request = Request(scope=scope, receive=lambda: b"")

        # Mock response
        original_response = Response(
            content="Test content", media_type="application/json"
        )

        async def mock_call_next(req):
            return original_response

        # Fix: Add await here
        response = await middleware.dispatch(request, mock_call_next)

        # Verify gzip compression was applied
        assert response.headers.get("Content-Encoding") == "gzip"
        assert "Content-Length" in response.headers

    @pytest.mark.asyncio  # Add this decorator
    async def test_dispatch_without_gzip_support(self):
        """Test dispatch without gzip support."""
        middleware = GzipCompressionMiddleware()

        # Create a request without gzip support
        scope = {
            "type": "http",
            "method": "GET",
            "headers": [],
        }
        request = Request(scope=scope, receive=lambda: b"")

        # Mock response
        original_response = Response(
            content="Test content", media_type="application/json"
        )

        async def mock_call_next(req):
            return original_response

        # Fix: Add await here
        response = await middleware.dispatch(request, mock_call_next)

        # Verify no compression was applied
        assert (
            "Content-Encoding" not in response.headers
            or response.headers.get("Content-Encoding") != "gzip"
        )

    @pytest.mark.asyncio  # Add this decorator
    async def test_dispatch_already_compressed(self):
        """Test dispatch with already compressed response."""
        middleware = GzipCompressionMiddleware()

        # Create a request with gzip support
        scope = {
            "type": "http",
            "method": "GET",
            "headers": [[b"accept-encoding", b"gzip"]],
        }
        request = Request(scope=scope, receive=lambda: b"")

        # Mock already compressed response
        original_response = Response(
            content="Test content",
            headers={"Content-Encoding": "gzip"},
            media_type="application/json",
        )

        async def mock_call_next(req):
            return original_response

        # Fix: Add await here
        response = await middleware.dispatch(request, mock_call_next)

        # Verify response is unchanged
        assert response == original_response

    @pytest.mark.asyncio  # Add this decorator
    async def test_dispatch_non_compressible_content(self):
        """Test dispatch with non-compressible content type."""
        middleware = GzipCompressionMiddleware()

        # Create a request with gzip support
        scope = {
            "type": "http",
            "method": "GET",
            "headers": [[b"accept-encoding", b"gzip"]],
        }
        request = Request(scope=scope, receive=lambda: b"")

        # Mock response with non-compressible content
        original_response = Response(content=b"binary data", media_type="image/png")

        async def mock_call_next(req):
            return original_response

        # Fix: Add await here
        response = await middleware.dispatch(request, mock_call_next)

        # Verify no compression was applied
        assert (
            "Content-Encoding" not in response.headers
            or response.headers.get("Content-Encoding") != "gzip"
        )

    @pytest.mark.asyncio  # Add this decorator
    async def test_dispatch_non_response_object(self):
        """Test dispatch with non-Response return value."""
        middleware = GzipCompressionMiddleware()

        scope = {
            "type": "http",
            "method": "GET",
            "headers": [[b"accept-encoding", b"gzip"]],
        }
        request = Request(scope=scope, receive=lambda: b"")

        # Mock call_next returning non-Response object
        non_response = {"message": "Not a response"}

        async def mock_call_next(req):
            return non_response

        # Fix: Add await here
        response = await middleware.dispatch(request, mock_call_next)

        # Verify original object is returned unchanged
        assert response == non_response
