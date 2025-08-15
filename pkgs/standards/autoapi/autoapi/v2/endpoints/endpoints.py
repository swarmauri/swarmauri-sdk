from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .naming import label_hook_callable
from ..hooks import Phase


def attach_health_and_methodz(api, get_async_db=None, get_db=None):
    """Add diagnostic endpoints to *api.router*.

    Adds ``/healthz``, ``/methodz`` and ``/hookz`` to the router. ``api`` is
    the :class:`~autoapi.v2.AutoAPI` instance and provides access to the method
    list and hook registry.
    """
    r = APIRouter()

    @r.get("/methodz", tags=["system"], name="Methods")
    def _methodz() -> list[str]:
        """Ordered, canonical operation list."""
        return list(api._method_ids.keys())

    @r.get("/hookz", tags=["system"], name="Hooks")
    def _hookz() -> dict[str, dict[str, list[str]]]:
        """
        Expose hook execution order for each method.

        - Phases appear in runner order; error phases trail.
        - Within each phase, hooks are listed in execution order:
          global (None) hooks, then method-specific hooks.
        """

        def label(fn) -> str:
            n = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
            m = getattr(fn, "__module__", None)
            return f"{m}.{n}" if m else n

        # Methods = declared RPC methods ∪ any method that has at least one hook
        methods = set(api._method_ids.keys())
        for hooks_by_method in api._hook_registry.values():
            methods.update(m for m in hooks_by_method.keys() if m is not None)

        # Execution-ordered phases (commit itself is not a hook phase)
        normal_phases = [
            getattr(Phase, "PRE_TX_BEGIN", None),
            getattr(Phase, "PRE_HANDLER", None),
            getattr(Phase, "POST_HANDLER", None),
            getattr(Phase, "PRE_COMMIT", None),
            getattr(Phase, "POST_COMMIT", None),
            getattr(Phase, "POST_RESPONSE", None),
        ]
        error_phases = [
            getattr(Phase, "ON_ROLLBACK", None),  # fired before specific ON_*_ERROR
            getattr(Phase, "ON_PRE_HANDLER_ERROR", None),
            getattr(Phase, "ON_HANDLER_ERROR", None),
            getattr(Phase, "ON_POST_HANDLER_ERROR", None),
            getattr(Phase, "ON_PRE_COMMIT_ERROR", None),
            getattr(Phase, "ON_COMMIT_ERROR", None),
            getattr(Phase, "ON_POST_COMMIT_ERROR", None),
            getattr(Phase, "ON_POST_RESPONSE_ERROR", None),
            getattr(Phase, "ON_ERROR", None),  # generic catch-all
        ]
        phase_order = [p for p in normal_phases + error_phases if p is not None]

        registry: dict[str, dict[str, list[str]]] = {}

        for method in sorted(methods):
            phase_map: dict[str, list[str]] = {}
            for phase in phase_order:
                hooks_by_method = api._hook_registry.get(phase, {})
                global_hooks = hooks_by_method.get(None, [])
                specific_hooks = hooks_by_method.get(method, [])
                if global_hooks or specific_hooks:
                    # Execution order: global → specific
                    phase_map[phase.name] = [
                        label_hook_callable(fn)
                        for fn in (global_hooks + specific_hooks)
                    ]
            if phase_map:
                registry[method] = phase_map

        return registry

    # Choose the appropriate health endpoint based on available DB provider
    if get_db:

        @r.get("/healthz", tags=["system"], name="Health")
        def _sync_healthz(db: Session = Depends(get_db)):
            try:
                res = db.execute(text("select 1"))
                if res.fetchall()[0][0]:
                    return {"ok": True}
                else:
                    return {"ok": False}
            finally:
                db.close()
    elif get_async_db:

        @r.get("/healthz", tags=["system"], name="Health")
        async def _async_healthz(db: AsyncSession = Depends(get_async_db)):
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
