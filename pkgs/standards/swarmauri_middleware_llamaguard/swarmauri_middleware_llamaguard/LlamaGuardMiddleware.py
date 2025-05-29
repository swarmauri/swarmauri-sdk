from fastapi import Request, JSONResponse
from llmaguard import LlamaGuard
from typing import Any, Callable, Optional
import logging

from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase
from swarmauri_core.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "LlamaGuardMiddleware")
class LlamaGuardMiddleware(MiddlewareBase, ComponentBase):
    """Middleware for inspecting and filtering unsafe content using LlamaGuard.
    
    This middleware integrates LlamaGuard to ensure that both incoming requests
    and outgoing responses are free from unsafe or malicious content. It provides
    a robust layer of security by inspecting both request and response payloads.
    
    Attributes:
        type: Literal["LlamaGuardMiddleware"] = "LlamaGuardMiddleware"
        llmaguard: LlamaGuard = Instance of LlamaGuard for content inspection
    """
    
    type: Literal["LlamaGuardMiddleware"] = "LlamaGuardMiddleware"
    
    def __init__(self) -> None:
        """Initialize the LlamaGuardMiddleware with LlamaGuard instance."""
        super().__init__()
        self.llmaguard = LlamaGuard()
        self.logger = logger
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        """Dispatches the request to the next middleware in the chain after inspection.
        
        This method performs the following steps:
        1. Inspects the incoming request content for safety
        2. Calls the next middleware in the chain
        3. Inspects the outgoing response content for safety
        4. Returns the final response
        
        Args:
            request: The incoming request object to be processed
            call_next: A callable that invokes the next middleware in the chain
            
        Returns:
            The response object after all middlewares have processed the request
            
        Raises:
            ValueError: If the request or response content is deemed unsafe
        """
        
        # Inspect request content
        if request.method in ["POST", "PUT", "PATCH"]:
            request_body = await request.body()
            if not self.llmaguard.inspect(request_body):
                return JSONResponse(
                    status_code=400,
                    content={"error": "Unsafe content detected in request"}
                )
        
        try:
            # Proceed with the request chain
            response = await call_next(request)
            
            # Inspect response content
            if isinstance(response, JSONResponse):
                response_body = response.body
                if not self.llmaguard.inspect(response_body):
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Unsafe content detected in response"}
                    )
            
            # For streaming responses, inspect content as it becomes available
            if isinstance(response, StreamingResponse):
                async for chunk in response.body_iterator:
                    if not self.llmaguard.inspect(chunk):
                        return JSONResponse(
                            status_code=400,
                            content={"error": "Unsafe streaming content detected"}
                        )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in LlamaGuardMiddleware: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error during content inspection"}
            )