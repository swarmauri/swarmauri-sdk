import pytest
from fastapi import Request, Response
from datetime import datetime
import logging
from swarmauri_middleware_cachecontrol.CacheControlMiddleware import CacheControlMiddleware

@pytest.mark.unit
class TestCacheControlMiddleware:
    """Unit tests for CacheControlMiddleware class."""
    
    def test_type_attribute(self):
        """Test the type attribute of CacheControlMiddleware."""
        assert CacheControlMiddleware.type == "CacheControlMiddleware"
        
    def test_max_age_default(self):
        """Test default value of max_age attribute."""
        middleware = CacheControlMiddleware()
        assert middleware.max_age == 3600
        
    def test_max_age_custom(self):
        """Test custom value of max_age attribute."""
        middleware = CacheControlMiddleware(max_age=7200)
        assert middleware.max_age == 7200
        
    def test_enabled_default(self):
        """Test default value of enabled attribute."""
        middleware = CacheControlMiddleware()
        assert middleware.enabled is True
        
    def test_enabled_custom(self):
        """Test custom value of enabled attribute."""
        middleware = CacheControlMiddleware(enabled=False)
        assert middleware.enabled is False
        
    def test_init(self):
        """Test initialization of CacheControlMiddleware."""
        middleware = CacheControlMiddleware()
        assert isinstance(middleware.logger, logging.Logger)
        
    @pytest.mark.asyncio
    async def test_dispatch_enabled(self):
        """Test dispatch method when enabled is True."""
        middleware = CacheControlMiddleware()
        request = Request(scope={"type": "http"})
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
        request = Request(scope={"type": "http"}, headers={"If-Modified-Since": "Wed, 21 Oct 2020 07:28:00 GMT"})
        response = Response(content=b"Test content")
        
        modified_since = datetime.strptime(
            "Wed, 21 Oct 2020 07:28:00 GMT",
            "%a, %d %b %Y %H:%M:%S %Z"
        ).timestamp()
        
        current_time = datetime.now().timestamp()
        
        # Mock current time to be before modified_since
        with pytest.mock.patch("datetime.datetime.now") as mock_now:
            mock_now.return_value.timestamp = modified_since - 100
            result = await middleware._handle_conditional_request(request, response)
            assert result is True
            
    @pytest.mark.asyncio
    async def test_handle_conditional_request_if_none_match(self):
        """Test handling of If-None-Match header."""
        middleware = CacheControlMiddleware()
        request = Request(scope={"type": "http"}, headers={"If-None-Match": '"12345"'})
        response = Response(content=b"Test content")
        response.headers["ETag"] = '"12345"'
        
        result = await middleware._handle_conditional_request(request, response)
        assert result is True
        
    @pytest.mark.asyncio
    async def test_handle_conditional_request_no_match(self):
        """Test handling when no conditional headers match."""
        middleware = CacheControlMiddleware()
        request = Request(scope={"type": "http"})
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