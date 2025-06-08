import pytest
from fastapi import Response
from swarmauri_middleware_ratelimit.RateLimitMiddleware import RateLimitMiddleware


@pytest.mark.unit
class TestRateLimitMiddleware:
    """Unit tests for RateLimitMiddleware class."""

    @pytest.fixture
    def middleware(self):
        """Fixture providing a RateLimitMiddleware instance."""
        return RateLimitMiddleware(rate_limit=100, time_window=60, use_token=False)

    def test_ubc_type(self, middleware):
        """Test that the middleware is of the correct type."""
        assert middleware.type == "RateLimitMiddleware"

    def test_ubc_resource(self, middleware):
        """Test that the middleware has the correct resource type."""
        assert middleware.resource == "Middleware"

    def test_serialization(self, middleware):
        """"""
        serialized = middleware.model_dump_json()
        assert RateLimitMiddleware.model_validate_json(serialized).id == middleware.id

    def test_init(self, middleware):
        """Test that the middleware initializes with correct attributes."""
        assert hasattr(middleware, "rate_limit")
        assert hasattr(middleware, "time_window")
        assert hasattr(middleware, "use_token")
        assert hasattr(middleware, "token_header")
        assert hasattr(middleware, "_ip_limits")
        assert middleware._ip_limits == {}

    @pytest.mark.parametrize(
        "use_token,token_header,expected_identifier",
        [(True, "X-Api-Key", "test-token"), (False, None, "192.168.1.1")],
    )
    @pytest.mark.asyncio
    async def test_get_client_identifier(
        self, use_token, token_header, expected_identifier, middleware
    ):
        """Test that client identifier is retrieved correctly."""
        # Mock request object
        request = type(
            "Request",
            (),
            {
                "headers": {token_header: expected_identifier} if use_token else {},
                "client": type("Client", (), {"host": expected_identifier}),
            },
        )()

        middleware.use_token = use_token
        middleware.token_header = token_header

        identifier = await middleware._get_client_identifier(request)
        assert identifier == expected_identifier

    @pytest.mark.asyncio
    async def test_dispatch_not_exceeded(self, middleware):  # Make async
        """Test that request is processed normally when rate limit is not exceeded."""
        # Mock request object
        request = type(
            "Request", (), {"client": type("Client", (), {"host": "192.168.1.1"})}
        )()

        # Mock call_next
        async def call_next(request):
            return "Processed request"

        response = await middleware.dispatch(request, call_next)
        assert response == "Processed request"

        # Second request within time window
        response = await middleware.dispatch(request, call_next)
        assert response == "Processed request"

    @pytest.mark.asyncio
    async def test_dispatch_exceeded(self, middleware):  # Make async
        """Test that 429 response is returned when rate limit is exceeded."""
        # Mock request object
        request = type(
            "Request", (), {"client": type("Client", (), {"host": "192.168.1.1"})}
        )()

        # Mock call_next
        async def call_next(request):
            return "Processed request"

        # Set up rate limit to 1
        middleware.rate_limit = 1

        response = await middleware.dispatch(request, call_next)
        assert response == "Processed request"

        # Second request exceeds limit
        response = await middleware.dispatch(request, call_next)
        assert isinstance(response, Response)
        assert response.status_code == 429

    @pytest.mark.asyncio  # Add asyncio marker
    async def test_dispatch_with_token(self, middleware):  # Make async
        """Test that token-based rate limiting works correctly."""
        # Enable token-based rate limiting
        middleware.use_token = True
        middleware.token_header = "X-Api-Token"

        # Mock request object with token
        request = type(
            "Request",
            (),
            {
                "headers": {"X-Api-Token": "test-token"},
                "client": type("Client", (), {"host": "192.168.1.1"}),
            },
        )()

        # Mock call_next
        async def call_next(request):
            return "Processed request"

        response = await middleware.dispatch(request, call_next)
        assert response == "Processed request"

        # Test rate limit exceeded
        middleware.rate_limit = 1
        response = await middleware.dispatch(request, call_next)
        assert isinstance(response, Response)
        assert response.status_code == 429
