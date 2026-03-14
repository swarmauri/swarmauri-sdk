from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from tigrbl_concrete._concrete import Request
from tigrbl_concrete._concrete.dependencies import Depends
from tigrbl_concrete._concrete import JSONResponse
from .utils import maybe_execute

logger = logging.getLogger(__name__)


def _resolve_db(candidate: Any) -> Any:
    """Resolve a DB-like object from either a DB handle or a Request object."""
    if hasattr(candidate, "execute"):
        return candidate

    state = getattr(candidate, "state", None)
    db = getattr(state, "db", None)
    if db is not None:
        return db
    return None


def build_healthz_endpoint(dep: Optional[Callable[..., Any]]):
    """
    Returns a ASGI endpoint function for /healthz.
    If `dep` is provided, it's used as a dependency to supply `db`.
    Otherwise, we try request.state.db.
    """
    if dep is not None:

        async def _healthz(db: Any = Depends(dep)):
            db = _resolve_db(db)
            if db is None:
                return {"ok": True, "warning": "no-db"}
            try:
                await maybe_execute(db, "SELECT 1")
                return {"ok": True}
            except Exception as e:  # pragma: no cover
                logger.warning("/healthz degraded: %s", e)
                return JSONResponse(
                    {"ok": False, "warning": "db-unavailable", "error": str(e)},
                    status_code=200,
                )

        return _healthz

    async def _healthz(request: Request):
        db = _resolve_db(request)
        if db is None:
            return {"ok": True, "warning": "no-db"}
        try:
            await maybe_execute(db, "SELECT 1")
            return {"ok": True}
        except Exception as e:  # pragma: no cover
            logger.warning("/healthz degraded: %s", e)
            return JSONResponse(
                {"ok": False, "warning": "db-unavailable", "error": str(e)},
                status_code=200,
            )

    return _healthz
