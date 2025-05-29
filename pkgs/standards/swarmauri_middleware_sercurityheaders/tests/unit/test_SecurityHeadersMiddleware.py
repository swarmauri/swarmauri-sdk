import pytest
from fastapi import Request, Response
from fastapi.middleware import Middleware
from typing import Callable, Dict, Any
import logging
from swarmauri_middleware_sercurityheaders.SecurityHeadersMiddleware import SecurityHeadersMiddleware

@pytest.mark.unit
class TestSecurityHeadersMiddleware:
    """Unit tests for SecurityHeadersMiddleware class."""
    
    @pytest.mark.unit
    def test_securityheadersmiddleware_init(self):
        """Test initialization of SecurityHeadersMiddleware class."""
        # Arrange
        async def mock_app(request: Request, call_next: Callable[[Request], Response]) -> Response:
            return await call_next(request)
            
        # Act
        middleware = SecurityHeadersMiddleware(app=mock_app)
        
        # Assert
        assert isinstance(middleware, Middleware)
        assert hasattr(middleware, "app")
        assert middleware.app is mock_app

    @pytest.mark.unit
    async def test_dispatch(self, mocker):
        """Test dispatch method of SecurityHeadersMiddleware."""
        # Arrange
        mock_request = mocker.Mock(spec=Request)
        async def mock_call_next(request: Request) -> Response:
            response = Response()
            return response
            
        middleware = SecurityHeadersMiddleware(app=mock_call_next)
        
        # Spy the _add_security_headers method
        spy_add_headers = mocker.spy(middleware, "_add_security_headers")
        
        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)
        
        # Assert
        assert isinstance(response, Response)
        spy_add_headers.assert_called_once_with(response)
        
    @pytest.mark.unit
    def test_add_security_headers(self, mocker):
        """Test _add_security_headers method."""
        # Arrange
        mock_response = mocker.Mock(spec=Response)
        middleware = SecurityHeadersMiddleware(app=lambda *_: mocker.Mock())
        
        # Act
        middleware._add_security_headers(mock_response)
        
        # Assert
        # Verify all security headers are added
        expected_headers: Dict[str, str] = {
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' https://cdn.example.com; "
                "style-src 'self' https://cdn.example.com; "
                "img-src 'self' https://images.example.com; "
                "font-src 'self' https://fonts.example.com"
            ),
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": (
                "max-age=31536000; "
                "includeSubDomains; "
                "preload"
            ),
            "Referrer-Policy": "same-origin",
            "Permissions-Policy": (
                "interest-cohort=(), "
                "geolocation=(self), "
                "microphone=(), "
                "camera=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=(self), "
                "vibrate=(), "
                "payment=()"
            )
        }
        
        for header, value in expected_headers.items():
            assert mock_response.headers.get(header) == value