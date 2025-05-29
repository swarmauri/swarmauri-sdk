import pytest
from fastapi import HTTPException, Request, Response
from swarmauri_middleware_time.TimerMiddleware import TimerMiddleware


@pytest.fixture
def middleware():
    """Fixture to provide a TimerMiddleware instance for testing."""
    return TimerMiddleware()


@pytest.mark.unit
def test_type(middleware):
    """Test that the type attribute is correctly set."""
    assert middleware.type == "TimerMiddleware"


@pytest.mark.unit
def test_resource(middleware):
    """Test that the resource attribute is correctly set."""
    assert middleware.resource == "Middleware"


@pytest.mark.unit
async def test_dispatch(middleware):
    """Test the dispatch method functionality."""

    class MockRequest:
        method = "GET"
        url = type("MockURL", (), {"path": "/"})

    request = MockRequest()

    class MockResponse:
        def __init__(self):
            self.headers = {}

    response = MockResponse()

    # Create a mock call_next coroutine
    async def mock_call_next(request: Request) -> Response:
        return response

    # Test the dispatch method
    result = await middleware.dispatch(request, mock_call_next)

    # Fix: Assert that the X-Request-Duration header was added
    assert "X-Request-Duration" in result.headers
    assert "X-Request-Start-Time" in result.headers

    # Verify the duration is a valid float string
    duration = float(result.headers["X-Request-Duration"])
    assert duration >= 0


@pytest.mark.unit
async def test_error_handling(middleware):
    """Test error handling in the dispatch method."""

    # Create a mock request object
    class MockRequest:
        method = "GET"
        url = type("MockURL", (), {"path": "/"})

    request = MockRequest()

    # Create a mock call_next that raises an exception
    async def mock_call_next(request: Request) -> Response:
        raise Exception("Test error")

    # Fix: Test if the middleware correctly raises HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await middleware.dispatch(request, mock_call_next)

    # Fix: Check the exception detail, not the string representation
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Test error"


@pytest.mark.unit
async def test_timing_accuracy(middleware):
    """Test that timing measurements are reasonably accurate."""
    import asyncio

    class MockRequest:
        method = "POST"
        url = type("MockURL", (), {"path": "/test"})

    request = MockRequest()

    class MockResponse:
        def __init__(self):
            self.headers = {}

    response = MockResponse()

    # Create a call_next that takes some time
    async def slow_call_next(request: Request) -> Response:
        await asyncio.sleep(0.1)  # Sleep for 100ms
        return response

    result = await middleware.dispatch(request, slow_call_next)

    # Verify timing is reasonable (should be around 0.1 seconds)
    duration = float(result.headers["X-Request-Duration"])
    assert 0.09 <= duration <= 0.2  # Allow some tolerance


@pytest.mark.unit
async def test_multiple_requests(middleware):
    """Test that multiple requests are timed independently."""

    class MockRequest:
        method = "GET"
        url = type("MockURL", (), {"path": "/multi"})

    class MockResponse:
        def __init__(self):
            self.headers = {}

    async def mock_call_next(request: Request) -> Response:
        return MockResponse()

    # Process multiple requests
    durations = []
    for _ in range(3):
        request = MockRequest()
        result = await middleware.dispatch(request, mock_call_next)
        durations.append(float(result.headers["X-Request-Duration"]))

    # All durations should be valid and potentially different
    assert all(d >= 0 for d in durations)
    assert len(durations) == 3


@pytest.mark.unit
async def test_response_without_headers(middleware):
    """Test handling of responses that don't have headers attribute."""

    class MockRequest:
        method = "GET"
        url = type("MockURL", (), {"path": "/"})

    request = MockRequest()

    # Response without headers attribute
    class MockResponseNoHeaders:
        pass

    response = MockResponseNoHeaders()

    async def mock_call_next(request: Request) -> Response:
        return response

    # Should not raise an error even if response has no headers
    result = await middleware.dispatch(request, mock_call_next)
    assert result == response  # Should return the original response
