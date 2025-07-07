# autoapi_endpoints.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

def attach_health_and_methodz(api, get_db):
    """
    Adds /healthz and /methodz to *api.router*.
    *api* is the AutoAPI instance (needed for method list).
    """
    r = APIRouter()

    @r.get("/methodz", tags="rpc")
    def _methodz() -> list[str]:
        """Ordered, canonical operation list."""
        return list(api._method_ids.keys())

    @r.get("/healthz", "health")
    def _health(db: Session = Depends(get_db)):
        try:
            db.execute("SELECT 1")
            return {"ok": True}
        finally:
            db.close()

    api.router.include_router(r)