from __future__ import annotations

from fastapi import HTTPException

from ..jsonrpc_models import HTTP_ERROR_MESSAGES, _HTTP_TO_RPC


def create_standardized_error(exc: BaseException) -> HTTPException:
    """Normalize *exc* into an HTTPException with RPC metadata."""
    if isinstance(exc, HTTPException):
        return exc
    status = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", str(exc))
    http_exc = HTTPException(status_code=status, detail=detail)
    rpc_code = _HTTP_TO_RPC.get(status, -32603)
    setattr(http_exc, "rpc_code", rpc_code)
    setattr(http_exc, "rpc_message", HTTP_ERROR_MESSAGES.get(status, detail))
    setattr(http_exc, "rpc_data", getattr(exc, "data", None))
    return http_exc
