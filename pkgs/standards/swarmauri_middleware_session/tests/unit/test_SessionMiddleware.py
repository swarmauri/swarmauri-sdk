from unittest.mock import MagicMock, Mock

import pytest
from fastapi import Request, Response
from swarmauri_middleware_session.SessionMiddleware import SessionMiddleware


@pytest.mark.unit
class TestSessionMiddleware:
    """Unit tests for SessionMiddleware class."""

    @pytest.fixture()
    def middleware(self):
        """Fixture to provide a configured SessionMiddleware instance."""
        return SessionMiddleware(
            session_storage={},
            session_header="X-Session-ID",
            session_cookie="session_id",
            max_age=3600,
        )

    def test_generate_session_id(self, middleware):
        """Test session ID generation."""
        session_id = middleware._generate_session_id()
        assert isinstance(session_id, str)
        assert len(session_id) == 36
        import uuid

        uuid.UUID(session_id)

    @pytest.mark.asyncio
    async def test_dispatch_new_session(self, middleware):
        """Test dispatch with new session creation."""

        mock_headers = MagicMock()
        mock_headers.get = Mock(return_value=None)  # No existing session
        mock_headers.__contains__ = Mock(return_value=False)
        mock_headers.__getitem__ = Mock(side_effect=KeyError())

        request = Mock(spec=Request)
        request.headers = mock_headers
        request.state = Mock()

        response = Mock(spec=Response)
        response.headers = {}

        async def call_next(req):
            return response

        result = await middleware.dispatch(request, call_next)

        # Verify session ID was created and set
        assert hasattr(request.state, "session_id")
        assert request.state.session_id is not None
        assert middleware.session_header in result.headers
        assert result.headers[middleware.session_header] is not None

    @pytest.mark.asyncio
    async def test_dispatch_existing_session(self, middleware):
        """Test dispatch with existing session."""
        session_id = "test-session-id"

        # Pre-populate session storage
        middleware.session_storage[session_id] = {}

        mock_headers = MagicMock()
        mock_headers.get = Mock(return_value=session_id)
        mock_headers.__contains__ = Mock(return_value=True)
        mock_headers.__getitem__ = Mock(return_value=session_id)

        request = Mock(spec=Request)
        request.headers = mock_headers
        request.state = Mock()

        response = Mock(spec=Response)
        response.headers = {}

        async def call_next(req):
            return response

        result = await middleware.dispatch(request, call_next)

        # Verify existing session ID is used
        assert request.state.session_id == session_id
        assert result.headers[middleware.session_header] == session_id

    @pytest.mark.asyncio
    async def test_session_storage_management(self, middleware):
        """Test session storage operations."""

        # Test that session storage starts empty
        assert len(middleware.session_storage) == 0

        mock_headers = MagicMock()
        mock_headers.get = Mock(return_value=None)  # No existing session
        mock_headers.__contains__ = Mock(return_value=False)

        request = Mock(spec=Request)
        request.headers = mock_headers
        request.state = Mock()

        response = Mock(spec=Response)
        response.headers = {}

        async def call_next(req):
            return response

        await middleware.dispatch(request, call_next)

        # Verify session was created in storage
        assert len(middleware.session_storage) == 1
        session_id = request.state.session_id
        assert session_id in middleware.session_storage

    def test_custom_configuration(self):
        """Test middleware with custom configuration."""
        custom_storage = {"existing-session": {"data": "value"}}
        middleware = SessionMiddleware(
            session_storage=custom_storage,
            session_header="Custom-Session",
            session_cookie="custom_session",
            max_age=7200,
        )

        assert middleware.session_storage == custom_storage
        assert middleware.session_header == "Custom-Session"
        assert middleware.session_cookie == "custom_session"
        assert middleware.max_age == 7200
