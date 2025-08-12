# autoapi/v2/rpcdispatch.py
from __future__ import annotations
from typing import Annotated, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from .types import APIRouter, Body, Depends, HTTPException, Request, ValidationError
from .impl._runner import _invoke
from .jsonrpc_models import _RPCReq, _RPCRes, _err, _ok, _http_exc_to_rpc, HTTP_ERROR_MESSAGES


def build_rpcdispatch(api) -> APIRouter:
    r = APIRouter()

    DBDep = (
        Annotated[AsyncSession, Depends(api.get_async_db)]
        if getattr(api, "get_async_db", None)
        else Annotated[Session, Depends(api.get_db)]
    )

    @r.post("/rpc", response_model=_RPCRes, tags=["rpc"])
    async def _rpcdispatch(
        req: Request,
        env: _RPCReq = Body(..., embed=False),
        db: DBDep = None,  # injected via Depends; value is Session or AsyncSession
        principal: Dict | None = api._optional_authn_dep,
    ):
        if getattr(req.state, "ctx", None) is None:
            req.state.ctx = {}
        req.state.principal = principal

        # Transport-optional, method-required auth
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
            rpc_code, rpc_message, data = _http_exc_to_rpc(exc)
            return _err(rpc_code, rpc_message, env, data=data)
        except ValidationError as exc:
            errors = exc.errors()
            missing = [e["loc"][-1] for e in errors if e["type"] == "missing"]
            msg = "Validation error" + (": missing parameter(s): " + ", ".join(missing) if missing else "")
            return _err(-32602, msg, env, data=errors)
        except Exception as exc:
            return _err(-32000, str(exc), env)

    return r
