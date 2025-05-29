import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from swarmauri_middleware_session.SessionMiddleware import SessionMiddleware

@pytest.mark.unit
class TestSessionMiddleware:
    """Unit tests for SessionMiddleware class."""
    
    def test_init(self):
        """Test initialization of SessionMiddleware."""
        middleware = SessionMiddleware()
        assert hasattr(middleware, "session_storage")
        assert hasattr(middleware, "session_header")
        assert hasattr(middleware, "session_cookie")
        assert hasattr(middleware, "max_age")
        
    def test_generate_session_id(self):
        """Test session ID generation."""
        middleware = SessionMiddleware()
        session_id = middleware._generate_session_id()
        assert isinstance(session_id, str)
        assert len(session_id) == 32
        
    @pytest.mark.asyncio
    async def test_dispatch_new_session(self, mocker):
        """Test dispatch with new session creation."""
        middleware = SessionMiddleware()
        request = mocker.Mock(spec=Request)
        request.headers.get.return_value = None
        
        async def call_next(request):
            return mocker.Mock(spec=Request)
            
        response = await middleware.dispatch(request, call_next)
        
        # Verify session ID was created and set in response
        assert request.state.session_id is not None
        assert response.headers.get(middleware.session_header) is not None
        assert response.headers.get(middleware.session_cookie) is not None
        
    @pytest.mark.asyncio
    async def test_dispatch_existing_session(self, mocker):
        """Test dispatch with existing session."""
        middleware = SessionMiddleware()
        session_id = "test-session-id"
        request = mocker.Mock(spec=Request)
        request.headers.get.return_value = session_id
        
        async def call_next(request):
            return mocker.Mock(spec=Request)
            
        response = await middleware.dispatch(request, call_next)
        
        # Verify existing session ID is used
        assert request.state.session_id == session_id
        assert response.headers.get(middleware.session_header) == session_id
        
    def test_logging(self, mocker):
        """Test logging within SessionMiddleware."""
        middleware = SessionMiddleware()
        logger = mocker.patch("logging.getLogger")
        
        # Test initialization logging
        middleware.__init__()
        logger.assert_called_once_with(__name__)
        
        # Test session creation logging
        session_id = middleware._generate_session_id()
        middleware.dispatch(mocker.Mock(), mocker.Mock())
        logger.return_value.info.assert_called_once_with(f"Created new session: {session_id}")

@pytest.fixture
def logger():
    import logging
    return logging.getLogger(__name__)