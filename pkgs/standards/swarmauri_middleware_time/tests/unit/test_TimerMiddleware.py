import pytest
import asyncio
from typing import Any
from fastapi import Request, Response, HTTPException
import logging

from swarmauri_middleware_time.TimerMiddleware import TimerMiddleware

@pytest.mark.unit
def test_type():
    """Test that the type attribute is correctly set."""
    assert TimerMiddleware.type == "TimerMiddleware"

@pytest.fixture
def logger_fixture():
    """Fixture to provide a logger instance for testing."""
    logger = logging.getLogger("test_timer_middleware")
    logger.setLevel(logging.DEBUG)
    return logger

@pytest.mark.unit
async def test_dispatch(logger_fixture):
    """Test the dispatch method functionality."""
    timer_middleware = TimerMiddleware()
    
    # Create a mock request object
    class MockRequest:
        method = "GET"
        url = type("MockURL", (), {"path": "/"})
        
    request = MockRequest()
    
    # Create a mock response object
    class MockResponse:
        headers = {}
    
    response = MockResponse()
    
    # Create a mock call_next coroutine
    async def mock_call_next(request: Request) -> Response:
        return response
    
    # Test the dispatch method
    await timer_middleware.dispatch(request, mock_call_next)
    
    # Assert that the X-Request-Duration header was added
    assert "X-Request-Duration" in response.headers
    
    # Check logger output
    logger_fixture.handlers.clear()
    logger_fixture.setLevel(logging.DEBUG)
    await timer_middleware.dispatch(request, mock_call_next)
    
    # Verify that the start and end logs were captured
    assert any("Request GET / started at" in record.msg for record in logger_fixture.records)
    assert any("Request GET / completed in" in record.msg for record in logger_fixture.records)

@pytest.mark.unit
async def test_error_handling():
    """Test error handling in the dispatch method."""
    timer_middleware = TimerMiddleware()
    
    # Create a mock request object
    class MockRequest:
        method = "GET"
        url = type("MockURL", (), {"path": "/"})
        
    request = MockRequest()
    
    # Create a mock call_next that raises an exception
    async def mock_call_next(request: Request) -> Response:
        raise Exception("Test error")
    
    # Test if the middleware correctly raises HTTPException
    try:
        await timer_middleware.dispatch(request, mock_call_next)
    except HTTPException as e:
        assert str(e) == "Test error"
    else:
        assert False, "HTTPException was not raised"