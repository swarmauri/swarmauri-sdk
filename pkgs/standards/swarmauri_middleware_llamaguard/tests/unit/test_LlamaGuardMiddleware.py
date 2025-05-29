import pytest
from fastapi import Request, JSONResponse, StreamingResponse
from llmaguard import LlamaGuard
import logging
from swarmauri_middleware_llamaguard.LlamaGuardMiddleware import LlamaGuardMiddleware

logger = logging.getLogger(__name__)

@pytest.fixture
def middleware():
    """Fixture providing a fresh instance of LlamaGuardMiddleware."""
    return LlamaGuardMiddleware()

@pytest.mark.unit
def test_llamaguard_middleware_inspects_request(middleware):
    """Test that middleware inspects request content for safety."""
    # Create a test request with a JSON body
    request = Request(
        scope={"method": "POST"},
        receive=lambda: iter([b'{"safe": "content"}'])
    )
    
    # Call the middleware dispatch
    response = middleware.dispatch(request, lambda req: JSONResponse(content={"test": "ok"}))
    
    # Assert response is not an error
    assert response.status_code != 400

@pytest.mark.unit
def test_llamaguard_middleware_blocks_unsafe_request(middleware):
    """Test that middleware blocks requests with unsafe content."""
    # Create a test request with unsafe content
    request = Request(
        scope={"method": "POST"},
        receive=lambda: iter([b'{"malicious": "content"}'])
    )
    
    # Call the middleware dispatch
    response = middleware.dispatch(request, lambda req: JSONResponse(content={"test": "ok"}))
    
    # Assert response is error
    assert response.status_code == 400
    assert response.json()["error"] == "Unsafe content detected in request"

@pytest.mark.unit
def test_llamaguard_middleware_inspects_response(middleware):
    """Test that middleware inspects response content for safety."""
    # Create a test response with safe content
    response = JSONResponse(content={"safe": "content"})
    
    # Call the middleware dispatch
    final_response = middleware.dispatch(
        Request(scope={"method": "GET"}),
        lambda req: response
    )
    
    # Assert response is not modified
    assert final_response == response

@pytest.mark.unit
def test_llamaguard_middleware_blocks_unsafe_response(middleware):
    """Test that middleware blocks responses with unsafe content."""
    # Create a test response with unsafe content
    response = JSONResponse(content={"malicious": "content"})
    
    # Call the middleware dispatch
    final_response = middleware.dispatch(
        Request(scope={"method": "GET"}),
        lambda req: response
    )
    
    # Assert response is error
    assert final_response.status_code == 400
    assert final_response.json()["error"] == "Unsafe content detected in response"

@pytest.mark.unit
def test_llamaguard_middleware_inspects_streaming_response(middleware):
    """Test that middleware inspects streaming response content."""
    async def stream_generator():
        yield b"safe content"
    
    response = StreamingResponse(stream_generator())
    
    # Call the middleware dispatch
    final_response = middleware.dispatch(
        Request(scope={"method": "GET"}),
        lambda req: response
    )
    
    # Assert response is not modified
    assert final_response == response

@pytest.mark.unit
def test_llamaguard_middleware_blocks_unsafe_streaming_response(middleware):
    """Test that middleware blocks streaming responses with unsafe content."""
    async def stream_generator():
        yield b"malicious content"
    
    response = StreamingResponse(stream_generator())
    
    # Call the middleware dispatch
    final_response = middleware.dispatch(
        Request(scope={"method": "GET"}),
        lambda req: response
    )
    
    # Assert response is error
    assert final_response.status_code == 400
    assert final_response.json()["error"] == "Unsafe streaming content detected"

@pytest.mark.unit
def test_llamaguard_middleware_error_handling(middleware, caplog):
    """Test that middleware handles exceptions properly."""
    # Create a request that will cause an error
    request = Request(
        scope={"method": "POST"},
        receive=lambda: iter([b"invalid_json"])
    )
    
    # Call the middleware dispatch with a failing call_next
    response = middleware.dispatch(
        request,
        lambda req: (1 / 0)  # Simulate an exception
    )
    
    # Assert error response
    assert response.status_code == 500
    assert response.json()["error"] == "Internal server error during content inspection"
    
    # Assert error was logged
    assert "Error in LlamaGuardMiddleware" in caplog.text