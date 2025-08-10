"""
autoapi.v2.gateway  – JSON-RPC façade for AutoAPI
-------------------------------------------------
Exposes a single /rpc endpoint that validates a JSON-RPC-2.0 envelope
and forwards execution to the unified hook-aware runner.

This module is *thin* by design:  it performs only
  • envelope parsing / authorisation
  • DB-session acquisition
  • error translation (HTTP → JSON-RPC)

Everything else (hooks, commit/rollback, result packing)
lives in autoapi.v2._runner._invoke.
"""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Any, Dict

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


# ────────────────────────────────────────────────────────────────────────────
def build_gateway(api) -> APIRouter:
    """
    Return a router exposing a single `/rpc` endpoint that drives JSON-RPC
    through AutoAPI.  Works for both sync and async SQLAlchemy sessions.
    """
    r = APIRouter()


    # ───────── synchronous SQLAlchemy branch ───────────────────────────────
    if api.get_db:

        @r.post(
            "/rpc",
            response_model=_RPCRes,
            tags=["rpc"],
        )
        async def _gateway(
            req: Request,
            env: _RPCReq = Body(..., embed=False),
            db: Session = Depends(api.get_db),
            principal: Dict | None = api._authn_dep,
        ):
            req.state.principal = principal
            print("GW principal:", principal)
            print("GW allow_anon:", api._allow_anon)
            print("GW method called:", env.method)
            ctx: Dict[str, Any] = {"request": req, "db": db, "env": env}
            if api._authn and env.method not in api._allow_anon and principal is None:
                return _err(-32001, HTTP_ERROR_MESSAGES[401], env)

            # Authorisation --------------------------------------------------
            if api.authorize and not api.authorize(env.method, req):
                return _err(403, "Forbidden", env)

            try:
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
                # _invoke() has already rolled back & fired ON_ERROR hook.
                return _err(-32000, str(exc), env)

            finally:
                db.close()

    # ───────── asynchronous SQLAlchemy branch ──────────────────────────────
    else:

        @r.post("/rpc", response_model=_RPCRes, tags=["rpc"])
        async def _gateway(
            req: Request,
            env: _RPCReq = Body(..., embed=False),
            db: AsyncSession = Depends(api.get_async_db),
            principal: Dict | None = api._authn_dep,
        ):
            req.state.principal = principal
            print("GW principal:", principal)
            print("GW allow_anon:", api._allow_anon)
            print("GW method called:", env.method)      
            ctx: Dict[str, Any] = {"request": req, "db": db, "env": env}
            if api._authn and env.method not in api._allow_anon and principal is None:
                return _err(-32001, HTTP_ERROR_MESSAGES[401], env)

            if api.authorize and not api.authorize(env.method, req):
                return _err(403, "Forbidden", env)

            try:
                # The core CRUD functions are synchronous; run them in the
                # async engine’s thread-pool via run_sync().
                result = await _invoke(
                    api,
                    env.method,
                    params=env.params,
                    ctx=ctx,
                    exec_fn=lambda m, p, s=db: s.run_sync(  # override executor
                        lambda sync_sess: api.rpc[m](p, sync_sess)
                    ),
                )
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
                return _err(-32000, str(exc), env)

            finally:
                await db.close()

    return r
