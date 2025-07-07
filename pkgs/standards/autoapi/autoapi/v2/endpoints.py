# autoapi_endpoints.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

def attach_health_and_methodz(api, get_db):
    """
    Adds /healthz and /methodz to *api.router*.
    *api* is the AutoAPI instance (needed for method list).
    """
    r = APIRouter()

    @r.get("/methodz", tags=["rpc"])
    def _methodz() -> list[str]:
        """Ordered, canonical operation list."""
        return list(api._method_ids.keys())

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

    api.router.include_router(r)