import logging

import pytest
from fastapi import HTTPException, Request
from swarmauri_middleware_circuitbreaker.CircuitBreakerMiddleware import (
    CircuitBreakerMiddleware,
)


@pytest.mark.unit
class TestCircuitBreakerMiddleware:
    """Unit tests for CircuitBreakerMiddleware class."""

    @pytest.fixture
    def middleware(self):
        """Fixture to create a CircuitBreakerMiddleware instance with default parameters."""
        return CircuitBreakerMiddleware()

    @pytest.fixture
    def successful_call_next(self, mocker):
        """Fixture simulating a successful call_next function."""

        async def mock_call_next(request):
            return {"status": "success"}

        return mocker.AsyncMock(side_effect=mock_call_next)

    @pytest.fixture
    def failing_call_next(self, mocker):
        """Fixture simulating a failing call_next function."""

        async def mock_call_next(request):
            raise HTTPException(status_code=500, detail="Service failed")

        return mocker.AsyncMock(side_effect=mock_call_next)

    def test_init(self, middleware):
        """Test CircuitBreakerMiddleware initialization."""
        assert hasattr(middleware, "circuit_breaker")
        assert hasattr(middleware, "fail_max")
        assert hasattr(middleware, "reset_timeout")
        assert hasattr(middleware, "half_open_wait_time")

    async def test_dispatch_success(self, middleware, successful_call_next):
        """Test successful request dispatch."""
        request = Request(scope={"type": "http"}, receive=lambda: b"")
        response = await middleware.dispatch(request, successful_call_next)
        assert response == {"status": "success"}

    async def test_dispatch_failure(self, middleware, failing_call_next):
        """Test failed request dispatch with circuit breaking."""
        request = Request(scope={"type": "http"}, receive=lambda: b"")

        # First 5 failures should be allowed
        for _ in range(5):
            with pytest.raises(HTTPException) as exc_info:
                await middleware.dispatch(request, failing_call_next)

        # 6th failure should trigger circuit opening
        with pytest.raises(HTTPException) as exc_info:
            await middleware.dispatch(request, failing_call_next)
            assert exc_info.value.status_code == 429

    async def test_circuit_state_changes(
        self, middleware, caplog, failing_call_next, successful_call_next
    ):
        """Test circuit state changes and logging."""
        caplog.set_level(logging.INFO)

        request = Request(scope={"type": "http"}, receive=lambda: b"")

        # Simulate failures to open circuit
        for _ in range(6):
            with pytest.raises(HTTPException):
                await middleware.dispatch(request, failing_call_next)

        # Verify circuit opened
        assert "Circuit opened: Excessive failures detected" in caplog.text

        # Simulate successful request to close circuit
        response = await middleware.dispatch(request, successful_call_next)
        assert response == {"status": "success"}
        assert "Circuit closed: Service is healthy again" in caplog.text

    async def test_circuit_recovery(
        self, middleware, failing_call_next, successful_call_next
    ):
        """Test circuit recovery after failures."""
        request = Request(scope={"type": "http"}, receive=lambda: b"")

        # Simulate 5 failures
        for _ in range(5):
            with pytest.raises(HTTPException):
                await middleware.dispatch(request, failing_call_next)

        # Simulate successful request
        response = await middleware.dispatch(request, successful_call_next)
        assert response == {"status": "success"}

        # Verify circuit is closed
        assert not middleware.circuit_breaker.open
