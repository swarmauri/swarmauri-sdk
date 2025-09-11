from unittest.mock import AsyncMock, Mock, patch

import pytest
from swarmauri_middleware_logging.LoggingMiddleware import LoggingMiddleware


@pytest.fixture
def logging_middleware():
    """Fixture to provide a LoggingMiddleware instance for testing."""
    return LoggingMiddleware()


@pytest.mark.unit
def test_logging_middleware_initialization(logging_middleware):
    """Test the initialization of LoggingMiddleware."""
    assert hasattr(logging_middleware, "logger")
    assert logging_middleware.type == "LoggingMiddleware"
    assert logging_middleware.resource == "Middleware"


@pytest.mark.unit
def test_logging_middleware_logger(logging_middleware):
    """Test that the logger is properly set up."""
    assert logging_middleware.logger is not None
    assert hasattr(logging_middleware.logger, "info")
    assert hasattr(logging_middleware.logger, "warning")


@pytest.mark.unit
@pytest.mark.asyncio  # Add asyncio marker
@patch("swarmauri_middleware_logging.LoggingMiddleware.logger.info")
async def test_dispatch_logs_request_info(mock_info, logging_middleware):
    """Test that dispatch logs request information."""
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.url.path = "/test"
    mock_request.headers = {"Content-Type": "application/json"}
    mock_request.json = AsyncMock(return_value={"test": "data"})

    mock_call_next = AsyncMock()  # Fix: Make call_next async
    mock_response = Mock()
    mock_response.status_code = 200
    mock_call_next.return_value = mock_response

    await logging_middleware.dispatch(mock_request, mock_call_next)

    # Verify the logging calls
    assert mock_info.call_count >= 2
    assert any(
        "Incoming request: GET /test" in str(call) for call in mock_info.call_args_list
    )
    assert any("Request headers:" in str(call) for call in mock_info.call_args_list)


@pytest.mark.unit
@pytest.mark.asyncio
@patch("swarmauri_middleware_logging.LoggingMiddleware.logger.info")
async def test_dispatch_logs_response_info(mock_info, logging_middleware):
    """Test that dispatch logs response information."""
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.url.path = "/test"
    mock_request.headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer token",
    }
    mock_request.json = AsyncMock(return_value={})

    mock_call_next = AsyncMock()  # Fix: Make call_next async
    mock_response = Mock()
    mock_response.status_code = 200
    mock_call_next.return_value = mock_response

    await logging_middleware.dispatch(mock_request, mock_call_next)

    # Verify response logging
    assert mock_info.call_count >= 3
    assert any(
        "Response status code: 200" in str(call) for call in mock_info.call_args_list
    )
    assert any(
        "Request completed in:" in str(call) for call in mock_info.call_args_list
    )


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_body,expected_body",
    [
        ({"test": "body"}, "Request body: {'test': 'body'}"),
        ("", "Request body: "),
        (None, "Request body: None"),
    ],
)
@patch("swarmauri_middleware_logging.LoggingMiddleware.logger.info")
async def test_dispatch_logs_request_body(
    mock_info, logging_middleware, request_body, expected_body
):
    """Test that dispatch logs request body information."""
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.url.path = "/test"
    mock_request.headers = {"Content-Type": "application/json"}
    mock_request.json = AsyncMock(return_value=request_body)

    mock_call_next = AsyncMock()
    mock_call_next.return_value = Mock(status_code=200)

    await logging_middleware.dispatch(mock_request, mock_call_next)

    # Verify request body logging
    if request_body:
        assert any(expected_body in str(call) for call in mock_info.call_args_list)
    else:
        assert any("Request body:" in str(call) for call in mock_info.call_args_list)


@pytest.mark.unit
@pytest.mark.asyncio  # Add asyncio marker
@patch("swarmauri_middleware_logging.LoggingMiddleware.logger.warning")
async def test_dispatch_logs_error_parsing_request_body(
    mock_warning, logging_middleware
):
    """Test that dispatch logs warning when parsing request body fails."""
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.url.path = "/test"
    mock_request.headers = {"Content-Type": "application/json"}
    mock_request.json = AsyncMock(side_effect=Exception("Test error"))

    mock_call_next = AsyncMock()
    mock_call_next.return_value = Mock(status_code=200)
    await logging_middleware.dispatch(mock_request, mock_call_next)

    # Verify warning was logged
    mock_warning.assert_called_with("Error parsing request body: Test error")
