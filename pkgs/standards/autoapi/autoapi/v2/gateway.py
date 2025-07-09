# autoapi_gateway.py
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Any, Dict

from .hooks import Phase
from .jsonrpc_models import _RPCReq, _RPCRes, _err, _ok, _http_exc_to_rpc


def build_gateway(api) -> APIRouter:
    """
    Return a router exposing a single /rpc endpoint that
    drives JSON-RPC through AutoAPI.
    """
    r = APIRouter()

    if api.get_db:

        @r.post("/rpc", response_model=_RPCRes, tags=["rpc"])
        async def _gateway(
            req: Request,
            env: _RPCReq = Body(..., embed=False),
            db: Session = Depends(api.get_db),
        ):
            ctx: Dict[str, Any] = {"request": req, "db": db, "env": env}

            if api.authorize and not api.authorize(env.method, req):
                return _err(403, "Forbidden", env)

            fn = api.rpc.get(env.method)
            if not fn:
                return _err(-32601, "Method not found", env)

            try:
                await api._run(Phase.PRE_TX_BEGIN, ctx)
                res = fn(env.params, db)
                ctx["result"] = res
                await api._run(Phase.POST_HANDLER, ctx)

                if db.in_transaction():
                    await api._run(Phase.PRE_COMMIT, ctx)
                    db.commit()
                    await api._run(Phase.POST_COMMIT, ctx)

                out = _ok(res, env)
                await api._run(Phase.POST_RESPONSE, ctx | {"response": out})
                return out

            except Exception as exc:
                db.rollback()

                if isinstance(exc, HTTPException):
                    rpc_code, rpc_data = _http_exc_to_rpc(exc)
                    return _err(rpc_code, exc.detail, env, rpc_data)

                await api._run(Phase.ON_ERROR, ctx | {"error": exc})
                return _err(-32000, str(exc), env)

            finally:
                db.close()

    else:

        @r.post("/rpc", response_model=_RPCRes, tags=["rpc"])
        async def _gateway(
            req: Request,
            env: _RPCReq = Body(..., embed=False),
            db: AsyncSession = Depends(api.get_async_db),
        ):
            ctx: Dict[str, Any] = {"request": req, "db": db, "env": env}

            if api.authorize and not api.authorize(env.method, req):
                return _err(403, "Forbidden", env)

            fn = api.rpc.get(env.method)
            if not fn:
                return _err(-32601, "Method not found", env)

            try:
                await api._run(Phase.PRE_TX_BEGIN, ctx)
                res = await db.run_sync(lambda s: fn(env.params, s))
                ctx["result"] = res
                await api._run(Phase.POST_HANDLER, ctx)

                if db.in_transaction():
                    await api._run(Phase.PRE_COMMIT, ctx)
                    await db.commit()
                    await api._run(Phase.POST_COMMIT, ctx)

                out = _ok(res, env)
                await api._run(Phase.POST_RESPONSE, ctx | {"response": out})
                return out

            except Exception as exc:
                await db.rollback()

                if isinstance(exc, HTTPException):
                    rpc_code, rpc_data = _http_exc_to_rpc(exc)
                    return _err(rpc_code, exc.detail, env, rpc_data)

                await api._run(Phase.ON_ERROR, ctx | {"error": exc})
                return _err(-32000, str(exc), env)

            finally:
                await db.close()

    return r
