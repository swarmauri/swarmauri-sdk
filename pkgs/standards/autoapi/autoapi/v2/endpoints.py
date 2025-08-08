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
    def _hookz() -> dict[str, dict[str | None, list[str]]]:
        """Expose the current hook registry."""
        registry: dict[str, dict[str | None, list[str]]] = {}
        for phase, hooks in api._hook_registry.items():
            registry[phase.name] = {
                (k if k is not None else "*"): [
                    getattr(f, "__name__", repr(f)) for f in v
                ]
                for k, v in hooks.items()
            }
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
