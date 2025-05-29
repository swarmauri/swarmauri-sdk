"""Unit tests for GzipCompressionMiddleware class."""
import pytest
from fastapi import Request, Response
from swarmauri_middleware_gzipcompression.GzipCompressionMiddleware import GzipCompressionMiddleware

@pytest.mark.unit
class TestGzipCompressionMiddleware:
    """Unit tests for GzipCompressionMiddleware class."""
    
    @pytest.mark.unit
    def test_type(self):
        """Test that type returns 'GzipCompressionMiddleware'."""
        assert GzipCompressionMiddleware.type == "GzipCompressionMiddleware"

    @pytest.mark.unit
    async def test_dispatch_with_gzip_supported(
        self, mock_request: Request, mock_response: Response
    ):
        """Test dispatch when client supports gzip encoding."""
        # Setup mock request and response
        mock_request.headers["Accept-Encoding"] = "gzip"
        mock_response.headers["Content-Type"] = "application/json"
        
        # Process the request
        middleware = GzipCompressionMiddleware()
        response = await middleware.dispatch(mock_request, lambda req: mock_response)
        
        # Verify response is compressed
        assert "gzip" in response.headers.get("Content-Encoding", "")
        assert isinstance(response, Response)

    @pytest.mark.unit
    async def test_dispatch_without_gzip_support(
        self, mock_request: Request, mock_response: Response
    ):
        """Test dispatch when client does not support gzip encoding."""
        # Setup mock request and response
        mock_request.headers["Accept-Encoding"] = "deflate"
        mock_response.headers["Content-Type"] = "application/json"
        
        # Process the request
        middleware = GzipCompressionMiddleware()
        response = await middleware.dispatch(mock_request, lambda req: mock_response)
        
        # Verify response is not compressed
        assert "gzip" not in response.headers.get("Content-Encoding", "")
        assert isinstance(response, Response)

    @pytest.mark.unit
    async def test_dispatch_with_non_compressible_content_type(
        self, mock_request: Request, mock_response: Response
    ):
        """Test dispatch with non-compressible content type."""
        # Setup mock request and response
        mock_request.headers["Accept-Encoding"] = "gzip"
        mock_response.headers["Content-Type"] = "image/png"
        
        # Process the request
        middleware = GzipCompressionMiddleware()
        response = await middleware.dispatch(mock_request, lambda req: mock_response)
        
        # Verify response is not compressed
        assert "gzip" not in response.headers.get("Content-Encoding", "")
        assert isinstance(response, Response)

    @pytest.mark.unit
    async def test_dispatch_with_empty_response(
        self, mock_request: Request, mock_response: Response
    ):
        """Test dispatch with an empty response body."""
        # Setup mock request and response
        mock_request.headers["Accept-Encoding"] = "gzip"
        mock_response.headers["Content-Type"] = "application/json"
        mock_response.body = b""
        
        # Process the request
        middleware = GzipCompressionMiddleware()
        response = await middleware.dispatch(mock_request, lambda req: mock_response)
        
        # Verify response is handled correctly
        assert isinstance(response, Response)
        assert response.body == b""

@pytest.fixture
def mock_request():
    """Fixture providing a mock Request object."""
    request = Request(scope={"type": "http"}, receive=lambda: b"")
    request.headers = {}
    return request

@pytest.fixture
def mock_response():
    """Fixture providing a mock Response object."""
    response = Response(content=b"test content", status_code=200)
    response.headers = {}
    return response

@pytest.mark.unit
@pytest.mark.parametrize(
    "test_case,expected_compressed",
    [
        ("gzip_supported", True),
        ("gzip_not_supported", False),
        ("non_compressible_type", False),
    ],
)
async def test_dispatch_compression_logic(
    test_case, expected_compressed, mock_request, mock_response
):
    """Test the compression logic based on different scenarios."""
    # Setup request headers based on test case
    if test_case == "gzip_supported":
        mock_request.headers["Accept-Encoding"] = "gzip"
        mock_response.headers["Content-Type"] = "application/json"
    elif test_case == "gzip_not_supported":
        mock_request.headers["Accept-Encoding"] = "deflate"
        mock_response.headers["Content-Type"] = "application/json"
    else:  # non_compressible_type
        mock_request.headers["Accept-Encoding"] = "gzip"
        mock_response.headers["Content-Type"] = "image/png"
    
    # Initialize middleware and process request
    middleware = GzipCompressionMiddleware()
    response = await middleware.dispatch(mock_request, lambda req: mock_response)
    
    # Verify if response was compressed
    content_encoding = response.headers.get("Content-Encoding", "")
    assert ("gzip" in content_encoding) == expected_compressed
    assert isinstance(response, Response)

@pytest.mark.unit
def test_logging(caplog, mock_request, mock_response):
    """Test logging statements in GzipCompressionMiddleware."""
    caplog.set_level(logging.DEBUG)
    
    # Initialize middleware and process request
    middleware = GzipCompressionMiddleware()
    response = await middleware.dispatch(
        mock_request, lambda req: mock_response
    )
    
    # Verify logging statements
    assert "Successfully compressed response using gzip" in caplog.text