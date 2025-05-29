import pytest
from unittest.mock import Mock, patch
from fastapi import Request
from swarmauri_middleware_logging.LoggingMiddleware import LoggingMiddleware

@pytest.fixture
def logging_middleware():
    """Fixture to provide a LoggingMiddleware instance for testing."""
    return LoggingMiddleware()

@pytest.mark.unit
def test_logging_middleware_initialization(logging_middleware):
    """Test the initialization of LoggingMiddleware."""
    assert hasattr(logging_middleware, 'logger')
    assert logging_middleware.resource == "middleware"

@pytest.mark.unit
@patch('logging.getLogger')
def test_logging_middleware_logger(mock_get_logger, logging_middleware):
    """Test that the logger is properly set up."""
    assert logging_middleware.logger == mock_get_logger.return_value

@pytest.mark.unit
@patch('logging.Logger.info')
def test_dispatch_logs_request_info(mock_info, logging_middleware):
    """Test that dispatch logs request information."""
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.url.path = "/test"
    mock_request.headers = {"Content-Type": "application/json"}
    
    mock_call_next = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_call_next.return_value = mock_response
    
    logging_middleware.dispatch(mock_request, mock_call_next)
    
    assert mock_info.call_args_list[0][0][0] == f"Incoming request: GET /test"
    assert mock_info.call_args_list[1][0][0] == "Request headers: {'Content-Type': 'application/json'}"

@pytest.mark.unit
@patch('logging.Logger.info')
def test_dispatch_logs_response_info(mock_info, logging_middleware):
    """Test that dispatch logs response information."""
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.url.path = "/test"
    
    mock_call_next = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_call_next.return_value = mock_response
    
    logging_middleware.dispatch(mock_request, mock_call_next)
    
    assert mock_info.call_args_list[-2][0][0] == "Response status code: 200"
    assert "Request completed in:" in mock_info.call_args_list[-1][0][0]

@pytest.mark.unit
@pytest.mark.parametrize("request_body,expected_body", [
    ({"test": "body"}, "Request body: {'test': 'body'}"),
    ("", "Request body: "),
    (None, "Request body: None")
])
@patch('logging.Logger.info')
def test_dispatch_logs_request_body(mock_info, logging_middleware, request_body, expected_body):
    """Test that dispatch logs request body information."""
    mock_request = Mock()
    mock_request.json = Mock(return_value=request_body)
    
    mock_call_next = Mock()
    
    logging_middleware.dispatch(mock_request, mock_call_next)
    
    if request_body:
        mock_info.assert_called_with(expected_body)
    else:
        mock_info.assert_called_with("Request body: ")

@pytest.mark.unit
@patch('logging.Logger.warning')
def test_dispatch_logs_error_parsing_request_body(mock_warning, logging_middleware):
    """Test that dispatch logs warning when parsing request body fails."""
    mock_request = Mock()
    mock_request.json = Mock(side_effect=Exception("Test error"))
    
    mock_call_next = Mock()
    
    logging_middleware.dispatch(mock_request, mock_call_next)
    
    mock_warning.assert_called_with("Error parsing request body: Test error")