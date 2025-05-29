from fastapi import Request, JSONResponse, StreamingResponse
from typing import Any, Callable, Optional
import logging

from swarmauri_standard.llms.GroqModel import GroqModel
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.conversations.Conversation import Conversation

from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase
from swarmauri_core.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "LlamaGuardMiddleware")
class LlamaGuardMiddleware(MiddlewareBase, ComponentBase):
    """Middleware for inspecting and filtering unsafe content using Groq's
    ``lama-guard-3-8b`` model.

    This middleware integrates the :class:`~swarmauri_standard.llms.GroqModel`
    running the ``lama-guard-3-8b`` model to ensure that both incoming requests
    and outgoing responses are free from unsafe or malicious content. It
    provides a robust layer of security by inspecting both request and response
    payloads.
    
    Attributes:
        type: Literal["LlamaGuardMiddleware"] = "LlamaGuardMiddleware"
        llm: GroqModel -- Instance of GroqModel for content inspection
    """

    type: Literal["LlamaGuardMiddleware"] = "LlamaGuardMiddleware"

    def __init__(self, llm: Optional[GroqModel] = None, api_key: Optional[str] = None) -> None:
        """Initialize the LlamaGuardMiddleware with a GroqModel instance."""
        super().__init__()
        self.llm = llm or GroqModel(
            api_key=api_key,
            allowed_models=["lama-guard-3-8b"],
            name="lama-guard-3-8b",
        )
        self.logger = logger

    def _is_safe(self, content: bytes) -> bool:
        """Run the content through the Groq ``lama-guard-3-8b`` model.

        Parameters
        ----------
        content : bytes
            Raw content to check for safety.

        Returns
        -------
        bool
            ``True`` if the content is considered safe, ``False`` otherwise.
        """
        text = content.decode("utf-8", errors="ignore")
        conversation = Conversation()
        conversation.add_message(HumanMessage(content=text))
        try:
            self.llm.predict(conversation=conversation)
            result = conversation.get_last().content
            if not isinstance(result, str):
                result = str(result)
            return "unsafe" not in result.lower()
        except Exception as exc:  # pragma: no cover - network errors
            self.logger.error(f"GroqModel error: {exc}")
            return False
    
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
            if not self._is_safe(request_body):
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
                if not self._is_safe(response_body):
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Unsafe content detected in response"}
                    )
            
            # For streaming responses, inspect content as it becomes available
            if isinstance(response, StreamingResponse):
                async for chunk in response.body_iterator:
                    if not self._is_safe(chunk):
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