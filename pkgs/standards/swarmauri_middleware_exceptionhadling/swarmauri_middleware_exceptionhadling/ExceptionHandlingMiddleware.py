from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Callable, Tuple
import logging
from ..base import MiddlewareBase
from core.middlewares.IMiddleware import IMiddleware

logger = logging.getLogger(__name__)

class ExceptionHandlingMiddleware(MiddlewareBase, IMiddleware):
    """Middleware for handling exceptions and errors across the application.
    
    This middleware captures unhandled exceptions and returns formatted error
    responses to the client. It ensures that all exceptions are properly logged
    and consistent error responses are returned.
    
    Attributes:
        type: Literal["ExceptionHandlingMiddleware"] = "ExceptionHandlingMiddleware"
        resource: Optional[str] = "middleware"
    """
    
    type: Literal["ExceptionHandlingMiddleware"] = "ExceptionHandlingMiddleware"
    resource: Optional[str] = "middleware"
    
    def __init__(self):
        """Initializes the ExceptionHandlingMiddleware instance."""
        super().__init__()
        
    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        """Dispatches the request to the next middleware in the chain while handling exceptions.
        
        This method wraps the call_next function in a try-except block to catch any
        exceptions that occur during request processing. When an exception is caught,
        it is logged, and a formatted error response is returned to the client.
        
        Args:
            request: The incoming request object to be processed.
            call_next: A callable that invokes the next middleware in the chain.
            
        Returns:
            The response object after all middlewares have processed the request,
            or an error response if an exception occurred.
            
        Raises:
            Exception: If any error occurs during request processing.
        """
        try:
            # Call the next middleware in the chain
            return await call_next(request)
            
        except Exception as e:
            # Log the exception with request details
            logger.error(
                "Unhandled exception occurred while processing request",
                exc_info=True,
                extra={
                    "request_method": request.method,
                    "request_path": request.url.path,
                    "request_headers": dict(request.headers)
                }
            )
            
            # Prepare the error response
            error_response = {
                "error": {
                    "type": "Unhandled Exception",
                    "message": str(e),
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
            }
            
            # Return a JSON response with 500 status code
            return Response(
                content=error_response,
                status_code=500,
                media_type="application/json"
            )

    async def __call__(self, request: Request) -> Response:
        """Makes the middleware callable.
        
        This method allows the middleware to be invoked directly as part of
        the request-response cycle.
        
        Args:
            request: The incoming request object.
            
        Returns:
            The response object after processing.
        """
        return await self.dispatch(request)

ComponentBase.register_type(MiddlewareBase, "ExceptionHandlingMiddleware")(
    ExceptionHandlingMiddleware
)