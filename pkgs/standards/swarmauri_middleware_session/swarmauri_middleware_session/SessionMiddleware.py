import logging
from typing import Any, Callable, Dict, Optional
from fastapi import Request
from core.middlewares import MiddlewareBase
from swarmauri_core import ComponentBase

# Configure logging
logger = logging.getLogger(__name__)

@ComponentBase.register_type(MiddlewareBase, "SessionMiddleware")
class SessionMiddleware(MiddlewareBase, ComponentBase):
    """Session middleware for maintaining session state across requests.
    
    This middleware tracks sessions using headers or cookies. It ensures that
    session state is maintained across multiple requests from the same client.
    
    Attributes:
        session_storage: Dict[str, Dict] = {}  # Storage for session data
        session_header: str = "X-Session-ID"  # Header name for session ID
        session_cookie: str = "session_id"      # Cookie name for session ID
        max_age: int = 3600                    # Default session expiration in seconds
        
    Methods:
        dispatch: Implements the core middleware dispatch logic
    """
    
    def __init__(self, *args, **kwargs):
        """Initializes the SessionMiddleware instance.
        
        Args:
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            None
        """
        super().__init__(*args, **kwargs)
        self.session_storage: Dict[str, Dict] = {}
        self.session_header: str = "X-Session-ID"
        self.session_cookie: str = "session_id"
        self.max_age: int = 3600
        
    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        """Dispatches the request to the next middleware in the chain while maintaining session state.
        
        This method processes the request to check for an existing session or create a new one.
        It ensures that session state is maintained across requests by setting appropriate
        headers or cookies.
        
        Args:
            request: The incoming request object
            call_next: A callable that invokes the next middleware in the chain
            
        Returns:
            The response object after processing the request
            
        Raises:
            None
        """
        # Check if session ID exists in request headers
        session_id: Optional[str] = request.headers.get(self.session_header)
        
        if session_id:
            # Session exists - update session storage
            if session_id not in self.session_storage:
                logger.warning(f"Session ID {session_id} exists in header but not in storage")
                # Create new session data
                self.session_storage[session_id] = {}
            else:
                logger.debug(f"Session {session_id} found in storage")
        else:
            # Create new session
            session_id = self._generate_session_id()
            logger.info(f"Created new session: {session_id}")
            self.session_storage[session_id] = {}
        
        # Add session ID to request state
        request.state.session_id = session_id
        
        # Process the request with next middleware
        response = await call_next(request)
        
        # Ensure session ID is set in response headers
        response.headers[self.session_header] = session_id
        
        # Set session cookie if not present
        if self.session_cookie not in response.headers:
            response.headers[self.session_cookie] = session_id
            response.headers["Set-Cookie"] = f"{self.session_cookie}={session_id}; Max-Age={self.max_age}"
        
        return response
        
    def _generate_session_id(self) -> str:
        """Generates a unique session ID.
        
        This method creates a new unique identifier for the session. You
        can override this method to implement custom session ID generation logic.
        
        Returns:
            A unique session ID as a string
        """
        # Import uuid here to avoid circular imports
        import uuid
        return str(uuid.uuid4())