from logging import getLogger
from typing import Any, Callable, Literal, Optional

from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.llms.GroqModel import GroqModel
from swarmauri_standard.messages.HumanMessage import HumanMessage

logger = getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "LlamaGuardMiddleware")
class LlamaGuardMiddleware(MiddlewareBase, ComponentBase):
    """Middleware for inspecting and filtering unsafe content using Groq's
    ``llama-guard-3-8b`` model.

    This middleware integrates the :class:`~swarmauri_standard.llms.GroqModel`
    running the ``llama-guard-3-8b`` model to ensure that both incoming requests
    and outgoing responses are free from unsafe or malicious content. It
    provides a robust layer of security by inspecting both request and response
    payloads.

    Attributes:
        type: Literal["LlamaGuardMiddleware"] = "LlamaGuardMiddleware"
        llm: Optional[GroqModel] -- Instance of GroqModel for content inspection
    """

    type: Literal["LlamaGuardMiddleware"] = "LlamaGuardMiddleware"
    llm: Optional[GroqModel] = None

    def __init__(
        self,
        llm: Optional[GroqModel] = None,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the LlamaGuardMiddleware with a GroqModel instance."""
        super().__init__(**kwargs)

        if llm is not None:
            self.llm = llm
        elif api_key is not None:
            self.llm = GroqModel(
                api_key=api_key,
                allowed_models=["llama-guard-3-8b"],  # Fix: correct model name
                name="llama-guard-3-8b",
            )
        else:
            self.llm = None
            logger.warning(
                "LlamaGuardMiddleware initialized without LLM - safety checks disabled"
            )

        self.logger = logger

    def _is_safe(self, content: bytes) -> bool:
        """Run the content through the Groq ``llama-guard-3-8b`` model."""
        if self.llm is None:
            logger.warning("No LLM configured - defaulting to safe content")
            return True
    
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

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Dispatches the request to the next middleware in the chain after inspection."""
        if request.method in ["POST", "PUT", "PATCH"]:
            request_body = await request.body()
            if not self._is_safe(request_body):
                return JSONResponse(
                    status_code=400,
                    content={"error": "Unsafe content detected in request"},
                )

        try:
            # Proceed with the request chain
            response = await call_next(request)

            # Inspect response content
            if isinstance(response, JSONResponse):
                # Fix: Handle response body properly
                if hasattr(response, "body") and response.body:
                    response_body = response.body
                else:
                    # For JSONResponse, we need to serialize the content to get bytes
                    import json

                    response_body = (
                        json.dumps(response.content).encode()
                        if response.content
                        else b""
                    )

                if response_body and not self._is_safe(response_body):
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Unsafe content detected in response"},
                    )

            # For streaming responses, inspect content as it becomes available
            if isinstance(response, StreamingResponse):
                try:
                    chunks = []
                    async for chunk in response.body_iterator:
                        chunks.append(chunk)
                        if not self._is_safe(chunk):
                            return JSONResponse(
                                status_code=400,
                                content={"error": "Unsafe streaming content detected"},
                            )

                    # Recreate the response with the collected chunks
                    async def new_body_iterator():
                        for chunk in chunks:
                            yield chunk

                    response.body_iterator = new_body_iterator()
                except Exception:
                    # If we can't iterate the stream, skip inspection
                    pass

            return response

        except Exception as e:
            self.logger.error(f"Error in LlamaGuardMiddleware: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error during content inspection"},
