import pytest
from typing import Any, Callable
from asyncio import Semaphore
from logging import Logger, getLogger
from fastapi import Request
from swarmauri_core.ComponentBase import ComponentBase
from base.swarmauri_base.middlewares import MiddlewareBase

from swarmauri_middleware_bulkhead.BulkheadMiddleware import BulkheadMiddleware

@pytest.mark.unit
class TestBulkheadMiddleware:
    """Unit tests for BulkheadMiddleware class."""

    @pytest.fixture
    def logger_fixture(self) -> Logger:
        """Fixture to provide a logger instance."""
        return getLogger(__name__)

    @pytest.fixture
    def bulkhead_middleware(self, logger_fixture: Logger) -> BulkheadMiddleware:
        """Fixture to provide a configured BulkheadMiddleware instance."""
        return BulkheadMiddleware(max_concurrency=5, logger=logger_fixture)

    @pytest.mark.unit
    def test_init(self, logger_fixture: Logger) -> None:
        """Test the initialization of BulkheadMiddleware."""
        max_concurrency = 10
        bulkhead = BulkheadMiddleware(max_concurrency=max_concurrency, logger=logger_fixture)
        
        assert bulkhead.max_concurrency == max_concurrency
        assert isinstance(bulkhead._semaphore, Semaphore)
        assert bulkhead.logger is logger_fixture

    @pytest.mark.unit
    def test_init_defaults(self, logger_fixture: Logger) -> None:
        """Test initialization with default values."""
        bulkhead = BulkheadMiddleware(logger=logger_fixture)
        assert bulkhead.max_concurrency == 10
        assert isinstance(bulkhead._semaphore, Semaphore)

    @pytest.mark.unit
    def test_init_invalid_max_concurrency(self, logger_fixture: Logger) -> None:
        """Test initialization with invalid max_concurrency values."""
        with pytest.raises(ValueError):
            BulkheadMiddleware(max_concurrency=0, logger=logger_fixture)
        
        with pytest.raises(ValueError):
            BulkheadMiddleware(max_concurrency=-1, logger=logger_fixture)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatch(self, bulkhead_middleware: BulkheadMiddleware, logger_fixture: Logger) -> None:
        """Test the dispatch method of BulkheadMiddleware."""
        # Setup mock request and call_next
        mock_request = Request(scope={"type": "http"})
        async def mock_call_next(request: Request) -> Any:
            return {"message": "Test response"}

        # Execute the dispatch method
        response = await bulkhead_middleware.dispatch(mock_request, mock_call_next)

        # Assert the response and semaphore usage
        assert response == {"message": "Test response"}
        bulkhead_middleware._semaphore._value == 0  # type: ignore

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dispatchLoggerOutput(self, bulkhead_middleware: BulkheadMiddleware, logger_fixture: Logger) -> None:
        """Test if dispatch method logs appropriately."""
        # Setup mock request and call_next
        mock_request = Request(scope={"type": "http"})
        async def mock_call_next(request: Request) -> Any:
            return {"message": "Test response"}

        # Execute the dispatch method
        response = await bulkhead_middleware.dispatch(mock_request, mock_call_next)

        # Assert the response and logs
        assert response == {"message": "Test response"}
        # TODO: Implement proper logging checks (this is a placeholder)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_close(self, bulkhead_middleware: BulkheadMiddleware) -> None:
        """Test the close method of BulkheadMiddleware."""
        await bulkhead_middleware.close()
        # Add assertions as needed based on actual implementation

    @pytest.mark.unit
    def test_type_and_resource(self) -> None:
        """Test the type and resource properties."""
        bulkhead = BulkheadMiddleware()
        assert bulkhead.type == "BulkheadMiddleware"
        assert bulkhead.resource == "Middleware"