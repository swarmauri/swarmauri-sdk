from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


def attach_health_and_methodz(api, get_async_db=None, get_db=None):
    """Add diagnostic endpoints to *api.router*.

    Adds ``/healthz``, ``/methodz`` and ``/hookz`` to the router. ``api`` is
    the :class:`~autoapi.v2.AutoAPI` instance and provides access to the method
    list and hook registry.
    """
    r = APIRouter()

    @r.get("/methodz", tags=["rpc"])
    def _methodz() -> list[str]:
        """Ordered, canonical operation list."""
        return list(api._method_ids.keys())

    @r.get("/hookz", tags=["hooks"])
    def _hookz() -> dict[str, dict[str, list[str]]]:
        """Expose hook execution order for each method."""
        registry: dict[str, dict[str, list[str]]] = {}

        methods = set(api._method_ids.keys())
        for hooks in api._hook_registry.values():
            methods.update(m for m in hooks.keys() if m is not None)

        for method in sorted(methods):
            method_hooks: dict[str, list[str]] = {}
            for phase, hooks in api._hook_registry.items():
                global_hooks = hooks.get(None, [])
                specific_hooks = hooks.get(method, [])
                if global_hooks or specific_hooks:
                    method_hooks[phase.name] = [
                        getattr(fn, "__name__", repr(fn))
                        for fn in (global_hooks + specific_hooks)
                    ]
            if method_hooks:
                registry[method] = method_hooks
        return registry

    # Choose the appropriate health endpoint based on available DB provider
    if get_db:

        @r.get("/healthz", tags=["health"])
        def _health(db: Session = Depends(get_db)):
            try:
                res = db.execute(text("select 1"))
                if res.fetchall()[0][0]:
                    return {"ok": True}
                else:
                    return {"ok": False}
            finally:
                db.close()
    elif get_async_db:

        @r.get("/healthz", tags=["health"])
        async def _health(db: AsyncSession = Depends(get_async_db)):
            try:
                result = await db.execute(text("select 1"))
                row = result.fetchone()
                if row and row[0]:
                    return {"ok": True}
                else:
                    return {"ok": False}
            finally:
                await db.close()

    api.router.include_router(r)
