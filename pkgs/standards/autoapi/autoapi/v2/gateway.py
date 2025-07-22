# autoapi_gateway.py
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .jsonrpc_models import _RPCReq, _RPCRes, _err, _ok, _http_exc_to_rpc


def _extract_model_and_verb(api, method_name: str) -> tuple[str, str]:
    """Extract model and verb from RPC method name with better table name resolution."""
    if "." in method_name:
        model_class_name, verb = method_name.split(".", 1)
        # Look up the actual table name from the registered tables
        model = None
        for table_name in api._registered_tables:
            # Match by table name or try to match class name
            if (
                table_name.lower() == model_class_name.lower()
                or table_name.lower() == model_class_name.lower() + "s"
                or table_name.lower().rstrip("s") == model_class_name.lower()
            ):
                model = table_name
                break
        # Fallback if no match found
        if not model:
            model = model_class_name.lower()
        return model, verb
    else:
        # Fallback for custom RPC methods
        return "custom", method_name


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
            if api.authorize and not api.authorize(env.method, req):
                return _err(403, "Forbidden", env)

            fn = api.rpc.get(env.method)
            if not fn:
                return _err(-32601, "Method not found", env)

            try:
                # Extract model and verb from method name with proper table name resolution
                model, verb = _extract_model_and_verb(api, env.method)

                # Use the unified invoke method
                result = await api._invoke(
                    model=model,
                    verb=verb,
                    core_fn=lambda: fn(env.params, db),
                    db=db,
                    request=req,
                    env=env,
                )

                return _ok(result, env)

            except Exception as exc:
                if isinstance(exc, HTTPException):
                    rpc_code, rpc_data = _http_exc_to_rpc(exc)
                    return _err(rpc_code, exc.detail, env, rpc_data)
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
            if api.authorize and not api.authorize(env.method, req):
                return _err(403, "Forbidden", env)

            fn = api.rpc.get(env.method)
            if not fn:
                return _err(-32601, "Method not found", env)

            try:
                # Extract model and verb from method name with proper table name resolution
                model, verb = _extract_model_and_verb(api, env.method)

                # Use the unified invoke method with async wrapper
                result = await api._invoke(
                    model=model,
                    verb=verb,
                    core_fn=lambda: db.run_sync(lambda s: fn(env.params, s)),
                    db=db,
                    request=req,
                    env=env,
                )

                return _ok(result, env)

            except Exception as exc:
                if isinstance(exc, HTTPException):
                    rpc_code, rpc_data = _http_exc_to_rpc(exc)
                    return _err(rpc_code, exc.detail, env, rpc_data)
                return _err(-32000, str(exc), env)

            finally:
                await db.close()

    return r
