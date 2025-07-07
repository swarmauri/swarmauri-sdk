from enum import Enum, auto
from collections import defaultdict
from functools import wraps
from inspect import signature
from typing import Any, Callable, Dict, Protocol, Type, NamedTuple, get_origin, get_args, Literal
from typing import Any, Optional        # already imported in the file
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, create_model, ConfigDict
from sqlalchemy import exc as sa_exc
from sqlalchemy.orm import Session
from collections import OrderedDict
import uuid
# ───────────────────── JSON-RPC envelopes ────────────────────────────
_HTTP_TO_RPC: dict[int, int] = {
    400: -32602,   # Invalid params
    404: -32601,   # Method / object not found
    409: -32099,   # Application-specific – duplicate key
    422: -32098,   # Application-specific – constraint violation
    500: -32000,   # Server error
}

def _http_exc_to_rpc(exc: HTTPException) -> tuple[int, dict]:
    """
    Convert FastAPI HTTPException -> (jsonrpc_code, data_obj)
    `data` is optional per spec; we include the HTTP status for clients
    that want the original information.
    """
    code = _HTTP_TO_RPC.get(exc.status_code, -32000)
    data = {"http_status": exc.status_code}
    return code, data

class _RPCReq(BaseModel):
    jsonrpc: str = Field(default="2.0", Literal=True)
    method: str
    params: dict = {}
    id: str | int | None = str(uuid.uuid4())

class _RPCRes(BaseModel):
    jsonrpc: str = Field(default="2.0", Literal=True)
    result: Any | None = None
    error: dict | None = None
    id: str | int | None = None

_ok  = lambda x,q: _RPCRes(result=x, id=q.id)
def _err(code: int, msg: str, q: _RPCReq, data: dict | None = None) -> _RPCRes:
    return _RPCRes(error={"code": code, "message": msg, "data": data}, id=q.id)
