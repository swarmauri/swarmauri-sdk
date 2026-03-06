
from __future__ import annotations
from .exceptions import HTTPException, StatusDetailError
from .mappings import status, ERROR_MESSAGES

def create_standardized_error(exc):
    if isinstance(exc, StatusDetailError):
        return exc
    status_code = int(getattr(exc, 'status_code', 500) or 500)
    detail = getattr(exc, 'detail', None)
    if detail in (None, ''):
        detail = str(exc) or 'Internal Server Error'
    headers = getattr(exc, 'headers', {}) or {}
    return StatusDetailError(status_code=status_code, detail=detail, headers=headers)

def to_rpc_error_payload(exc):
    err = create_standardized_error(exc)
    return {'code': -32603 if err.status_code >= 500 else -32602, 'message': str(err.detail), 'data': {'http_status': err.status_code}}

__all__ = ['HTTPException','StatusDetailError','status','ERROR_MESSAGES','create_standardized_error','to_rpc_error_payload']
