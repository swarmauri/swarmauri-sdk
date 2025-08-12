"""
autoapi.v2.rpcdispatch  – JSON-RPC façade for AutoAPI
-----------------------------------------------------
Exposes a single /rpc endpoint that validates a JSON-RPC-2.0 envelope
and forwards execution to the unified hook-aware runner.
"""

from __future__ import annotations

from typing import Annotated, Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .types import APIRouter, Body, Depends, HTTPException, Request
from .impl._runner import _invoke  # ← central lifecycle engine
from .jsonrpc_models import (
    _RPCReq,
    _RPCRes,
    _err,
    _ok,
    _http_exc_to_rpc,
    HTTP_ERROR_MESSAGES,
)
from pydantic import ValidationError


def build_rpcdispatch(api) -> APIRouter:
    """
    Return a router exposing a single `/rpc` endpoint that drives JSON-RPC
    through AutoAPI. Works for both sync and async SQLAlchemy sessions.
    """
    r = APIRouter()

    # Choose one concrete dependency type (no Optional, no unions)
    DBDep = (
        Annotated[AsyncSession, Depends(api.get_async_db)]
        if getattr(api, "get_async_db", None)
        else Annotated[Session, Depends(api.get_db)]
    )

    @r.post("/rpc", response_model=_RPCRes, tags=["rpc"])
    async def _rpcdispatch(
        req: Request,
        env: _RPCReq = Body(..., embed=False),
        db: DBDep = None,  # type: ignore[assignment]  (FastAPI injects via Depends)
        principal: Dict | None = api._optional_authn_dep,
    ):
        # Seed ctx bridge for downstream
        if getattr(req.state, "ctx", None) is None:
            req.state.ctx = {}

        req.state.principal = principal
        ctx: Dict[str, Any] = {"request": req, "db": db, "env": env}
        ext = getattr(req.state, "ctx", None)
        if isinstance(ext, dict):
            ctx.update(ext)

        # AuthN: optional at transport, required per method unless allow_anon
        if api._authn and env.method not in api._allow_anon and principal is None:
            return _err(-32001, HTTP_ERROR_MESSAGES[401], env)

        # AuthZ
        if api._authorize and not api._authorize(env.method, req):
            return _err(403, "Forbidden", env)

        try:
            # If AsyncSession, run sync cores in the async engine's run_sync
            result = await _invoke(api, env.method, params=env.params, ctx=ctx)

            return _ok(result, env)

        except HTTPException as exc:
            rpc_code, rpc_message, data = _http_exc_to_rpc(exc)
            return _err(rpc_code, rpc_message, env, data=data)

        except ValidationError as exc:
            errors = exc.errors()
            missing = [e["loc"][-1] for e in errors if e["type"] == "missing"]
            msg = "Validation error"
            if missing:
                msg += ": missing parameter(s): " + ", ".join(missing)
            return _err(-32602, msg, env, data=errors)

        except Exception as exc:
            # _invoke() already handled rollback and ON_ERROR hook
            return _err(-32000, str(exc), env)

    return r
