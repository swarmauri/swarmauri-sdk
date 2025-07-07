# autoapi_gateway.py
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session
from typing import Any, Dict

from .hooks           import Phase
from .jsonrpc_models  import _RPCReq, _RPCRes, _ok, _err   # tiny utility file


def build_gateway(api) -> APIRouter:
    """
    Return a router exposing a single /rpc endpoint that
    drives JSON-RPC through AutoAPI.
    """
    r = APIRouter()

    @r.post("/rpc", response_model=_RPCRes, tags=['rpc'])
    async def _gateway(                                   # ← signature updated
        req: Request,
        env: _RPCReq = Body(..., embed=False),            # ① JSON-RPC envelope
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
            await api._run(Phase.ON_ERROR, ctx | {"error": exc})
            code = exc.status_code if isinstance(exc, HTTPException) else -32000
            return _err(code, str(exc), env)

        finally:
            db.close()

    return r
