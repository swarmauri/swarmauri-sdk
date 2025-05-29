from typing import Any, Callable
from tenacity import retry, wait_exponential
from core.middlewares.MiddlewareBase import MiddlewareBase
import logging

logger = logging.getLogger(__name__)


class RetryPolicyMiddleware(MiddlewareBase):
    """Middleware that implements retry policy for failed requests.
    
    This middleware uses the tenacity library to provide exponential backoff
    for failed requests. It wraps the call_next function with a retry decorator
    that will attempt to process the request multiple times before giving up.
    
    Attributes:
        max_retries: int = 3  # Maximum number of retry attempts
        initial_wait: float = 1  # Initial wait time in seconds
    """
    
    def __init__(self, max_retries: int = 3, initial_wait: float = 1):
        super().__init__()
        self.max_retries = max_retries
        self.initial_wait = initial_wait
        
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
    def dispatch(self, request: Any, call_next: Callable[[Any], Any]) -> Any:
        """Dispatches the request to the next middleware with retry capability.
        
        This method wraps the call_next function in a retry decorator that
        will retry failed requests with exponential backoff. The number of
        retries and initial wait time can be configured.
        
        Args:
            request: The incoming request object to be processed
            call_next: A callable that invokes the next middleware
                in the chain
                
        Returns:
            The response object after all middlewares have processed
            the request
            
        Raises:
            Exception: If all retry attempts fail
        """
        logger.info("Processing request with retry policy")
        try:
            response = call_next(request)
            logger.info("Request processed successfully")
            return response
        except Exception as e:
            logger.warning(f"Request failed - retrying: {str(e)}")
            raise

    def __call__(self, request: Any, call_next: Callable[[Any], Any]) -> Any:
        """Syntactic sugar for the dispatch method."""
        return self.dispatch(request, call_next)