"""
autoapi.v2.endpoints.rpcdispatcher – JSON-RPC façade for AutoAPI
"""

from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..types import APIRouter, Body, Depends, HTTPException, Request, ValidationError
from ..impl._runner import _invoke
from ..jsonrpc_models import (
    _RPCReq,
    _RPCRes,
    _err,
    _ok,
    _http_exc_to_rpc,
    HTTP_ERROR_MESSAGES,
)


def build_rpcdispatch(api) -> APIRouter:
    r = APIRouter()

    if callable(getattr(api, "get_async_db", None)):
        # Async engine: inject AsyncSession directly (no alias, no forward-ref)
        @r.post("/rpc", response_model=_RPCRes, tags=["system"], name="RPC Dispatcher")
        async def _rpcdispatch(
            req: Request,
            db: AsyncSession = Depends(api.get_async_db),
            env: _RPCReq = Body(..., embed=False),
            principal: Dict | None = api._optional_authn_dep,
        ):
            if getattr(req.state, "ctx", None) is None:
                req.state.ctx = {}
            req.state.principal = principal

            if api._authn and env.method not in api._allow_anon and principal is None:
                return _err(-32001, HTTP_ERROR_MESSAGES[401], env)
            if api._authorize and not api._authorize(env.method, req):
                return _err(403, "Forbidden", env)

            ctx: Dict[str, Any] = {"request": req, "db": db, "env": env}
            ext = getattr(req.state, "ctx", None)
            if isinstance(ext, dict):
                ctx.update(ext)

            try:
                result = await _invoke(api, env.method, params=env.params, ctx=ctx)
                return _ok(result, env)
            except HTTPException as exc:
                code, msg, data = _http_exc_to_rpc(exc)
                return _err(code, msg, env, data=data)
            except ValidationError as exc:
                errors = exc.errors()
                missing = [e["loc"][-1] for e in errors if e["type"] == "missing"]
                msg = "Validation error" + (
                    ": missing parameter(s): " + ", ".join(missing) if missing else ""
                )
                return _err(-32602, msg, env, data=errors)
            except Exception as exc:
                return _err(-32000, str(exc), env)

    else:
        # Sync engine: inject Session directly (no alias, no forward-ref)
        @r.post("/rpc", response_model=_RPCRes, tags=["system"], name="RPC Dispatcher")
        async def _rpcdispatch(
            req: Request,
            db: Session = Depends(api.get_db),
            env: _RPCReq = Body(..., embed=False),
            principal: Dict | None = api._optional_authn_dep,
        ):
            if getattr(req.state, "ctx", None) is None:
                req.state.ctx = {}
            req.state.principal = principal

            if api._authn and env.method not in api._allow_anon and principal is None:
                return _err(-32001, HTTP_ERROR_MESSAGES[401], env)
            if api._authorize and not api._authorize(env.method, req):
                return _err(403, "Forbidden", env)

            ctx: Dict[str, Any] = {"request": req, "db": db, "env": env}
            ext = getattr(req.state, "ctx", None)
            if isinstance(ext, dict):
                ctx.update(ext)

            try:
                result = await _invoke(api, env.method, params=env.params, ctx=ctx)
                return _ok(result, env)
            except HTTPException as exc:
                code, msg, data = _http_exc_to_rpc(exc)
                return _err(code, msg, env, data=data)
            except ValidationError as exc:
                errors = exc.errors()
                missing = [e["loc"][-1] for e in errors if e["type"] == "missing"]
                msg = "Validation error" + (
                    ": missing parameter(s): " + ", ".join(missing) if missing else ""
                )
                return _err(-32602, msg, env, data=errors)
            except Exception as exc:
                return _err(-32000, str(exc), env)

    return r
