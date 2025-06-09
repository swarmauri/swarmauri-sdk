import json
import logging
from typing import Any, Callable

from fastapi import Request, Response
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "JsonRpcMiddleware")
class JsonRpcMiddleware(MiddlewareBase):
    """Basic validation middleware for JSON-RPC requests."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Validate JSON-RPC requests before calling the next middleware."""
        if request.headers.get("content-type", "").startswith("application/json"):
            body = await request.body()
            try:
                data = json.loads(body or b"{}")
            except json.JSONDecodeError:
                logger.error("Invalid JSON in request body")
                return Response(status_code=400, content="Invalid JSON")
            if isinstance(data, dict) and "jsonrpc" not in data:
                logger.error("Missing jsonrpc field")
                return Response(status_code=400, content="Missing jsonrpc field")
        return await call_next(request)
