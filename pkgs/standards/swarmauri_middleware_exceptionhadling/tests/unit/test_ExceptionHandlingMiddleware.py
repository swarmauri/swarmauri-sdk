import pytest
from datetime import datetime
from swarmauri_middleware_exceptionhadling.ExceptionHandlingMiddleware import ExceptionHandlingMiddleware
import logging

@pytest.mark.unit
class TestExceptionHandlingMiddleware:
    """Unit tests for the ExceptionHandlingMiddleware class."""
    
    def test_type_attribute(self):
        """Test that the type attribute is correctly set."""
        assert ExceptionHandlingMiddleware.type == "ExceptionHandlingMiddleware"
        
    def test_resource_attribute(self):
        """Test that the resource attribute is correctly set."""
        assert ExceptionHandlingMiddleware.resource == "middleware"
        
    def test_initialization(self):
        """Test that the middleware initializes correctly."""
        middleware = ExceptionHandlingMiddleware()
        assert isinstance(middleware, MiddlewareBase)
        assert middleware.type == "ExceptionHandlingMiddleware"
        assert middleware.resource == "middleware"
        
    @pytest.fixture
    def mock_request(self, mocker):
        """Fixture providing a mock Request object."""
        return mocker.Mock()
        
    @pytest.fixture
    def mock_call_next(self, mocker):
        """Fixture providing a mock call_next function."""
        return mocker.Mock()
        
    @pytest.fixture
    def mock_logger(self, mocker):
        """Fixture providing a mock logger to test logging functionality."""
        mocker.patch('logging.getLogger')
        return mocker.patch('swarmauri_middleware_exceptionhadling.ExceptionHandlingMiddleware.logger')
        
    @pytest.mark.parametrize("test_case", [
        (200, "Success response"),
        (500, "Internal Server Error")
    ])
    def test_dispatch(self, mock_request, mock_call_next, mock_logger, test_case):
        """Test the dispatch method under different scenarios.
        
        Args:
            mock_request: Mocked Request object
            mock_call_next: Mocked call_next function
            mock_logger: Mocked logger instance
            test_case: Tuple containing expected status code and response phrase
        """
        # Setup mock_call_next to return a response
        mock_response = Response()
        mock_response.status_code = test_case[0]
        mock_call_next.return_value = mock_response
        
        middleware = ExceptionHandlingMiddleware()
        response = middleware.dispatch(mock_request, mock_call_next)
        
        # Verify call_next was called with the request
        mock_call_next.assert_called_once_with(mock_request)
        
        # Verify the response matches expectations
        assert response == mock_response
        
        # Verify logging occurs only when an error occurs
        if test_case[0] == 500:
            mock_logger.error.assert_called_once()
            
    def test_dispatch_with_exception(self, mock_request, mock_call_next, mock_logger):
        """Test that exceptions are properly caught and handled."""
        # Setup mock_call_next to raise an exception
        test_exception = Exception("Test exception")
        mock_call_next.side_effect = test_exception
        
        middleware = ExceptionHandlingMiddleware()
        response = middleware.dispatch(mock_request, mock_call_next)
        
        # Verify that the response is an error response
        assert response.status_code == 500
        assert isinstance(response.content, str)
        
        # Verify logging occurred with the exception
        mock_logger.error.assert_called_once()
        assert "Unhandled exception occurred while processing request" in mock_logger.error.call_args[0][0]
        
    def test_call_method(self, mock_request, mock_logger, mocker):
        """Test the __call__ method."""
        # Mock the dispatch method
        mock_dispatch = mocker.patch.object(ExceptionHandlingMiddleware, 'dispatch')
        
        middleware = ExceptionHandlingMiddleware()
        middleware(mock_request)
        
        # Verify that dispatch was called with the request
        mock_dispatch.assert_called_once_with(mock_request, mocker.ANY)
        
    def test_logging_setup(self, mock_logger):
        """Test that the logger is properly configured."""
        assert isinstance(mock_logger, logging.Logger)
        assert mock_logger.name == __name__