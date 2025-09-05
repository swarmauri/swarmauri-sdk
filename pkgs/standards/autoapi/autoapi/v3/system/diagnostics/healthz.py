from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from .compat import Depends, JSONResponse, Request
from .utils import maybe_execute

logger = logging.getLogger(__name__)


def build_healthz_endpoint(dep: Optional[Callable[..., Any]]):
    """
    Returns a FastAPI endpoint function for /healthz.
    If `dep` is provided, it's used as a dependency to supply `db`.
    Otherwise, we try request.state.db.
    """
    if dep is not None:

        async def _healthz(db: Any = Depends(dep)):
            try:
                await maybe_execute(db, "SELECT 1")
                return {"ok": True}
            except Exception as e:  # pragma: no cover
                logger.exception("/healthz failed")
                return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

        return _healthz

    async def _healthz(request: Request):
        db = getattr(request.state, "db", None)
        if db is None:
            return {"ok": True, "warning": "no-db"}
        try:
            await maybe_execute(db, "SELECT 1")
            return {"ok": True}
        except Exception as e:  # pragma: no cover
            logger.exception("/healthz failed")
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    return _healthz
