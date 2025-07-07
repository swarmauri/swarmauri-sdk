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
_err = lambda c,m,q: _RPCRes(error={"code": c, "message": m}, id=q.id)
