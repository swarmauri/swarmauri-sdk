import logging
import os

import pytest
from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse
from swarmauri_middleware_llamaguard.LlamaGuardMiddleware import LlamaGuardMiddleware

from swarmauri_standard.llms.GroqModel import GroqModel
from swarmauri_standard.messages.AgentMessage import AgentMessage

load_dotenv()

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def middleware():
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        logger.info("Using GroqModel with API key for LlamaGuardMiddleware")
        llm = GroqModel(api_key=api_key, name="llama-guard-3-8b")
    else:
        logger.info("No GROQ_API_KEY found, using a fake GroqModel for testing")

        class FakeGroqModel:
            def predict(self, conversation, *args, **kwargs):
                text = conversation.get_last().content
                label = "unsafe" if "malicious" in text else "safe"
                conversation.add_message(AgentMessage(content=label))

        llm = FakeGroqModel()

    return LlamaGuardMiddleware(llm=llm)


@pytest.mark.unit
@pytest.mark.asyncio  # Add asyncio marker
async def test_llamaguard_middleware_inspects_request(middleware):
    """Test that middleware inspects request content for safety."""

    async def receive():
        return {
            "type": "http.request",
            "body": b'{"safe": "content"}',
            "more_body": False,
        }

    scope = {"type": "http", "method": "POST", "path": "/", "headers": []}
    request = Request(scope=scope, receive=receive)

    async def mock_call_next(req):
        return JSONResponse(content={"test": "ok"})

    # Await the async call
    response = await middleware.dispatch(request, mock_call_next)

    # Assert response is not an error
    assert response.status_code != 400


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llamaguard_middleware_blocks_unsafe_request(middleware):
    """Test that middleware blocks requests with unsafe content."""

    async def receive():
        return {
            "type": "http.request",
            "body": b'{"malicious": "content"}',
            "more_body": False,
        }

    scope = {"type": "http", "method": "POST", "path": "/", "headers": []}
    request = Request(scope=scope, receive=receive)

    async def mock_call_next(req):
        return JSONResponse(content={"test": "ok"})

    # Await the async call
    response = await middleware.dispatch(request, mock_call_next)

    # Assert response is error
    assert response.status_code == 400

    import json

    response_data = json.loads(response.body.decode())
    assert response_data["error"] == "Unsafe content detected in request"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llamaguard_middleware_inspects_response(middleware):
    """Test that middleware inspects response content for safety."""

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
    request = Request(scope=scope, receive=receive)

    # Create a test response with safe content
    response = JSONResponse(content={"safe": "content"})

    async def mock_call_next(req):
        return response

    # Await the async call
    final_response = await middleware.dispatch(request, mock_call_next)

    # Assert response is not modified
    assert final_response == response


@pytest.mark.unit
@pytest.mark.asyncio  # Add asyncio marker
async def test_llamaguard_middleware_blocks_unsafe_response(middleware):
    """Test that middleware blocks responses with unsafe content."""

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
    request = Request(scope=scope, receive=receive)

    # Create a test response with unsafe content
    response = JSONResponse(content={"malicious": "content"})

    async def mock_call_next(req):
        return response

    # Await the async call
    final_response = await middleware.dispatch(request, mock_call_next)

    # Assert response is error
    assert final_response.status_code == 400

    import json

    response_data = json.loads(final_response.body.decode())
    assert response_data["error"] == "Unsafe content detected in response"


@pytest.mark.unit
@pytest.mark.asyncio  # Add asyncio marker
async def test_llamaguard_middleware_inspects_streaming_response(middleware):
    """Test that middleware inspects streaming response content."""

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
    request = Request(scope=scope, receive=receive)

    async def stream_generator():
        yield b"safe content"

    response = StreamingResponse(stream_generator())

    async def mock_call_next(req):
        return response

    # Await the async call
    final_response = await middleware.dispatch(request, mock_call_next)

    # Assert response is not modified
    assert final_response == response


@pytest.mark.unit
@pytest.mark.asyncio  # Add asyncio marker
async def test_llamaguard_middleware_blocks_unsafe_streaming_response(middleware):
    """Test that middleware blocks streaming responses with unsafe content."""

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
    request = Request(scope=scope, receive=receive)

    async def stream_generator():
        yield b"malicious content"

    response = StreamingResponse(stream_generator())

    async def mock_call_next(req):
        return response

    # Await the async call
    final_response = await middleware.dispatch(request, mock_call_next)

    # Assert response is error
    assert final_response.status_code == 400

    import json

    response_data = json.loads(final_response.body.decode())
    assert response_data["error"] == "Unsafe streaming content detected"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llamaguard_middleware_error_handling(middleware, caplog):
    """Test that middleware handles exceptions properly."""

    async def receive():
        return {"type": "http.request", "body": b"invalid_json", "more_body": False}

    scope = {"type": "http", "method": "POST", "path": "/", "headers": []}
    request = Request(scope=scope, receive=receive)

    async def mock_call_next_with_error(req):
        raise Exception("Test exception")

    # Await the async call
    response = await middleware.dispatch(request, mock_call_next_with_error)

    # Assert response is error
    assert response.status_code == 500

    import json

    response_data = json.loads(response.body.decode())
    assert "Internal server error" in response_data["error"]
    assert "Error in LlamaGuardMiddleware" in caplog.text
