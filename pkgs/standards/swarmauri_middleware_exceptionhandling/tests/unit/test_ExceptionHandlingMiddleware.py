import pytest
from fastapi import Response
from swarmauri_middleware_exceptionhandling.ExceptionHandlingMiddleware import (
    ExceptionHandlingMiddleware,
)


@pytest.mark.unit
class TestExceptionHandlingMiddleware:
    """Unit tests for the ExceptionHandlingMiddleware class."""

    @pytest.fixture()
    def middleware(self):
        """Fixture to provide an instance of ExceptionHandlingMiddleware."""
        return ExceptionHandlingMiddleware()

    def test_type_attribute(self, middleware):
        """Test that the type attribute is correctly set."""
        assert middleware.type == "ExceptionHandlingMiddleware"

    def test_resource_attribute(self, middleware):
        """Test that the resource attribute is correctly set."""
        assert middleware.resource == "Middleware"

    def test_serialization(self):
        """Test serialization of ExceptionHandlingMiddleware instance."""
        middleware = ExceptionHandlingMiddleware()
        serialized = middleware.model_dump_json()
        assert (
            ExceptionHandlingMiddleware.model_validate_json(serialized).id
            == middleware.id
        )

    @pytest.fixture
    def mock_request(self, mocker):
        """Fixture providing a mock Request object."""
        return mocker.Mock()

    @pytest.fixture
    def mock_call_next(self, mocker):
        """Fixture providing a mock call_next function."""
        # Fix: Make mock_call_next async
        async_mock = mocker.AsyncMock()
        return async_mock

    @pytest.mark.parametrize(
        "test_case", [(200, "Success response"), (500, "Internal Server Error")]
    )
    @pytest.mark.asyncio  # Add asyncio marker
    async def test_dispatch(self, mock_request, mock_call_next, test_case, middleware):
        """Test the dispatch method under different scenarios."""
        # Setup mock_call_next to return a response
        mock_response = Response()
        mock_response.status_code = test_case[0]
        mock_call_next.return_value = mock_response

        response = await middleware.dispatch(mock_request, mock_call_next)

        mock_call_next.assert_called_once_with(mock_request)

        assert response == mock_response

    @pytest.mark.asyncio
    async def test_dispatch_with_exception(self, mocker):
        """Test that exceptions are properly caught and handled."""
        # Create a proper mock request with headers that behave like a dict
        mock_request = mocker.Mock()
        mock_request.method = "GET"
        mock_request.url.path = "/test"
        mock_request.headers = {
            "Authorization": "Bearer token",
            "Content-Type": "application/json",
        }

        mock_call_next = mocker.AsyncMock()
        test_exception = Exception("Test exception")
        mock_call_next.side_effect = test_exception

        middleware = ExceptionHandlingMiddleware()
        response = await middleware.dispatch(mock_request, mock_call_next)

        assert response.status_code == 500

        import json

        response_data = json.loads(response.body)
        assert "error" in response_data
        assert response_data["error"]["type"] == "Unhandled Exception"
        assert response_data["error"]["message"] == "Test exception"
        assert "timestamp" in response_data["error"]

    @pytest.mark.asyncio
    async def test_call_method(self, mock_request, mocker):
        """Test the __call__ method."""
        mock_dispatch = mocker.patch.object(
            ExceptionHandlingMiddleware, "dispatch", new_callable=mocker.AsyncMock
        )

        middleware = ExceptionHandlingMiddleware()

        # Fix: Provide call_next parameter and await
        async def mock_call_next(req):
            return Response()

        await middleware(mock_request, mock_call_next)

        mock_dispatch.assert_called_once_with(mock_request, mock_call_next)
