"""
Unit tests for AuthMiddleware class in the swarmauri_middleware_auth package.
"""

import pytest
from fastapi import HTTPException, Request
from swarmauri_middleware_auth.AuthMiddleware import AuthMiddleware


@pytest.mark.unit
class TestAuthMiddleware:
    """Unit test class for AuthMiddleware."""

    @pytest.fixture()
    def auth_middleware(self):
        """Fixture to set up the AuthMiddleware instance."""
        return AuthMiddleware()

    def test_resource(self, auth_middleware):
        """Test that the resource attribute is correctly set."""
        assert auth_middleware.resource == "Middleware"

    def test_type(self, auth_middleware):
        """Test that the type attribute is correctly set."""
        assert auth_middleware.type == "AuthMiddleware"

    @pytest.mark.parametrize(
        "header,expected_exception",
        [
            ("Bearer fake-token", None),
            ("", HTTPException),
            ("InvalidHeader", HTTPException),
            ("Bearer invalid-token", HTTPException),
        ],
    )
    async def test_dispatch(self, header, expected_exception, caplog, monkeypatch):
        """Test the dispatch method with various header scenarios.

        Args:
            header: The Authorization header to test
            expected_exception: Expected exception type if any
            caplog: Fixture to capture log messages
            monkeypatch: Fixture for mocking dependencies
        """
        # Create headers for the request
        headers = []
        if header:
            headers.append([b"authorization", header.encode()])

        # Create a proper Request object with headers in scope
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": headers,
        }
        request = Request(scope=scope, receive=lambda: b"")

        # Initialize the middleware
        middleware = AuthMiddleware()

        async def mock_call_next(req):
            return req

        if expected_exception:
            with pytest.raises(expected_exception):
                await middleware.dispatch(request, mock_call_next)
        else:
            # Test successful authentication
            response = await middleware.dispatch(request, mock_call_next)
            assert response == request

        # Verify logging
        if header == "Bearer fake-token":
            assert "Authentication successful" in caplog.text
        else:
            assert (
                "Missing Authorization header" in caplog.text
                or "Invalid Authorization header format" in caplog.text
                or "Invalid authentication token" in caplog.text
            )
