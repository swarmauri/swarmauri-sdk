import gzip
import io
import logging
from typing import Any, Callable

from fastapi import Request, Response
from swarmauri_base.ComponentBase import ComponentBase  # Add this import
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

_logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "GzipCompressionMiddleware")
class GzipCompressionMiddleware(MiddlewareBase):
    """Middleware that provides gzip compression for outgoing responses."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Dispatches the request to the next middleware in the chain."""

        # Process the request by calling the next middleware in the chain
        response = await call_next(request)

        # Check if the response is a Response object
        if not isinstance(response, Response):
            return response

        # Check if the response content is not already compressed
        if "gzip" in str(response.headers.get("Content-Encoding", "")):
            _logger.debug("Response is already gzipped, skipping compression")
            return response

        # Check if the client supports gzip encoding
        if "gzip" not in request.headers.get("Accept-Encoding", "").lower():
            _logger.debug("Client does not support gzip encoding, skipping compression")
            return response

        # Check if the response content type is compressible
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type and "text/" not in content_type:
            _logger.debug(
                f"Content type {content_type} is not compressible, skipping compression"
            )
            return response

        # Get the response body
        response_body = response.body

        # Compress the response body using gzip
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode="w") as gzip_file:
            if response_body:
                if isinstance(response_body, str):
                    gzip_file.write(response_body.encode("utf-8"))
                else:
                    gzip_file.write(response_body)

        compressed_body = buffer.getvalue()

        # Create a new response with the compressed body
        new_response = Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

        # Add or update the Content-Encoding header
        new_response.headers["Content-Encoding"] = "gzip"

        # Update the Content-Length header
        new_response.headers["Content-Length"] = str(len(compressed_body))

        _logger.debug("Successfully compressed response using gzip")
        return new_response
